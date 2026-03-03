#!/usr/bin/env python3
"""
seed-from-plan.py -- Generalized project artifact seeder
==========================================================

Universal version that works for ANY EVA project (51-ACA, 33-eva-brain-v2, etc).

Reads README.md, PLAN.md, STATUS.md, ACCEPTANCE.md and rebuilds:
  1. .eva/veritas-plan.json  -- complete story roster for Veritas MTI
  2. Data model HTTP API     -- seed/reseed stories via 37-data-model endpoint

Project Prefix (ID) Detection:
  1. --project-id argument:    python seed-from-plan.py --project-id "31-eva-faces"
  2. PROJECT_ID env var:       export PROJECT_ID="31-eva-faces"; python seed-from-plan.py
  3. Folder name inference:    C:\AICOE\eva-foundry\51-ACA -> PROJECT_PREFIX="ACA"
  4. PLAN.md scan:             Look for "EPIC NN -- ..." to infer prefix

Usage:
  python seed-from-plan.py                           # rebuild veritas-plan.json only
  python seed-from-plan.py --reseed-model            # rebuild + seed HTTP data model
  python seed-from-plan.py --project-id "TEST"       # specify project prefix explicitly
  python seed-from-plan.py --wipe-only               # wipe model only (no plan parse)
  python seed-from-plan.py --dry-run                 # print what would be written

Design principle:
  Parse PLAN.md as the single source of truth.
  Every Epic, Feature, and Story gets a canonical PROJECT-EE-NNN ID.
  veritas-plan.json is rebuilt from scratch every run.
  Data model seed endpoint receives parsed stories via HTTP.

Encoding: ASCII-only output (no emoji, no Unicode >U+007F)
"""

import re
import json
import sys
import os
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Detect repository root (parent of .github, .eva, PLAN.md)
REPO_ROOT = Path(__file__).parent.parent
PLAN_FILE = REPO_ROOT / "PLAN.md"
STATUS_FILE = REPO_ROOT / "STATUS.md"
README_FILE = REPO_ROOT / "README.md"
ACCEPT_FILE = REPO_ROOT / "ACCEPTANCE.md"
EVA_DIR = REPO_ROOT / ".eva"
PLAN_OUT = EVA_DIR / "veritas-plan.json"

# Data model API endpoint
DATA_MODEL_URL = os.environ.get(
    "DATA_MODEL_URL",
    "https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io"
)


def detect_project_id(explicit_id: Optional[str] = None) -> str:
    """
    Auto-detect PROJECT_ID (e.g., 'ACA', 'TEST') in order of precedence:
      1. Explicit --project-id argument
      2. PROJECT_ID environment variable
      3. Infer from folder name (e.g., /51-ACA -> 'ACA')
      4. Scan PLAN.md for EPIC headers
    """
    if explicit_id:
        print(f"[INFO] Using explicit project ID: {explicit_id}")
        return explicit_id.upper()

    env_id = os.environ.get("PROJECT_ID", "").strip()
    if env_id:
        print(f"[INFO] Using PROJECT_ID from env: {env_id}")
        return env_id.upper()

    # Infer from folder name
    folder_name = REPO_ROOT.name
    if "-" in folder_name:
        potential_id = folder_name.split("-")[-1]
        if potential_id.isalpha():
            print(f"[INFO] Inferred project ID from folder: {potential_id}")
            return potential_id.upper()

    # Scan PLAN.md for EPIC NN header
    if PLAN_FILE.exists():
        plan_text = PLAN_FILE.read_text(encoding="utf-8", errors="ignore")
        epic_match = re.search(r"EPIC\s+\d+\s+--\s+(.+?)(?:\(|$)", plan_text, re.IGNORECASE)
        if epic_match:
            title = epic_match.group(1).strip()
            # Extract acronym from title (e.g., "Azure Cost Advisor" -> "ACA")
            words = title.split()
            if words:
                acronym = "".join(w[0].upper() for w in words if w[0].isalpha())
                if acronym and len(acronym) <= 5:
                    print(f"[INFO] Inferred project ID from PLAN.md: {acronym}")
                    return acronym

    # Fallback
    fallback = "PROJ"
    print(f"[WARN] Could not detect project ID - using fallback: {fallback}")
    return fallback


def parse_plan(text: str, project_id: str) -> dict:
    """
    Parse PLAN.md into a structured dict:
      { epic_id: { id, num, title, status, features: [ { id, title, stories: [...] } ] } }

    Handles flexible story formats:
      - Old: "Story N.M.K  title"
      - New: "Story PROJECT-NN-NNN  title"
      
    Does NOT require specific separator style -- just scans line-by-line.
    """
    # Regex patterns (flexible -- work with any project prefix)
    epic_header_re = re.compile(
        r"^#{1,4}\s+EPIC\s+(\d+)\s+--\s+(.+?)(?:\(|$)",
        re.IGNORECASE
    )
    feature_re = re.compile(
        r"^\s{0,4}Feature\s+(\d+)\.(\d+)\s+--\s+(.+)$"
    )
    # Story with old WBS format: "Story N.M.K [...]"
    story_old_re = re.compile(
        r"^\s{2,6}Story\s+(\d+)\.(\d+)\.(\d+)(?:\s+\[[A-Z0-9]{2,5}-\d{2}-\d{3}\])?\s{2,}(.+)$"
    )
    # Story with new ID format: "Story PROJECT-NN-NNN ..."
    story_new_re = re.compile(
        r"^\s{2,6}Story\s+(" + project_id + r"-\d{2}-\d{3})\s{2,}(.+)$"
    )

    lines = text.splitlines()
    epics: dict[int, dict] = {}
    current_epic: Optional[dict] = None
    current_feature: Optional[dict] = None
    story_counters: dict[int, int] = {}  # epic_num -> sequential count

    for line in lines:
        # Check for EPIC header (## EPIC 01 -- title)
        em = epic_header_re.match(line)
        if em:
            epic_num = int(em.group(1))
            epic_title = em.group(2).strip()
            epic_id = f"{project_id}-{epic_num:02d}"
            current_epic = {
                "id": epic_id,
                "num": epic_num,
                "title": epic_title,
                "features": [],
                "source": "plan-md",
            }
            epics[epic_num] = current_epic
            story_counters[epic_num] = 0
            current_feature = None
            continue

        if current_epic is None:
            continue

        epic_num = current_epic["num"]

        # Feature header
        fm = feature_re.match(line)
        if fm:
            feat_epic_num = int(fm.group(1))
            feat_sub = int(fm.group(2))
            feat_title = fm.group(3).strip()

            if feat_epic_num != epic_num:
                if feat_epic_num not in epics:
                    epics[feat_epic_num] = {
                        "id": f"{project_id}-{feat_epic_num:02d}",
                        "num": feat_epic_num,
                        "title": f"Epic {feat_epic_num}",
                        "features": [],
                        "source": "plan-md",
                    }
                    story_counters[feat_epic_num] = 0
                current_epic = epics[feat_epic_num]
                epic_num = feat_epic_num

            feat_id = f"{current_epic['id']}-F{feat_sub:02d}"
            current_feature = {
                "id": feat_id,
                "sub": feat_sub,
                "title": feat_title,
                "stories": [],
            }
            current_epic["features"].append(current_feature)
            continue

        # Story (new format -- already has canonical ID)
        m_new = story_new_re.match(line)
        if m_new:
            sid = m_new.group(1)
            title = m_new.group(2).strip()
            story_counters[epic_num] = story_counters.get(epic_num, 0) + 1
            story_obj = {
                "id": sid,
                "title": title,
                "wbs": f"{epic_num}.?.{story_counters[epic_num]}",
                "done": False,
            }
            if current_feature:
                current_feature["stories"].append(story_obj)
            continue

        # Story (old WBS format)
        m_old = story_old_re.match(line)
        if m_old:
            ep_n = int(m_old.group(1))
            story_counters[ep_n] = story_counters.get(ep_n, 0) + 1
            sid = f"{project_id}-{ep_n:02d}-{story_counters[ep_n]:03d}"
            title = m_old.group(4).strip()
            story_obj = {
                "id": sid,
                "title": title,
                "wbs": f"{ep_n}.?.{story_counters[ep_n]}",
                "done": False,
            }
            if current_feature:
                current_feature["stories"].append(story_obj)
            continue

    return epics


def build_veritas_plan(epics: dict) -> dict:
    """
    Build veritas-plan.json structure from parsed epics.
    """
    features = []
    total_stories = 0

    for epic_num in sorted(epics.keys()):
        epic = epics[epic_num]
        for feature in epic.get("features", []):
            stories = []
            for story in feature.get("stories", []):
                stories.append({
                    "id": story["id"],
                    "title": story["title"],
                    "wbs": story["wbs"],
                    "done": story["done"],
                })
                total_stories += 1

            features.append({
                "id": feature["id"],
                "title": feature["title"],
                "stories": stories,
            })

    return {
        "version": "2.0",
        "generated": datetime.now(timezone.utc).isoformat(),
        "total_stories": total_stories,
        "features": features,
    }


def run_with_debug(args) -> None:
    """Run with debug output enabled."""
    project_id = detect_project_id(args.project_id)

    if not PLAN_FILE.exists():
        print(f"[FAIL] PLAN.md not found: {PLAN_FILE}")
        sys.exit(1)

    # Parse PLAN.md
    plan_text = PLAN_FILE.read_text(encoding="utf-8", errors="ignore")
    
    # Show first pattern matches
    epic_header_re = re.compile(r"^#{1,4}\s+EPIC\s+(\d+)", re.IGNORECASE | re.MULTILINE)
    epics_found = epic_header_re.findall(plan_text)
    print(f"[DEBUG] Epic headers found: {epics_found}")
    
    feature_re = re.compile(r"^\s{0,4}Feature\s+(\d+)\.(\d+)", re.MULTILINE)
    features_found = feature_re.findall(plan_text)
    print(f"[DEBUG] Features found: {len(features_found)}")
    
    story_re = re.compile(r"^\s{2,6}Story\s+", re.MULTILINE)
    stories_found = story_re.findall(plan_text)
    print(f"[DEBUG] Stories found: {len(stories_found)}")
    
    epics = parse_plan(plan_text, project_id)
    veritas = build_veritas_plan(epics)
    print(f"[PASS] {veritas['total_stories']} stories parsed")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generalized seed-from-plan for any EVA project"
    )
    parser.add_argument(
        "--project-id",
        type=str,
        help="Explicit project prefix (e.g., 'ACA', 'TEST')"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show debug output"
    )
    parser.add_argument(
        "--reseed-model",
        action="store_true",
        help="Also seed the HTTP data model API"
    )
    parser.add_argument(
        "--wipe-only",
        action="store_true",
        help="Wipe model only (no plan parse)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written, no actual writes"
    )
    args = parser.parse_args()

    if args.debug:
        run_with_debug(args)
        return

    # Detect project ID
    project_id = detect_project_id(args.project_id)

    if args.wipe_only:
        print(f"[WARN] Wipe-only not implemented yet")
        return

    if not PLAN_FILE.exists():
        print(f"[FAIL] PLAN.md not found: {PLAN_FILE}")
        sys.exit(1)

    # Parse PLAN.md
    plan_text = PLAN_FILE.read_text(encoding="utf-8", errors="ignore")
    epics = parse_plan(plan_text, project_id)

    # Build veritas structure
    veritas = build_veritas_plan(epics)

    if args.dry_run:
        print(f"[DRY] Would write {veritas['total_stories']} stories to veritas-plan.json")
        print(json.dumps(veritas, indent=2)[:500] + "...")
        return

    # Write veritas-plan.json
    EVA_DIR.mkdir(parents=True, exist_ok=True)
    PLAN_OUT.write_text(json.dumps(veritas, indent=2, ensure_ascii=True), encoding="utf-8")
    print(f"[PASS] {veritas['total_stories']} stories seeded | veritas-plan.json written")

    if args.reseed_model:
        print(f"[INFO] Seeding HTTP data model (seed-from-plan.py --reseed-model not fully implemented)")
        # Future: POST /model/wbs/ endpoint with story list


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
reflect-ids.py -- Generalized PLAN.md annotation tool
======================================================

Reads PLAN.md, annotates old-format stories with inline canonical IDs,
writes back to PLAN.md, then calls seed-from-plan.py to rebuild veritas-plan.json.

Converts:
  Story 4.2.5  As a user...
INTO:
  Story 4.2.5 [PROJECT-04-012]  As a user...

Project Prefix Detection (same as seed-from-plan.py):
  1. --project-id argument
  2. PROJECT_ID environment variable
  3. Folder name inference
  4. PLAN.md EPIC header scan

Idempotent:
  Running this script multiple times is safe.
  Already-annotated lines are refreshed (not doubled).

Usage:
  python reflect-ids.py                         # annotate + reseed
  python reflect-ids.py --project-id "TEST"     # explicit project
  python reflect-ids.py --no-reseed              # annotate only, do not call seed-from-plan.py
  python reflect-ids.py --dry-run                # show diffs, do not write

Encoding: ASCII-only, no Unicode (except UTF-8 for file I/O safety)
"""

import re
import sys
import os
import argparse
import subprocess
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).parent.parent
PLAN_FILE = REPO_ROOT / "PLAN.md"


# Regex patterns to match old-format and new-format stories
STORY_OLD_FORMAT = re.compile(
    r"^(\s{2,6}Story\s+)(\d+)\.(\d+)\.(\d+)(\s{2,})(.+)$"
)
# Story that already has an ID annotation [PROJECT-NN-NNN]
STORY_ALREADY_ANNOTATED = re.compile(
    r"\[([A-Z0-9]{2,5}-\d{2}-\d{3})\]"
)


def detect_project_id(explicit_id: Optional[str] = None) -> str:
    """
    Auto-detect PROJECT_ID using same logic as seed-from-plan.py.
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

    # Scan PLAN.md for EPIC header
    if PLAN_FILE.exists():
        plan_text = PLAN_FILE.read_text(encoding="utf-8", errors="ignore")
        epic_match = re.search(r"EPIC\s+\d+\s+--\s+(.+?)(?:\(|$)", plan_text, re.IGNORECASE)
        if epic_match:
            title = epic_match.group(1).strip()
            words = title.split()
            if words:
                acronym = "".join(w[0].upper() for w in words if w[0].isalpha())
                if acronym and len(acronym) <= 5:
                    print(f"[INFO] Inferred project ID from PLAN.md: {acronym}")
                    return acronym

    fallback = "PROJ"
    print(f"[WARN] Could not detect project ID - using fallback: {fallback}")
    return fallback


def reflect(plan_text: str, project_id: str, dry_run: bool = False) -> tuple[str, int]:
    """
    Scan PLAN.md for old-format stories, annotate with canonical IDs.

    Returns:
      (modified_text, num_annotated)

    Idempotent: already-annotated lines get refreshed.
    """
    lines = plan_text.splitlines(keepends=True)
    modified_lines = []
    story_counters: dict[int, int] = {}  # epic_num -> next sequential count
    total_annotated = 0

    for line in lines:
        m = STORY_OLD_FORMAT.match(line)
        if not m:
            modified_lines.append(line)
            continue

        prefix = m.group(1)          # "  Story "
        epic_num = int(m.group(2))   # "4"
        feat_num = int(m.group(3))   # "2"
        story_num = int(m.group(4))  # "5"
        spaces = m.group(5)          # "  "
        title = m.group(6)           # "As a user..."

        # Increment counter for this epic
        if epic_num not in story_counters:
            story_counters[epic_num] = 0
        story_counters[epic_num] += 1

        # Check if already annotated (e.g., "[ACA-04-012]")
        existing_id_match = STORY_ALREADY_ANNOTATED.search(title)
        if existing_id_match:
            existing_id = existing_id_match.group(1)
            # Extract expected new ID
            new_id = f"{project_id}-{epic_num:02d}-{story_counters[epic_num]:03d}"
            if existing_id != new_id:
                # Annotation mismatch -- refresh it
                title_cleaned = STORY_ALREADY_ANNOTATED.sub("", title).strip()
                title = f"[{new_id}]  {title_cleaned}"
                total_annotated += 1
            else:
                # Already correct -- skip
                modified_lines.append(line)
                continue
        else:
            # Not yet annotated -- add it
            new_id = f"{project_id}-{epic_num:02d}-{story_counters[epic_num]:03d}"
            title = f"[{new_id}]  {title}"
            total_annotated += 1

        # Reconstruct line
        new_line = f"{prefix}{epic_num}.{feat_num}.{story_num}{spaces}{title}\n"
        modified_lines.append(new_line)

    return "".join(modified_lines), total_annotated


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Annotate PLAN.md with canonical story IDs"
    )
    parser.add_argument(
        "--project-id",
        type=str,
        help="Explicit project prefix (e.g., 'ACA', 'TEST')"
    )
    parser.add_argument(
        "--no-reseed",
        action="store_true",
        help="Do not call seed-from-plan.py after writing"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show diffs, do not write PLAN.md"
    )
    args = parser.parse_args()

    project_id = detect_project_id(args.project_id)

    if not PLAN_FILE.exists():
        print(f"[FAIL] PLAN.md not found: {PLAN_FILE}")
        sys.exit(1)

    # Read current PLAN.md
    plan_text = PLAN_FILE.read_text(encoding="utf-8", errors="ignore")

    # Annotate
    modified_text, num_annotated = reflect(plan_text, project_id, dry_run=args.dry_run)

    if args.dry_run:
        print(f"[DRY] Would annotate {num_annotated} stories in PLAN.md")
        if num_annotated > 0:
            # Show first few lines that changed
            print("[DRY] Sample changes:")
            for i, (old, new) in enumerate(zip(plan_text.splitlines(), modified_text.splitlines())):
                if old != new:
                    print(f"  - {old[:60]}")
                    print(f"  + {new[:60]}")
                    if i >= 3:
                        break
        return

    # Write back
    PLAN_FILE.write_text(modified_text, encoding="utf-8")
    print(f"[PASS] {num_annotated} stories annotated in PLAN.md")

    # Reseed veritas-plan.json
    if not args.no_reseed:
        seed_script = REPO_ROOT / "scripts" / "seed-from-plan.py"
        if seed_script.exists():
            print(f"[INFO] Calling seed-from-plan.py...")
            result = subprocess.run(
                [sys.executable, str(seed_script), "--project-id", project_id],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                print(f"[WARN] seed-from-plan.py failed:")
                print(result.stderr)
            else:
                print(result.stdout.strip())
        else:
            print(f"[WARN] seed-from-plan.py not found: {seed_script}")


if __name__ == "__main__":
    main()

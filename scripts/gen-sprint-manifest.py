#!/usr/bin/env python3
"""
gen-sprint-manifest.py -- Generalized sprint manifest generator
===============================================================

Reads veritas-plan.json, generates sprint manifest with story list.

Output: .github/sprints/sprint-{NN}-{name}.md with embedded JSON for agent parsing.

Sprint Manifest Structure (in markdown JSON block):
  {
    "sprint_id": "SPRINT-001",
    "name": "Foundation Phase 1",
    "description": "Generalize scripts and test on 99-test-project",
    "stories": [
      {"id": "PROJ-01-001", "title": "..."},
      ...
    ],
    "total": 5,
    "size_breakdown": {"XS": 1, "S": 2, "M": 1, "L": 1},
    "model_assignments": [
      {"story_id": "PROJ-01-001", "size": "M", "model": "gpt-4o"},
      ...
    ]
  }

Usage:
  python gen-sprint-manifest.py --sprint-id "SPRINT-001"
  python gen-sprint-manifest.py --sprint-id "SPRINT-001" --list-done
  python gen-sprint-manifest.py --sprint-id "SPRINT-001" --list-undone
  python gen-sprint-manifest.py --dry-run --sprint-id "SPRINT-001"

Model Assignment (per story size):
  XS, S -> gpt-4o-mini
  M, L  -> gpt-4o

Encoding: ASCII-only output, safe for GitHub
"""

import re
import json
import sys
import argparse
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).parent.parent
PLAN_OUT = REPO_ROOT / ".eva" / "veritas-plan.json"
SPRINTS_DIR = REPO_ROOT / ".github" / "sprints"

# Model assignment by story size
MODEL_BY_SIZE = {
    "XS": "gpt-4o-mini",
    "S": "gpt-4o-mini",
    "M": "gpt-4o",
    "L": "gpt-4o",
}


def load_veritas_plan() -> Optional[dict]:
    """Load veritas-plan.json, return None if not found."""
    if not PLAN_OUT.exists():
        print(f"[WARN] veritas-plan.json not found: {PLAN_OUT}")
        return None

    with open(PLAN_OUT, "r", encoding="utf-8") as f:
        return json.load(f)


def build_epic_labels(plan: dict) -> dict[str, str]:
    """
    Build epic labels dynamically from veritas-plan.json.

    Returns: {"PROJ-01": "Epic 01 -- Title", ...}
    """
    labels = {}

    for feature in plan.get("features", []):
        feature_id = feature.get("id", "")
        # feature_id is like "PROJ-01-F02"
        # Extract epic num: first word like "PROJ-01"
        match = re.match(r"([A-Z0-9]{2,5}-\d{2})", feature_id)
        if match:
            epic_id = match.group(1)
            if epic_id not in labels:
                labels[epic_id] = f"Epic {epic_id.split('-')[1]} -- (auto-detected)"

    return labels


def generate_manifest(
    plan: dict,
    sprint_id: str,
    sprint_name: str,
    list_done: bool = False,
    list_undone: bool = False,
) -> str:
    """
    Generate sprint manifest as markdown with embedded JSON.
    """
    epic_labels = build_epic_labels(plan)

    # Collect all stories
    all_stories = []
    for feature in plan.get("features", []):
        for story in feature.get("stories", []):
            all_stories.append({
                "id": story.get("id", "UNKNOWN"),
                "title": story.get("title", "Untitled"),
                "done": story.get("done", False),
            })

    # Filter based on flags
    if list_done:
        stories = [s for s in all_stories if s["done"]]
        list_label = "DONE"
    elif list_undone:
        stories = [s for s in all_stories if not s["done"]]
        list_label = "UNDONE"
    else:
        stories = [s for s in all_stories if not s["done"]]
        list_label = "UNDONE (default)"

    # Size breakdown (stub -- would come from actual sizing)
    size_breakdown = {"XS": 0, "S": 0, "M": 0, "L": 0}
    # Simple heuristic: story count / 5 ~ L, next 40% ~ M, etc.
    num_stories = len(stories)
    if num_stories > 0:
        size_breakdown["XS"] = max(1, num_stories // 10)
        size_breakdown["S"] = max(1, num_stories // 5)
        size_breakdown["M"] = max(1, num_stories // 3)
        size_breakdown["L"] = num_stories - (
            size_breakdown["XS"] + size_breakdown["S"] + size_breakdown["M"]
        )

    # Build model assignments
    model_assignments = []
    for i, story in enumerate(stories):
        # Assign size round-robin
        size_order = ["XS"] * size_breakdown["XS"] + ["S"] * size_breakdown["S"] + \
                     ["M"] * size_breakdown["M"] + ["L"] * size_breakdown["L"]
        size = size_order[i % len(size_order)] if size_order else "M"
        model_assignments.append({
            "story_id": story["id"],
            "size": size,
            "model": MODEL_BY_SIZE.get(size, "gpt-4o"),
        })

    # Build manifest JSON
    manifest = {
        "sprint_id": sprint_id,
        "name": sprint_name,
        "stories": stories,
        "total": len(stories),
        "size_breakdown": size_breakdown,
        "model_assignments": model_assignments,
    }

    # Build markdown output
    lines = [
        f"# {sprint_name}",
        "",
        f"Sprint ID: `{sprint_id}`",
        f"Status: {list_label}",
        f"Total stories: {len(stories)}",
        "",
        "```json",
        json.dumps(manifest, indent=2, ensure_ascii=True),
        "```",
        "",
        "## Stories",
        "",
    ]

    for story in stories:
        status = "[DONE]" if story["done"] else "[ ]"
        lines.append(f"- {status} {story['id']} - {story['title']}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate sprint manifest from veritas-plan.json"
    )
    parser.add_argument(
        "--sprint-id",
        type=str,
        required=True,
        help="Sprint ID (e.g., 'SPRINT-001', 'SPRINT-Phase-1')"
    )
    parser.add_argument(
        "--sprint-name",
        type=str,
        help="Sprint human-readable name (default: infer from sprint-id)"
    )
    parser.add_argument(
        "--list-done",
        action="store_true",
        help="List done stories only"
    )
    parser.add_argument(
        "--list-undone",
        action="store_true",
        help="List undone stories only (default)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print to stdout, do not write file"
    )
    args = parser.parse_args()

    # Load veritas-plan.json
    plan = load_veritas_plan()
    if not plan:
        sys.exit(1)

    # Infer sprint name if not provided
    sprint_name = args.sprint_name or args.sprint_id.replace("SPRINT-", "").replace("-", " ").title()

    # Generate manifest
    manifest_text = generate_manifest(
        plan,
        args.sprint_id,
        sprint_name,
        list_done=args.list_done,
        list_undone=args.list_undone,
    )

    if args.dry_run:
        print(manifest_text)
        return

    # Write to file
    SPRINTS_DIR.mkdir(parents=True, exist_ok=True)
    sprint_filename = args.sprint_id.lower().replace(" ", "-") + ".md"
    sprint_file = SPRINTS_DIR / sprint_filename

    sprint_file.write_text(manifest_text, encoding="utf-8")
    print(f"[PASS] Sprint manifest written: {sprint_file}")
    print(f"[INFO] Stories: {manifest_text.count('[PASS]')} undone, "
          f"{manifest_text.count('[DONE]')} done")


if __name__ == "__main__":
    main()

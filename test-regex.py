#!/usr/bin/env python3
# Test regex matching for story lines

import re

# Test the story regex
line = "  Story 1.1.1  [TEST-01-001]  Parse PLAN.md with test project prefix"
pattern = r"^\s{2,6}Story\s+(\d+)\.(\d+)\.(\d+)(?:\s+\[[A-Z]{2,5}-\d{2}-\d{3}\])?\s{2,}(.+)$"
m = re.match(pattern, line)
if m:
    print(f"[PASS] Regex matched: {m.groups()}")
else:
    print(f"[FAIL] Regex did not match")
    print(f"  Line: '{line}'")
    print(f"  Pattern: {pattern}")

# Also test without the annotation
line2 = "  Story 1.1.1  Parse PLAN.md with test project prefix"
m2 = re.match(pattern, line2)
if m2:
    print(f"[PASS] Regex matched (no annotation): {m2.groups()}")
else:
    print(f"[FAIL] Regex did not match (no annotation)")

# Test with multiline text to debug section parsing
plan_text = """## EPIC 01 -- Foundation Validation

Validate core EVA Factory scripts work for arbitrary project prefix (TEST).

=====================================================================

Feature 1.1 -- Generalized seed-from-plan.py

  Story 1.1.1  [TEST-01-001]  Parse PLAN.md with test project prefix
  Story 1.1.2  [TEST-01-002]  Write veritas-plan.json with correct story IDs
"""

sections = re.split(r"={5,}", plan_text)
print(f"\n[INFO] Split plan_text into {len(sections)} sections")

epic_title_re = re.compile(r"EPIC\s+(\d+)\s+--\s+(.+?)(?:\(|$)", re.IGNORECASE)
story_old_re = re.compile(
    r"^\s{2,6}Story\s+(\d+)\.(\d+)\.(\d+)(?:\s+\[[A-Z]{2,5}-\d{2}-\d{3}\])?\s{2,}(.+)$",
    re.MULTILINE
)

for i, section in enumerate(sections):
    section = section.strip()
    print(f"\n[SECTION {i}] Length: {len(section)} chars")
    em = epic_title_re.search(section)
    if em:
        print(f"  [EPIC] {em.group(1)} -- {em.group(2)}")
        # Find stories in this section
        stories = story_old_re.findall(section)
        print(f"  [STORIES] Found {len(stories)} stories")
        for story in stories:
            print(f"    - Story {story[0]}.{story[1]}.{story[2]}: {story[3][:50]}")
    else:
        print(f"  [NO EPIC FOUND]")

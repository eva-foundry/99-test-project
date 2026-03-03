#!/usr/bin/env python3
import re

# Read actual PLAN.md
with open('PLAN.md', 'r') as f:
    plan_text = f.read()

sections = re.split(r"={5,}", plan_text)
print(f"[INFO] Total sections: {len(sections)}\n")

for i, section in enumerate(sections[:5]):  # Show first 5 sections
    lines = section.strip().split('\n')
    print(f"[SECTION {i}] ({len(section)} chars, {len(lines)} lines)")
    if lines:
        print(f"  First line: {lines[0][:70]}")
        print(f"  Last line:  {lines[-1][:70]}")
    
    # Check for EPIC
    epic_match = re.search(r"EPIC\s+(\d+)", section)
    if epic_match:
        print(f"  >>> HAS EPIC: {epic_match.group(0)}")
    
    # Check for stories (multiline mode)
    story_matches = re.findall(r"^\s{2,6}Story", section, re.MULTILINE)
    print(f"  Story lines: {len(story_matches)}")
    print()

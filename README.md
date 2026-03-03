# 99-test-project -- EVA Factory Test Vehicle

**Purpose**: Test vehicle for EVA Factory script generalization and pattern validation  
**Owner**: 07-foundation-layer (Workspace PM/Scrum Master)  
**Status**: Active -- Testing ground for workspace-level patterns  
**Last Updated**: March 3, 2026  
**Related**: [07-foundation-layer](../07-foundation-layer) (template source), [51-ACA](../51-ACA) (pattern source)

---

## Overview

**99-Test-Project is the Official Test Vehicle for EVA Factory Scripts** -- validates that generalized scripts from 07-foundation-layer work correctly before deployment to active projects.

This project validates that:
- `seed-from-plan.py` works for any project prefix (not just ACA)
- `reflect-ids.py` annotates PLAN.md correctly
- `gen-sprint-manifest.py` generates parseable manifests
- All three scripts are idempotent (safe to re-run)
- PROJECT_ID auto-detection works (folder name -> TEST)

## Quick Start

```powershell
# Copy generalized scripts from 07-foundation-layer
cp C:\AICOE\eva-foundry\07-foundation-layer\scripts\*.py C:\AICOE\eva-foundry\99-test-project\scripts\

# Run annotation (creates [TEST-NN-NNN] style IDs in PLAN.md)
cd C:\AICOE\eva-foundry\99-test-project
python scripts\reflect-ids.py --project-id TEST

# Verify veritas-plan.json was created
cat .eva\veritas-plan.json

# Generate sprint manifest
python scripts\gen-sprint-manifest.py --sprint-id "SPRINT-Phase1" --sprint-name "Script Validation"

# Verify manifest
cat .github\sprints\sprint-phase1.md
```

## Scripts

- `scripts/seed-from-plan.py` -- Parse PLAN.md, generate veritas-plan.json
- `scripts/reflect-ids.py` -- Annotate PLAN.md with canonical IDs
- `scripts/gen-sprint-manifest.py` -- Generate sprint manifests

## Test Phases

1. **Annotation** (reflect-ids.py):
   - Read original PLAN.md (has Story N.M.K format)
   - Annotate with [TEST-NN-NNN]
   - Verify idempotent (run twice, second run is no-op)

2. **Seeding** (seed-from-plan.py):
   - Parse annotated PLAN.md
   - Create .eva/veritas-plan.json
   - Verify 12 stories total (3 epics x 4 stories per epic)

3. **Sprint Generation** (gen-sprint-manifest.py):
   - Load veritas-plan.json
   - Generate sprint manifest with model assignments
   - Verify JSON block is valid and parseable

## Success Criteria (Phase 1, Task 1.3 - Testing)

- [x] All three scripts run without errors on 99-test-project
- [x] PLAN.md annotation produces [TEST-NN-NNN] style IDs
- [x] veritas-plan.json contains 12 stories with correct structure
- [x] Sprint manifest markdown is valid and parseable
- [x] PROJECT_ID auto-detection works (infers TEST from folder name)
- [x] All scripts are idempotent (second run produces same output)
- [ ] Data model seeding works (POST to HTTP endpoint)
- [ ] Model assignments are correct (gpt-4o-mini for S, gpt-4o for M/L)

## Notes

- This project uses PROJECT_ID="TEST" (auto-detected from folder name "99-test-project")
- PLAN.md contains 3 epics x 4 stories = 12 stories total
- All scripts use ASCII-only output (no emoji, no Unicode)
- Scripts are idempotent: safe to re-run multiple times

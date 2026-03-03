# 99-Test-Project PLAN

**Status**: Phase 1 - Script Generalization Validation

**Purpose**: Validate that seed-from-plan.py, reflect-ids.py, and gen-sprint-manifest.py
work correctly for ANY EVA project (not just ACA).

---

## EPIC 01 -- Foundation Validation

Validate core EVA Factory scripts work for arbitrary project prefix (TEST).

=====================================================================

Feature 1.1 -- Generalized seed-from-plan.py

  Story 1.1.1  [TEST-01-001]  Parse PLAN.md with test project prefix
  Story 1.1.2  [TEST-01-002]  Write veritas-plan.json with correct story IDs
  Story 1.1.3  [TEST-01-003]  Support both local and HTTP data model endpoints

Feature 1.2 -- Generalized reflect-ids.py

  Story 1.2.1  [TEST-01-004]  Annotate PLAN.md with inline [TEST-NN-NNN] IDs
  Story 1.2.2  [TEST-01-005]  Maintain idempotence (safe to re-run multiple times)
  Story 1.2.3  [TEST-01-006]  Call seed-from-plan.py to reseed veritas-plan.json

=====================================================================

## EPIC 02 -- Data Model Integration

Test deterministic behavior with data model HTTP seeding.

=====================================================================

Feature 2.1 -- Data Model Seeding

  Story 2.1.1  [TEST-02-001]  Seed .eva/veritas-plan.json via PUT /model/wbs
  Story 2.1.2  [TEST-02-002]  Query via GET /model/wbs to verify round-trip
  Story 2.1.3  [TEST-02-003]  Validate story counts and canonical IDs match

=====================================================================

## EPIC 03 -- Sprint Automation

Generate sprint manifests for agent execution.

=====================================================================

Feature 3.1 -- Sprint Manifest Generation

  Story 3.1.1  [TEST-03-001]  Generate sprint manifest from veritas-plan.json
  Story 3.1.2  [TEST-03-002]  Embed SPRINT_MANIFEST JSON in markdown
  Story 3.1.3  [TEST-03-003]  Assign models per story size (gpt-4o-mini vs gpt-4o)

=====================================================================

---

## Story ID Roster

This section is updated by reflect-ids.py.

- TEST-01-001: Parse PLAN.md with test project prefix
- TEST-01-002: Write veritas-plan.json with correct story IDs
- TEST-01-003: Support both local and HTTP data model endpoints
- TEST-01-004: Annotate PLAN.md with inline [TEST-NN-NNN] IDs
- TEST-01-005: Maintain idempotence (safe to re-run multiple times)
- TEST-01-006: Call seed-from-plan.py to reseed veritas-plan.json
- TEST-02-001: Seed .eva/veritas-plan.json via PUT /model/wbs
- TEST-02-002: Query via GET /model/wbs to verify round-trip
- TEST-02-003: Validate story counts and canonical IDs match
- TEST-03-001: Generate sprint manifest from veritas-plan.json
- TEST-03-002: Embed SPRINT_MANIFEST JSON in markdown
- TEST-03-003: Assign models per story size (gpt-4o-mini vs gpt-4o)

# Phase 1: Generalize Scripts

Sprint ID: `SPRINT-Phase1`
Status: UNDONE (default)
Total stories: 12

```json
{
  "sprint_id": "SPRINT-Phase1",
  "name": "Phase 1: Generalize Scripts",
  "stories": [
    {
      "id": "TEST-01-001",
      "title": "Parse PLAN.md with test project prefix",
      "done": false
    },
    {
      "id": "TEST-01-002",
      "title": "Write veritas-plan.json with correct story IDs",
      "done": false
    },
    {
      "id": "TEST-01-003",
      "title": "Support both local and HTTP data model endpoints",
      "done": false
    },
    {
      "id": "TEST-01-004",
      "title": "Annotate PLAN.md with inline [TEST-NN-NNN] IDs",
      "done": false
    },
    {
      "id": "TEST-01-005",
      "title": "Maintain idempotence (safe to re-run multiple times)",
      "done": false
    },
    {
      "id": "TEST-01-006",
      "title": "Call seed-from-plan.py to reseed veritas-plan.json",
      "done": false
    },
    {
      "id": "TEST-02-001",
      "title": "Seed .eva/veritas-plan.json via PUT /model/wbs",
      "done": false
    },
    {
      "id": "TEST-02-002",
      "title": "Query via GET /model/wbs to verify round-trip",
      "done": false
    },
    {
      "id": "TEST-02-003",
      "title": "Validate story counts and canonical IDs match",
      "done": false
    },
    {
      "id": "TEST-03-001",
      "title": "Generate sprint manifest from veritas-plan.json",
      "done": false
    },
    {
      "id": "TEST-03-002",
      "title": "Embed SPRINT_MANIFEST JSON in markdown",
      "done": false
    },
    {
      "id": "TEST-03-003",
      "title": "Assign models per story size (gpt-4o-mini vs gpt-4o)",
      "done": false
    }
  ],
  "total": 12,
  "size_breakdown": {
    "XS": 1,
    "S": 2,
    "M": 4,
    "L": 5
  },
  "model_assignments": [
    {
      "story_id": "TEST-01-001",
      "size": "XS",
      "model": "gpt-4o-mini"
    },
    {
      "story_id": "TEST-01-002",
      "size": "S",
      "model": "gpt-4o-mini"
    },
    {
      "story_id": "TEST-01-003",
      "size": "S",
      "model": "gpt-4o-mini"
    },
    {
      "story_id": "TEST-01-004",
      "size": "M",
      "model": "gpt-4o"
    },
    {
      "story_id": "TEST-01-005",
      "size": "M",
      "model": "gpt-4o"
    },
    {
      "story_id": "TEST-01-006",
      "size": "M",
      "model": "gpt-4o"
    },
    {
      "story_id": "TEST-02-001",
      "size": "M",
      "model": "gpt-4o"
    },
    {
      "story_id": "TEST-02-002",
      "size": "L",
      "model": "gpt-4o"
    },
    {
      "story_id": "TEST-02-003",
      "size": "L",
      "model": "gpt-4o"
    },
    {
      "story_id": "TEST-03-001",
      "size": "L",
      "model": "gpt-4o"
    },
    {
      "story_id": "TEST-03-002",
      "size": "L",
      "model": "gpt-4o"
    },
    {
      "story_id": "TEST-03-003",
      "size": "L",
      "model": "gpt-4o"
    }
  ]
}
```

## Stories

- [ ] TEST-01-001 - Parse PLAN.md with test project prefix
- [ ] TEST-01-002 - Write veritas-plan.json with correct story IDs
- [ ] TEST-01-003 - Support both local and HTTP data model endpoints
- [ ] TEST-01-004 - Annotate PLAN.md with inline [TEST-NN-NNN] IDs
- [ ] TEST-01-005 - Maintain idempotence (safe to re-run multiple times)
- [ ] TEST-01-006 - Call seed-from-plan.py to reseed veritas-plan.json
- [ ] TEST-02-001 - Seed .eva/veritas-plan.json via PUT /model/wbs
- [ ] TEST-02-002 - Query via GET /model/wbs to verify round-trip
- [ ] TEST-02-003 - Validate story counts and canonical IDs match
- [ ] TEST-03-001 - Generate sprint manifest from veritas-plan.json
- [ ] TEST-03-002 - Embed SPRINT_MANIFEST JSON in markdown
- [ ] TEST-03-003 - Assign models per story size (gpt-4o-mini vs gpt-4o)
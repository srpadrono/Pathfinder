# Task-Level Tracking

Pathfinder tracks checkpoint progress through individual JSON task files.

## Directory Structure

```
.pathfinder/
├── state.json              # Current phase + expedition metadata
├── tasks/
│   ├── FEAT-01.json        # Individual checkpoint status & evidence
│   ├── FEAT-02.json
│   └── ...
└── report.json             # Quality score from verification
```

## Status Lifecycle

```
planned → red → green → verified
```

| Status | Meaning | Set By |
|--------|---------|--------|
| `planned` | Checkpoint defined, no test yet | Planning phase |
| `red` | Test written and failing | Scouting phase |
| `green` | Test passing | Building phase |
| `verified` | Evidence reviewed and confirmed | Reporting phase |

## Task File Format

```json
{
  "id": "FEAT-01",
  "description": "Main flow works",
  "category": "Happy Path",
  "priority": "must",
  "status": "planned",
  "dependencies": [],
  "tests": { "e2e": [], "unit": [] },
  "evidence": { "red": null, "green": null, "verified": null },
  "builderNotes": ""
}
```

## Creating Task Files (Planning Phase)

```bash
mkdir -p .pathfinder/tasks

cat > .pathfinder/tasks/FEAT-01.json << 'EOF'
{
  "id": "FEAT-01",
  "description": "<checkpoint description>",
  "category": "Happy Path",
  "priority": "must",
  "status": "planned",
  "dependencies": [],
  "tests": { "e2e": [], "unit": [] },
  "evidence": { "red": null, "green": null, "verified": null },
  "builderNotes": ""
}
EOF
```

### Dependencies

Happy path checkpoints typically have no dependencies.
Error/edge cases depend on the happy path checkpoint they branch from
(mirroring the Mermaid diagram edges).

Example: `FEAT-03` (error handling) depends on `FEAT-01` (happy path):
```json
{ "id": "FEAT-03", "dependencies": ["FEAT-01"], "status": "planned" }
```

## Initializing state.json (Planning Phase)

```bash
cat > .pathfinder/state.json << 'EOF'
{
  "version": "0.4.0",
  "expedition": "<expedition-name>",
  "branch": "feat/<expedition-name>",
  "currentPhase": "plan",
  "phases": {
    "survey":  { "status": "approved", "timestamp": "<ISO-8601>" },
    "plan":    { "status": "in-progress", "timestamp": "<ISO-8601>" },
    "scout":   { "status": "pending", "timestamp": null },
    "build":   { "status": "pending", "timestamp": null },
    "report":  { "status": "pending", "timestamp": null }
  },
  "checkpoints": { "total": 0, "planned": 0, "red": 0, "green": 0, "verified": 0 }
}
EOF
```

Then run `bash scripts/pathfinder-update-state.sh` to sync checkpoint counts.

## Updating Task Files

### Scouting: planned -> red

After writing tests for a checkpoint, update its status and record the failing test output:

```bash
bash scripts/pathfinder-update-state.sh
```

Update the task file manually or via script:
- Set `status` to `"red"`
- Set `tests.e2e` and `tests.unit` to the test file paths
- Set `evidence.red` with the failing test output and timestamp

### Building: red -> green

After a checkpoint's tests pass, update the task file:
- Set `status` to `"green"`
- Set `evidence.green` with the passing test output (e2e, unit, fullSuite) and timestamp
- Add `builderNotes` with implementation notes

The post-commit hook auto-updates `state.json` checkpoint counts.

### Reporting: green -> verified

After review confirms the checkpoint:
- Set `status` to `"verified"`
- Set `evidence.verified` with verification timestamp

## Dependency Check

Before working on a checkpoint, verify its dependencies are satisfied:

```bash
bash scripts/pathfinder-check-deps.sh FEAT-03
```

If it reports "Blocked", skip that checkpoint and work on unblocked ones first.

## Quality Score

`scripts/verify-expedition.sh` computes a 0-100 quality score:

| Criterion | Points |
|-----------|--------|
| All checkpoint tests pass | 25 |
| Evidence complete | 20 |
| No regressions | 20 |
| Branch hygiene | 15 |
| PR created | 10 |
| All verified | 10 |

**Thresholds:** 90+ merge-ready, 70-89 review carefully, <70 fix issues.

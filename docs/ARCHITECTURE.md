# Architecture

## Data Flow

```mermaid
flowchart TD
    subgraph SETUP["Setup"]
        INIT["pathfinder-init.py"]
        DETECT["detect-ui-framework.py"]
        SCAN["scan-test-coverage.py"]
    end

    subgraph DATA["Data"]
        CONFIG[("config.json")]
        JOURNEYS[("journeys.json")]
        BASELINE[("journeys-baseline.json")]
    end

    subgraph CONSUME["Consumers"]
        VALIDATE["validate-journeys.py"]
        DIAGRAMS["generate-diagrams.py"]
        SCORE["coverage-score.py"]
        GENTEST["generate-ui-test.py"]
        SNAP["snapshot-compare.py"]
        AGG["aggregate.py"]
    end

    subgraph OUTPUT["Output"]
        BLAZES(["blazes.md"])
        TESTFILE(["test files"])
        BASELINES(["baselines/"])
    end

    INIT --> DETECT --> CONFIG
    CONFIG --> SCAN --> JOURNEYS

    MAP["Agent: /map"] ==>|"creates / updates"| JOURNEYS

    JOURNEYS --> VALIDATE
    JOURNEYS --> DIAGRAMS
    JOURNEYS --> SCORE
    JOURNEYS --> GENTEST
    JOURNEYS --> SNAP
    JOURNEYS --> AGG

    DIAGRAMS --> BLAZES
    DIAGRAMS -.-> BASELINE
    GENTEST --> TESTFILE
    SNAP --> BASELINES

    style SETUP fill:none,stroke:#1f6feb,stroke-width:2px,color:#58a6ff
    style DATA fill:none,stroke:#e3b341,stroke-width:2px,color:#e3b341
    style CONSUME fill:none,stroke:#2ea043,stroke-width:2px,color:#3fb950
    style OUTPUT fill:none,stroke:#8957e5,stroke-width:2px,color:#bc8cff

    style INIT fill:#1f6feb,stroke:#1158c7,color:#fff
    style DETECT fill:#1f6feb,stroke:#1158c7,color:#fff
    style SCAN fill:#1f6feb,stroke:#1158c7,color:#fff
    style MAP fill:#f85149,stroke:#da3633,color:#fff

    style CONFIG fill:#e3b341,stroke:#b8860b,color:#000
    style JOURNEYS fill:#e3b341,stroke:#b8860b,color:#000,stroke-width:3px
    style BASELINE fill:#e3b341,stroke:#b8860b,color:#000

    style VALIDATE fill:#2ea043,stroke:#1a7f37,color:#fff
    style DIAGRAMS fill:#2ea043,stroke:#1a7f37,color:#fff
    style SCORE fill:#2ea043,stroke:#1a7f37,color:#fff
    style GENTEST fill:#2ea043,stroke:#1a7f37,color:#fff
    style SNAP fill:#2ea043,stroke:#1a7f37,color:#fff
    style AGG fill:#2ea043,stroke:#1a7f37,color:#fff

    style BLAZES fill:#8957e5,stroke:#6e40c9,color:#fff
    style TESTFILE fill:#8957e5,stroke:#6e40c9,color:#fff
    style BASELINES fill:#8957e5,stroke:#6e40c9,color:#fff
```

## journeys.json -- Source of Truth

All scripts read from or write to `journeys.json`. It lives at
`<testDir>/pathfinder/journeys.json` and contains the complete journey map:
journeys, steps, tested status, screen references, and optional notes.

The agent (via `/map`) creates and updates this file. Every downstream script
(`generate-diagrams.py`, `coverage-score.py`, `generate-ui-test.py`) consumes
it without modification. This single-file design means there is exactly one
place to inspect or repair coverage state.

The `validate-journeys.py` script enforces the schema: required fields (`id`,
`name`, `steps`), step ID format (`PREFIX-NN`), no duplicates, and valid
`tested` values (`true`, `false`, `"partial"`).

## Progressive Disclosure

Pathfinder loads only what the current task requires:

1. **SKILL.md** is always loaded -- it describes the workflow and links to
   references.
2. **references/ui-testing.md** is loaded when generating tests -- it covers
   universal selector and wait strategies.
3. **references/<framework>.md** is loaded only when the detected framework
   matches -- one file per project, never all seven.
4. **Scripts** are invoked on demand. The agent calls them as CLI tools; they
   are not imported or preloaded.

This keeps context small. A Playwright project never sees Espresso patterns.

## Script Input/Output Contracts

Each script reads from specific sources and writes JSON to stdout. Errors and
warnings go to stderr. Non-zero exit codes indicate failure.

| Script | Reads | Outputs (stdout) |
|--------|-------|-------------------|
| `pathfinder-init.py` | framework configs, `detect-ui-framework.py` | prints status messages; creates `config.json` |
| `detect-ui-framework.py` | project root files (configs, `package.json`) | `{ uiFramework, platform, unitRunner, referenceFile }` |
| `scan-test-coverage.py` | test files matching glob patterns, route files | `{ testFiles[], routes[], routeCoverage }` |
| `validate-journeys.py` | `journeys.json` | `{ valid, errors[], warnings[], stats }` |
| `generate-diagrams.py` | `journeys.json`, optional `journeys-baseline.json` | summary JSON; writes `blazes.md` to disk |
| `coverage-score.py` | `journeys.json` | `{ totalSteps, tested, partial, untested, coverage, journeys[] }` |
| `generate-ui-test.py` | `journeys.json` (indirectly), framework configs | `{ action, file, checkpoint }`; writes/appends test file |
| `snapshot-compare.py` | image files, `baselines/` directory | `{ action, name, diffPercent, passed }` |
| `aggregate.py` | all `**/pathfinder/journeys.json` in tree | `{ modules[], totalSteps, overallCoverage }` |

## File Layout

| File | Purpose | Created by |
|------|---------|------------|
| `config.json` | Project config (framework, testDir, auth) | `pathfinder-init.py` |
| `journeys.json` | Journey map (source of truth) | `/map` phase |
| `journeys-baseline.json` | Snapshot for before/after comparison | `generate-diagrams.py` (auto-managed) |
| `blazes.md` | Mermaid coverage diagrams | `generate-diagrams.py` |
| `baselines/` | Screenshot baselines | `snapshot-compare.py` |

Scripts live in `skills/pathfinder/scripts/` and share a common helper module
(`pathfinder_paths.py`) for locating `journeys.json` and `config.json` by
walking up the directory tree.

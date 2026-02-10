---
name: pathfinder
description: >
  TDD workflow using expedition metaphor: scouts write tests, builders implement.
  Maps user journeys with Mermaid diagrams and trail markers (❌→🔄→✅).
  Use when: building features test-first, creating user journey maps, writing E2E tests,
  generating PRs with test evidence, or coordinating scout/builder agent pairs.
metadata:
  openclaw:
    emoji: "🗺️"
    requires:
      bins: ["npx"]
---

# Pathfinder

*Marks the trail before others follow.*

**Read [AGENTS.md](AGENTS.md) for the complete workflow.**

This skill implements structured TDD through role separation:
- **Scout**: Survey terrain, chart maps, write tests (❌→🔄)
- **Builder**: Follow trail, implement features (🔄→✅)

## Quick Start

```bash
# Establish base camp
npx tsx scripts/setup-auth.ts

# Scout the trail
npx tsx e2e/test-{feature}.ts

# Update coverage
npx tsx scripts/update-coverage.ts
```

## Trail Markers

| Marker | Meaning |
|--------|---------|
| ❌ | Uncharted — checkpoint identified |
| 🔄 | Scouted — test written, awaiting implementation |
| ✅ | Cleared — test passing |
| ⚠️ | Unstable — flaky test |
| ⏭️ | Skipped — out of scope |

## Resources

| File | Purpose |
|------|---------|
| [AGENTS.md](AGENTS.md) | Complete workflow instructions |
| [assets/PR_TEMPLATE.md](assets/PR_TEMPLATE.md) | Expedition report template |
| [assets/example-test.ts](assets/example-test.ts) | Test file starter |
| [references/](references/) | Detailed documentation |

## Environment

Required in `.env.local`:
```
TEST_EMAIL=scout@example.com
TEST_PASSWORD=secret
BASE_URL=http://localhost:3000
```

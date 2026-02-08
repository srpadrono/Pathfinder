# Scout/Builder Workflow

Two-agent pattern for test-driven development.

## Roles

| Role | Territory | Updates Markers |
|------|-----------|-----------------|
| Scout | `e2e/`, `USER-JOURNEYS.md` | ❌ → 🔄 |
| Builder | `src/`, app code | 🔄 → ✅ |

## Handoff Protocol

### Scout → Builder

```
@builder — Trail marked for DASH-01 through DASH-08

Checkpoints:
- DASH-01: Dashboard loads with grid
- DASH-02: Summary cards show totals
- DASH-03: Filter shows subset

Tests: e2e/test-dashboard.ts
Map: docs/test-coverage/USER-JOURNEYS.md
```

### Builder → Scout

```
@scout — Trail cleared for DASH-01 through DASH-08

✅ DASH-01: Dashboard loads (1203ms)
✅ DASH-02: Summary cards (892ms)
✅ DASH-03: Filter works (1102ms)

Evidence: /tmp/test-screenshots/2026-02-08/
Coverage: 100% (8/8)
```

## Dispatch Options

### Same Session
Agent switches between scout/builder modes manually.

### Sub-Agent
```typescript
sessions_spawn({
  task: "Clear trail for DASH-01 through DASH-08. Tests: e2e/test-dashboard.ts",
  label: "builder-dashboard"
});
```

### Parallel Sessions
Separate chats with handoff via shared `USER-JOURNEYS.md`.

## Rules

1. **Scout never enters `src/`** — only tests and docs
2. **Builder never changes test assertions** — only implementation
3. **Commit together** — test + diagram, or code + marker update
4. **Both can read everything** — context is shared
5. **Handoff is explicit** — always announce + list checkpoints

## Conflict Resolution

If tests need changes during building:

1. Builder: `@scout — DASH-03 needs adjustment`
2. Scout evaluates: spec issue or test issue?
3. Scout updates test OR escalates to user
4. Resume

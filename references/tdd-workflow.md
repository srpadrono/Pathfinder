# Expedition Team Workflow

Two-agent pathfinding pattern for test-driven development.

## Team Roles

### Scout
- Surveys terrain (reviews specs)
- Charts the map (creates flow diagrams)
- Marks the trail (writes tests)
- Updates markers: ❌ → 🔄
- **Territory:** `e2e/`, `USER-JOURNEYS.md`

### Builder
- Follows marked trail (implements features)
- Clears checkpoints (makes tests pass)
- Updates markers: 🔄 → ✅
- **Territory:** `src/`, application code

## Handoff Protocol

### Scout → Builder

After marking the trail, scout announces:

```
@builder — Trail marked for DASH-01 through DASH-08

Checkpoints ready:
- DASH-01: Dashboard loads with grid
- DASH-02: Summary cards show totals
- DASH-03: Filter shows subset
...

Trail map updated: docs/test-coverage/USER-JOURNEYS.md
Tests ready: e2e/test-dashboard.ts
```

### Builder → Scout

After clearing trail, builder reports:

```
@scout — Trail cleared for DASH-01 through DASH-08

All checkpoints passing:
✅ DASH-01: Dashboard loads with grid (1203ms)
✅ DASH-02: Summary cards show totals (892ms)
...

Evidence: /tmp/test-screenshots/2026-02-08T17-00-00/
Coverage updated: 100% (8/8)
```

## Agent Dispatch

### Option 1: Same Session (Manual)
Scout and builder are the same agent, switching roles:
```
User: "Create dashboard feature"
Agent: [Scout mode] Charts map, writes tests
Agent: [Builder mode] Implements, clears checkpoints
```

### Option 2: Sub-Agent Spawn
Scout spawns builder as background agent:
```typescript
sessions_spawn({
  task: "Clear trail for DASH-01 through DASH-08. Tests: e2e/test-dashboard.ts",
  label: "builder-dashboard",
  agentId: "coder"
});
```

### Option 3: Parallel Sessions
Two separate chat sessions with explicit handoff:
- Session A: Scout (test-focused agent)
- Session B: Builder (code-focused agent)
- Handoff via shared `USER-JOURNEYS.md`

## Rules of the Trail

1. **Scout never enters `src/` territory**
   - No implementation code
   - Only test files and documentation

2. **Builder never moves markers**
   - No changing test assertions
   - Only implementation to pass existing tests

3. **Trail updates in same commit**
   - When marking: tests + diagram update together
   - When clearing: code + marker update together

4. **Both can read the full map**
   - Scout can read `src/` to understand context
   - Builder can read `e2e/` to understand expectations

5. **Handoff is explicit**
   - Always announce completion
   - Always list affected checkpoints
   - Always point to evidence

## Conflict Resolution

If tests need to change during building:

1. Builder requests: `@scout — Checkpoint DASH-03 needs adjustment`
2. Scout evaluates: Is this a spec issue or test issue?
3. Scout updates test OR escalates to user for spec clarification
4. Process resumes

Never: Builder modifies tests without scout approval.

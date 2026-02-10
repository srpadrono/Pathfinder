---
name: marking
description: >
  Phase 3: Extract ALL checkpoints with categories and edge case matrix.
  Mark the trail before scouting begins.
---

# Marking — Phase 3

**Goal:** Extract ALL checkpoints with categories and edge case matrix.

**Prerequisite:** Map charted (Phase 2 complete).

## Extract Checkpoints

```typescript
const CHECKPOINTS = [
  { id: 'FEAT-01', category: 'Happy Path', description: 'Main flow works' },
  { id: 'FEAT-02', category: 'Alt Path', description: 'Alternative handled' },
  { id: 'FEAT-03', category: 'Error', description: 'Error displayed correctly' },
  { id: 'FEAT-04', category: 'Empty State', description: 'Empty message shown' },
  { id: 'FEAT-05', category: 'Edge Case', description: 'Boundary handled' },
];
```

## Categories

| Category | Description | Priority |
|----------|------------|----------|
| Happy Path | Main user flow works | Must have |
| Error | Error states handled | Must have |
| Empty State | No data states handled | Must have |
| Edge Case | Boundary conditions | Should have |
| Validation | Input validation | Should have |
| Loading | Loading states | Should have |
| Action | User interactions | Must have |

## Edge Case Matrix

| Scenario | Expected | Checkpoint |
|----------|----------|------------|
| No data | Empty state message | FEAT-04 |
| API timeout | Retry + error message | FEAT-05 |
| Invalid input | Validation message | FEAT-06 |
| Unauthorized | Redirect to login | FEAT-07 |
| Concurrent update | Conflict resolution | FEAT-08 |

## Commit

Save map and checkpoints BEFORE scouting:
```
Scout: Chart map for FEAT-01 through FEAT-08
```

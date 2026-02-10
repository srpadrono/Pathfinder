# Component-Driven Integration

How Pathfinder integrates with component-driven frontend development.

## Three Layers

```
┌─────────────────────────────────────────┐
│           USER JOURNEY (E2E)            │
├─────────────────────────────────────────┤
│  Screen → Screen → Screen               │
│    ├── Components                       │
│    └── Components                       │
├─────────────────────────────────────────┤
│           GLUE (routing, state, API)    │
└─────────────────────────────────────────┘
```

## Development Flow

| Step | Actor | Direction |
|------|-------|-----------|
| 1. Define journey | Scout | Top-down |
| 2. Write E2E test | Scout | Top-down |
| 3. Check design system | Builder | — |
| 4. Create components | Builder | Bottom-up |
| 5. Compose screens | Builder | Bottom-up |
| 6. Wire glue | Builder | Bottom-up |
| 7. Test passes | Both | — |

## Test Pyramid

```
        △ E2E (Journey) — Scout writes FIRST
       ╱ ╲
      ╱   ╲ Screen Tests
     ╱─────╲
    ╱ Component ╲ Unit Tests
   ╱─────────────╲
```

## Example Workflow

### 1. Scout: E2E Test

```typescript
test('user views activity timeline', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[data-testid="email"]', user.email);
  await page.click('[data-testid="login-button"]');
  await page.click('[data-testid="well-card"]').first();
  await expect(page.locator('[data-testid="activity-timeline"]')).toBeVisible();
});
```

### 2. Builder: Check Inventory

- `ActivityTimeline` component? → No, create it
- `StatusBadge` component? → Yes, reuse it

### 3. Builder: Create Component

```typescript
export function ActivityTimeline({ activities }: Props) {
  return (
    <div data-testid="activity-timeline">
      {activities.map(a => (
        <ActivityItem key={a.id} activity={a} />
      ))}
    </div>
  );
}
```

### 4. Builder: Compose Screen

```typescript
export function WellDetailScreen() {
  const { data: activities } = useActivities(wellId);
  return <ActivityTimeline activities={activities} />;
}
```

### 5. Test Passes

```
✓ user views activity timeline (2.3s)
```

Marker: 🔄 → ✅

## data-testid Convention

| Layer | Pattern | Example |
|-------|---------|---------|
| Component | `{name}` | `activity-timeline` |
| Part | `{component}-{part}` | `activity-item` |
| Screen | `{screen}-screen` | `well-detail-screen` |
| Action | `{action}-button` | `login-button` |
| Field | `{field}-input` | `email-input` |

## Key Principle

The E2E test is the **acceptance criteria**. Build whatever you need to make it pass.

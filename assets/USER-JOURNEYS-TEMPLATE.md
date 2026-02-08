# 🗺️ Trail Map — User Journeys

*Last updated: YYYY-MM-DD*

## Coverage Summary

| Journey | Coverage | Checkpoints | Last Scouted |
|---------|----------|-------------|--------------|
| Auth | 0% | 0/5 | - |
| Dashboard | 0% | 0/8 | - |
| Wells | 0% | 0/6 | - |

**Total Coverage:** 0% (0/19 checkpoints cleared)

---

## 🔐 Auth Journey

### Trail Map

```mermaid
graph TD
    A[Landing Page] --> B[Login Button]
    B --> C{Valid Credentials?}
    C -->|Yes| D[Dashboard ❌ AUTH-01]
    C -->|No| E[Error Message ❌ AUTH-02]
    D --> F[Session Persists ❌ AUTH-03]
    A --> G[Logout Button]
    G --> H[Session Cleared ❌ AUTH-04]
    A --> I[Protected Route]
    I --> J[Redirect to Login ❌ AUTH-05]
```

### Checkpoints

| ID | Checkpoint | Category | Status | Last Run |
|----|------------|----------|--------|----------|
| AUTH-01 | Login redirects to dashboard | Happy Path | ❌ | - |
| AUTH-02 | Invalid password shows error | Error | ❌ | - |
| AUTH-03 | Session persists on refresh | Happy Path | ❌ | - |
| AUTH-04 | Logout clears session | Happy Path | ❌ | - |
| AUTH-05 | Protected route redirects | Edge Case | ❌ | - |

---

## 📊 Dashboard Journey

### Trail Map

```mermaid
graph TD
    A[Dashboard Load] --> B{Data Exists?}
    B -->|No| C[Empty State ❌ DASH-01]
    B -->|Yes| D[Show Grid ❌ DASH-02]
    D --> E[Summary Cards ❌ DASH-03]
    D --> F{Filter Applied?}
    F -->|Active| G[Filtered View ❌ DASH-04]
    F -->|Clear| H[All Items ❌ DASH-05]
    D --> I[Click Item ❌ DASH-06]
    I --> J[Detail Page]
    D --> K[Export CSV ❌ DASH-07]
    D --> L{API Error?}
    L -->|Yes| M[Error State ❌ DASH-08]
```

### Checkpoints

| ID | Checkpoint | Category | Status | Last Run |
|----|------------|----------|--------|----------|
| DASH-01 | Empty state shows message | Edge Case | ❌ | - |
| DASH-02 | Grid loads with items | Happy Path | ❌ | - |
| DASH-03 | Summary cards show totals | Happy Path | ❌ | - |
| DASH-04 | Filter shows subset | Happy Path | ❌ | - |
| DASH-05 | Clear filter shows all | Happy Path | ❌ | - |
| DASH-06 | Click navigates to detail | Happy Path | ❌ | - |
| DASH-07 | Export triggers download | Happy Path | ❌ | - |
| DASH-08 | API error shows message | Error | ❌ | - |

---

## 🛢️ Wells Journey

### Trail Map

```mermaid
graph TD
    A[Wells List] --> B{Wells Exist?}
    B -->|No| C[Empty State ❌ WELL-01]
    B -->|Yes| D[Show Wells ❌ WELL-02]
    D --> E[Click Well ❌ WELL-03]
    E --> F[Well Detail]
    F --> G[Activity Chart ❌ WELL-04]
    F --> H[Edit Well ❌ WELL-05]
    H --> I[Save Changes ❌ WELL-06]
```

### Checkpoints

| ID | Checkpoint | Category | Status | Last Run |
|----|------------|----------|--------|----------|
| WELL-01 | Empty state shows message | Edge Case | ❌ | - |
| WELL-02 | Wells list loads | Happy Path | ❌ | - |
| WELL-03 | Click navigates to detail | Happy Path | ❌ | - |
| WELL-04 | Activity chart renders | Happy Path | ❌ | - |
| WELL-05 | Edit form opens | Happy Path | ❌ | - |
| WELL-06 | Save persists changes | Happy Path | ❌ | - |

---

## Trail Markers Legend

| Marker | Meaning |
|--------|---------|
| ❌ | Uncharted — checkpoint identified, not tested |
| 🔄 | Scouted — test written, not yet passing |
| ✅ | Cleared — test passing |
| ⚠️ | Unstable — flaky test, needs investigation |
| ⏭️ | Skipped — intentionally not tested |

---

## Expedition History

| Date | Scout | Expedition | Checkpoints Cleared |
|------|-------|------------|---------------------|
| - | - | - | - |

---

*Maintained by Pathfinder — Marks the trail before others follow.*

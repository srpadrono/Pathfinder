> **Note:** This is an extended example. For the minimal template, see `templates/user-journeys.md`.

# 🗺️ Trail Map — User Journeys

*Last updated: YYYY-MM-DD*

## Coverage Summary

| Journey | Coverage | Checkpoints | Last Scouted |
|---------|----------|-------------|--------------|
| Auth | 0% | 0/5 | - |
| Items | 0% | 0/8 | - |
| Settings | 0% | 0/6 | - |

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

## 📋 Items Journey

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

## ⚙️ Settings Journey

### Trail Map

```mermaid
graph TD
    A[Settings Page] --> B{Has Profile?}
    B -->|No| C[Default State ❌ SET-01]
    B -->|Yes| D[Show Profile ❌ SET-02]
    D --> E[Edit Profile ❌ SET-03]
    E --> F[Profile Form]
    F --> G[Validation ❌ SET-04]
    F --> H[Save Changes ❌ SET-05]
    H --> I[Success Message ❌ SET-06]
```

### Checkpoints

| ID | Checkpoint | Category | Status | Last Run |
|----|------------|----------|--------|----------|
| SET-01 | Default state shows placeholder | Edge Case | ❌ | - |
| SET-02 | Profile data loads | Happy Path | ❌ | - |
| SET-03 | Edit form opens | Happy Path | ❌ | - |
| SET-04 | Invalid input shows error | Error | ❌ | - |
| SET-05 | Save persists changes | Happy Path | ❌ | - |
| SET-06 | Success message appears | Happy Path | ❌ | - |

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

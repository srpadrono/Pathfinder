# Pathfinder World-Class Roadmap

A practical execution plan to turn Pathfinder into a world-class repository: high trust, low complexity, and strong engineering rigor.

## Outcomes (Success Criteria)

- Fresh clone reliability: `npm run validate` and `npm run test:all` succeed in a documented baseline setup.
- Single canonical workflow definition across all top-level docs and skill routing.
- Deterministic CI pipeline with no hidden local assumptions.
- One checkpoint state pipeline (no duplicate source-of-truth paths).
- Clear contributor model and release quality gates.

---

## Program Structure

## Epic E0 — Program Foundation (Week 1)

### PF-000: Establish roadmap governance
- **Priority:** P0
- **Owner:** Maintainer
- **Description:** Adopt this roadmap as canonical improvement backlog.
- **Acceptance Criteria:**
  - This file is linked from `README.md`.
  - A GitHub project board mirrors all epics and tasks below.

### PF-001: Define quality KPIs
- **Priority:** P0
- **Owner:** Maintainer
- **Description:** Add measurable KPIs for repo health.
- **Acceptance Criteria:**
  - KPI section added to `README.md`.
  - Baselines captured for: command pass rate, CI stability, onboarding time.

---

## Epic E1 — Canonical Workflow Contract (Weeks 1–2)

### PF-101: Create a single source-of-truth workflow spec
- **Priority:** P0
- **Owner:** Docs
- **Description:** Add `docs/architecture/canonical-workflow.md` defining phases, skills, commands, and gate files.
- **Acceptance Criteria:**
  - Canonical doc approved.
  - No conflicting phase names across docs.

### PF-102: Align `AGENTS.md`, `README.md`, and `skills/using-pathfinder/SKILL.md`
- **Priority:** P0
- **Owner:** Docs
- **Dependencies:** PF-101
- **Description:** Resolve phase/skill drift.
- **Acceptance Criteria:**
  - Skill list and process order match exactly in all three files.
  - Slash commands map to the same phase names.

### PF-103: Add docs consistency guardrail
- **Priority:** P0
- **Owner:** Tooling
- **Dependencies:** PF-101
- **Description:** Add script to validate key workflow constants across files.
- **Acceptance Criteria:**
  - `npm run validate:docs` fails when workflow terms drift.
  - CI runs this check on PR.

---

## Epic E2 — Verification and Enforcement Hardening (Weeks 2–3)

### PF-201: Refactor `verify-expedition.sh` preflight logic
- **Priority:** P0
- **Owner:** Tooling
- **Description:** Graceful, actionable preflight for missing `.pathfinder` state.
- **Acceptance Criteria:**
  - Missing files produce remediation guidance instead of opaque hard stop.
  - Script exits with clear status codes per failure class.

### PF-202: Dynamic default-branch detection
- **Priority:** P0
- **Owner:** Tooling
- **Dependencies:** PF-201
- **Description:** Replace hardcoded `main..HEAD` assumptions.
- **Acceptance Criteria:**
  - Branch detection supports `main`, `master`, and custom default branches.
  - Branch-based checks pass in single-branch local clones.

### PF-203: Verification script test harness
- **Priority:** P1
- **Owner:** QA/Tooling
- **Dependencies:** PF-201, PF-202
- **Description:** Add fixture-based tests for verification scenarios.
- **Acceptance Criteria:**
  - Test matrix includes happy path + top 5 failure modes.
  - Golden outputs captured for reproducibility.

---

## Epic E3 — Deterministic Local and CI Runs (Weeks 3–4)

### PF-301: Fix baseline script ergonomics
- **Priority:** P0
- **Owner:** Tooling
- **Description:** Ensure `lint`, `test:unit`, and `test:all` behave meaningfully in this repo.
- **Acceptance Criteria:**
  - No command fails solely due to missing expected folders.
  - Command outputs include actionable fixes.

### PF-302: Add `npm run validate` umbrella command
- **Priority:** P1
- **Owner:** Tooling
- **Dependencies:** PF-301
- **Description:** Aggregate static checks and environment checks.
- **Acceptance Criteria:**
  - Includes docs consistency, lint, type checks, script checks.
  - Used in CI and recommended in PR template.

### PF-303: Make Playwright CI self-contained
- **Priority:** P0
- **Owner:** CI
- **Description:** Start app server or provide deterministic test harness.
- **Acceptance Criteria:**
  - CI does not depend on undocumented external server.
  - Failure messages indicate whether app boot or test logic failed.

---

## Epic E4 — Checkpoint Pipeline Simplification (Weeks 4–5)

### PF-401: Choose checkpoint source of truth
- **Priority:** P0
- **Owner:** Architecture
- **Description:** Standardize on reporter output or fixture marker artifacts.
- **Acceptance Criteria:**
  - Decision record (ADR) added.
  - Non-canonical path is removed or explicitly deprecated.

### PF-402: Remove dead/duplicated checkpoint plumbing
- **Priority:** P1
- **Owner:** Tooling
- **Dependencies:** PF-401
- **Description:** Delete unused files and references.
- **Acceptance Criteria:**
  - No orphan artifacts are emitted.
  - Coverage update reads one stable schema.

### PF-403: Add schema validation for checkpoint outputs
- **Priority:** P1
- **Owner:** Tooling
- **Dependencies:** PF-401
- **Description:** Validate `test-results/checkpoints.json` before downstream scripts run.
- **Acceptance Criteria:**
  - Invalid schema fails fast with clear error message.

---

## Epic E5 — Script Reliability and Security (Weeks 5–6)

### PF-501: Add JSON schema validation for `.pathfinder/*.json`
- **Priority:** P1
- **Owner:** Tooling
- **Description:** Validate `state`, `plan`, `task`, and `report` files.
- **Acceptance Criteria:**
  - `npm run validate:pathfinder` command added.
  - Invalid state blocks report generation.

### PF-502: Harden shell scripts with static checks
- **Priority:** P1
- **Owner:** Tooling
- **Description:** Add shellcheck and strict conventions.
- **Acceptance Criteria:**
  - Shell scripts pass static analysis in CI.
  - Shared helper library used for common checks.

### PF-503: Security automation baseline
- **Priority:** P1
- **Owner:** Security
- **Description:** Add secret scanning + dependency audit policy.
- **Acceptance Criteria:**
  - CI job for secrets scanning.
  - Documented thresholds for dependency vulnerabilities.

---

## Epic E6 — DX and Productization (Weeks 6–8)

### PF-601: Add `npm run doctor`
- **Priority:** P1
- **Owner:** DX
- **Description:** One command to diagnose environment readiness.
- **Acceptance Criteria:**
  - Verifies node/playwright/hooks/env prerequisites.
  - Prints fixes for each failing check.

### PF-602: Provide deterministic demo app or mock harness
- **Priority:** P2
- **Owner:** DX
- **Description:** Make example tests runnable without external app assumptions.
- **Acceptance Criteria:**
  - New contributor can run demo suite in <10 minutes.
  - README quickstart uses deterministic path.

### PF-603: Contributor and release ops hardening
- **Priority:** P2
- **Owner:** Maintainer
- **Description:** Add CODEOWNERS, ADR template, release checklist.
- **Acceptance Criteria:**
  - New architecture decisions recorded via ADRs.
  - Release checklist used for every tagged release.

---

## Recommended GitHub Project Columns

1. **Backlog**
2. **Ready**
3. **In Progress**
4. **In Review**
5. **Blocked**
6. **Done**

## Recommended Labels

- `priority:P0`, `priority:P1`, `priority:P2`
- `type:docs`, `type:tooling`, `type:ci`, `type:security`, `type:dx`
- `risk:high`, `risk:medium`, `risk:low`

## Suggested Milestones

- **M1: Contract Integrity** — PF-101, PF-102, PF-103
- **M2: Reliable Verification** — PF-201, PF-202, PF-203
- **M3: Deterministic CI/Local** — PF-301, PF-302, PF-303
- **M4: Pipeline Simplification** — PF-401, PF-402, PF-403
- **M5: Engineering Excellence** — PF-501, PF-502, PF-503, PF-601
- **M6: Productization** — PF-602, PF-603

---

## First 10 Tickets to Open Immediately

1. PF-101
2. PF-102
3. PF-103
4. PF-201
5. PF-202
6. PF-301
7. PF-303
8. PF-401
9. PF-501
10. PF-601

These ten create the fastest path to trust, reliability, and maintainability.

## Implementation Status

- ✅ PF-101 implemented
- ✅ PF-102 implemented
- ✅ PF-103 implemented
- ✅ PF-201 implemented
- ✅ PF-202 implemented
- ✅ PF-203 initial implementation (verification preflight test harness added)
- ✅ PF-301 implemented
- ✅ PF-302 implemented
- ✅ PF-303 implemented (deterministic local demo server + Playwright webServer)
- ✅ PF-401 implemented (ADR-0001 chooses reporter output as source of truth)
- ✅ PF-402 implemented (fixture marker file emission removed)
- ✅ PF-403 initial implementation (`validate:checkpoints` schema check added)
- ✅ PF-501 initial implementation (`validate:pathfinder`)
- ✅ PF-502 initial implementation (shellcheck added to CI)
- ✅ PF-503 implemented (security workflow for npm audit + baseline secret scan)
- ✅ PF-601 implemented (`npm run doctor`)
- ✅ PF-602 implemented (deterministic demo app + default demo auth env path)
- ✅ PF-603 implemented (CODEOWNERS + ADR template + release checklist)

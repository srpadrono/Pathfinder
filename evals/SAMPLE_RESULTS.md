# Sample eval run

Real, `claude`-backed runs of this suite — including the uncomfortable parts and the
infrastructure limits. The point of an honest eval is that it surfaces genuine
weaknesses (and genuine outages) instead of a rigged "100%".

## Triggering eval — a real weakness, found and fixed

Full run: 20 queries × 3 runs, agent = Sonnet, plugin loaded via `--plugin-dir`.

```bash
python3 evals/scripts/run_triggering.py --runs 3
```

**Result (description v3.0.0 initial):**

| Metric | Value |
|--------|-------|
| Accuracy | 70% (14/20) |
| **Precision** | **100%** — never fired on a near-miss (0 false positives) |
| Recall | 40% — fired on only 4 of 10 should-trigger queries |
| Held-out test accuracy | 75% |

Precision was perfect: every unit-test / API-test / line-coverage / flaky-test
near-miss correctly stayed quiet. But recall was poor, and the misses clustered:
**mobile frameworks** (iOS/XCUITest `t02`, Flutter `t06`, RN/Detox `t08`, Espresso
`t10`), the **"write E2E tests"** framing (`t05`), and **"generate a Mermaid diagram"**
(`t04`). The web-and-journey-framed queries (`t01,t03,t07,t09`) fired.

**The fix** (the eval loop working): the `description` was rewritten to be pushier and
to name those exact framings — "find untested user flows", "audit or visualize UI/E2E
coverage", "generate E2E/UI tests", across web **and** iOS, Android, React Native,
Flutter — while keeping the negative boundary so precision is preserved. The optimizer
(`run_loop.py`) automates this same loop against a held-out split. *(Re-measuring the
post-fix recall needs another run; see "infrastructure limits" below.)*

## Output-quality A/B

Full 7-case A/B (with-skill via `--plugin-dir` vs. baseline, Opus judge). The agent
ran successfully on every case; grading is Opus-bound and was throttled by a usage
limit (below), so at the time of writing **1 of 7 cases is graded** — and even that one
is informative:

| Case | with_skill | without_skill | lift |
|------|-----------|---------------|------|
| baseline-comparison-no-remap | 67% ± 0% | 67% ± 0% | +0% |

The aggregator's auto-analysis flagged `before-after-or-delta` as **failing in *both*
arms** (0% / 0%) — i.e. neither the skilled nor the baseline run produced the
before/after delta the case asked for — and reconciled it against the case's declared
`discriminating: true` flag as a real "declared discriminating but didn't" mismatch.
That's a concrete, actionable signal about the skill's baseline-comparison flow, not a
vanity metric.

## Infrastructure limits — and an honesty guard that earned its keep

Both the triggering re-run and the Opus grading hit the account's **session usage
limit** mid-flight. A naive harness would have logged a flat **0% — which looks exactly
like the skill failing.** It isn't; the model just couldn't run. So the harness:

- **aborts loudly** on a session/usage limit or unavailable model (runners + grader),
- **excludes ungraded runs** from the benchmark instead of scoring them 0
  (`aggregate_benchmark.py` reports e.g. "24 run(s) ungraded and excluded"), and
- **resumes incrementally** — `grade_evals.py` skips already-graded runs, so grading
  completes across as many usage windows as it takes without redoing work or re-running
  the agent.

```text
$ python3 evals/scripts/grade_evals.py --run-dir evals/runs/v3-suite
  grading empty-project-no-hallucination / with_skill / run 1 ...
ABORTED: judge model unavailable (session/usage limit?)
  ...no 0% gradings were fabricated.
```

**Completing the benchmark** is therefore just re-running grading as quota frees up
(the agent transcripts are intact — no re-run needed):

```bash
python3 evals/scripts/grade_evals.py --run-dir evals/runs/v3-suite   # resumes; skips graded
python3 evals/scripts/aggregate_benchmark.py --run-dir evals/runs/v3-suite
```

## What this demonstrates

1. The suite **really runs the agent with the skill** (loaded via `--plugin-dir`; a
   prior version mistakenly copied skills to `.claude/skills/`, which headless
   `claude -p` ignores — so its A/B was secretly baseline-vs-baseline).
2. It **finds real weaknesses** (40% triggering recall in identifiable framings; a
   journey case that fails its before/after expectation in both arms) and drives fixes.
3. It is **honest under failure**: outages abort loudly and grading resumes, rather
   than masquerading as skill results.

That is the difference from the rigged harness this replaced, which reported "100%" no
matter what — including when its own scripts errored.

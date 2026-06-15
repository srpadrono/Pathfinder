# Sample eval run

Real, `claude`-backed runs of this suite — including the uncomfortable parts. The
point of an honest eval is that it surfaces genuine weaknesses (and genuine
infrastructure limits) instead of a rigged "100%".

## Triggering eval — a real weakness, found and fixed

Full run: 20 queries × 3 runs, agent = Sonnet, plugin loaded via `--plugin-dir`.

```bash
python3 evals/scripts/run_triggering.py --runs 3
```

**Before** (description v3.0.0 initial):

| Metric | Value |
|--------|-------|
| Accuracy | 70% (14/20) |
| **Precision** | **100%** — never fired on a near-miss (0 false positives) |
| Recall | 40% — fired on only 4 of 10 should-trigger queries |
| Held-out test accuracy | 75% |

Precision was perfect: every unit-test / API-test / line-coverage / flaky-test
near-miss correctly stayed quiet. But recall was poor, and the misses clustered
clearly: **mobile frameworks** (iOS/XCUITest `t02`, Flutter `t06`, RN/Detox `t08`,
Espresso `t10`), the **"write E2E tests"** framing (`t05`), and **"generate a Mermaid
diagram"** (`t04`). The web-and-journey-framed queries (`t01,t03,t07,t09`) fired.

**The fix** (this is the eval loop working): the `description` was rewritten to be
pushier and to name those exact framings — "find untested user flows", "audit or
visualize UI/E2E coverage", "generate E2E/UI tests", across web **and** iOS, Android,
React Native, Flutter — while keeping the negative boundary ("Not for unit tests,
API/backend tests, or debugging a single existing test") so precision is preserved.
The optimizer (`run_loop.py`) automates this same loop against a held-out split.

**After**: re-measurement was started but the run hit the account's **session usage
limit** mid-flight (see below), so the post-fix number isn't reported here yet — it
will be re-run after the limit resets.

## Output-quality A/B — and an honesty guard that earned its keep

The full 7-case A/B suite (with-skill via `--plugin-dir` vs. baseline, Opus judge)
ran the agent successfully on all cases, but the **Opus judge hit the session usage
limit**, so every grading came back empty. A naive harness would have reported a flat
**0% — which looks exactly like the skill failing.** It isn't; the model just couldn't
run. The harness now detects this and refuses to fabricate a result:

```text
$ python3 evals/scripts/aggregate_benchmark.py --run-dir evals/runs/v3-suite
ERROR: no graded runs in evals/runs/v3-suite. 28 run(s) were ungraded
(judge unavailable / no parseable output) — these are NOT counted as 0%.
Re-grade with grade_evals.py.
```

`run_evals.py`, `run_triggering.py`, and `grade_evals.py` all abort with a clear
message on a session/usage limit or an unavailable model, and `aggregate_benchmark.py`
excludes ungraded runs instead of scoring them 0. A model outage is never reported as
a skill failure. (The agent transcripts and artifacts from that run are intact, so a
re-grade needs no re-run.)

## What this demonstrates

1. The suite **really runs the agent with the skill** (loaded via `--plugin-dir`; a
   prior version mistakenly copied skills to `.claude/skills/`, which headless
   `claude -p` ignores — so its A/B was secretly baseline-vs-baseline).
2. It **finds real weaknesses** (40% recall, concentrated in identifiable framings)
   and drives a targeted fix to the highest-leverage field.
3. It is **honest under failure**: infrastructure limits abort loudly rather than
   masquerading as skill results.

That is the difference from the rigged harness this replaced, which reported "100%"
no matter what — including when its own scripts errored.

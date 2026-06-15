# Pathfinder Evals

A real, honest evaluation suite — modeled on Anthropic's [skill-creator](https://github.com/anthropics/skills) methodology and OpenAI's [Testing Agent Skills with Evals](https://developers.openai.com/blog/eval-skills) pattern.

> **Why this matters.** Earlier versions of this repo shipped graders that returned
> `passed: true` unconditionally and "ran" the bundled Python scripts instead of the
> agent — then reported "100% pass rate." That measured nothing. This suite replaces
> it. Nothing here fakes a verdict; layers that can't reach a model say so and exit.

There are two kinds of eval, because a skill can fail in two different ways.

## 1. Output-quality evals (`output_quality.json`) — *does the skill do the job well?*

Each case is run **A/B**: once with the Pathfinder skills available to the agent
(`with_skill`) and once with a plain agent (`without_skill`). Both produce a
transcript and a tree of files; an **LLM-as-judge** (default: Opus) grades each
expectation against the rubric in [`agents/grader.md`](agents/grader.md):

- **No partial credit** — each expectation passes or fails.
- **Burden of proof on passing** — uncertain ⇒ fail.
- **Outcomes over gestures** — "I detected Playwright" with no evidence fails.
- **Every verdict cites the transcript or an artifact.**

Each case runs **N times** (default 3) so we can report **mean ± stddev** and the
**`with_skill − without_skill` lift**. `aggregate_benchmark.py` then flags:

- **Non-discriminating assertions** — pass about equally with and without the skill,
  so they don't measure the skill's value (sharpen or drop them).
- **High-variance cases** — possibly flaky.

Each case declares which expectations it *expects* to be discriminating
(`"discriminating": true`); `aggregate_benchmark.py` reconciles that claim against the
observed data and reports **declared-vs-observed mismatches** (declared discriminating
but didn't, or discriminated despite being declared non-discriminating).

## 2. Triggering evals (`triggering.json`) — *does the skill fire at the right time?*

20 realistic queries: ~10 that **should** trigger Pathfinder and ~10 deliberate
**near-misses** that share keywords (test, coverage, journey) but need a different
tool — unit tests, API tests, flaky-test debugging, line-coverage, CI setup.
`run_triggering.py` runs each query against Claude Code with the skills installed,
detects whether a skill actually fired (from the stream-json tool events), and
scores at a 0.5 trigger-rate threshold. It reports accuracy / precision / recall
plus a **held-out test split** (stratified, deterministic) so a description that's
been over-tuned to a few phrasings is caught.

## Running

```bash
# CI-safe (no model, no network): schema + structural validation
python3 evals/scripts/validate_suite.py          # npm run eval:validate

# Plumbing smoke test (no model): proves the runner → artifact → grade pipeline
python3 evals/scripts/run_evals.py --backend mock --runs 1   # npm run eval:smoke

# Full output-quality run (needs the `claude` CLI logged in, or ANTHROPIC_API_KEY)
python3 evals/scripts/run_evals.py --backend claude --runs 3
python3 evals/scripts/grade_evals.py             # LLM judge (Opus by default)
python3 evals/scripts/aggregate_benchmark.py     # benchmark.md + benchmark.json

# Triggering eval
python3 evals/scripts/run_triggering.py --runs 3 # npm run eval:trigger
```

Models are pinned (default agent `sonnet`, judge `opus`) so headless runs don't
inherit an unavailable session model. Override with `--model`, `--backend codex`,
or `PATHFINDER_EVAL_MODEL` / `PATHFINDER_EVAL_JUDGE_MODEL`. Run artifacts land in
`evals/runs/` (git-ignored).

**Honest under failure.** If the backend hits a session/usage limit or an unavailable
model, the runners and grader **abort with a clear message** rather than silently
recording a 0% — a model outage is not a skill failure. `aggregate_benchmark.py`
likewise excludes ungraded runs instead of scoring them 0. (Transcripts and artifacts
survive, so you can re-grade without re-running the agent.)

## What CI runs

CI has no model access, so it gates every PR on the parts that don't need one:
`validate_suite.py` (schema + structure of the committed datasets) and the
harness unit tests in [`tests/test_eval_harness.py`](../tests/test_eval_harness.py)
(aggregation math, variance + non-discriminating analysis, trigger thresholds,
the stratified split). The agent-graded runs above are run on demand by a maintainer
with credentials. This mirrors Anthropic's own note that there is no built-in way to
run skill evals in CI — so we're explicit about which layer runs where.

## A real result (and why honest evals are uncomfortable)

See [`SAMPLE_RESULTS.md`](SAMPLE_RESULTS.md) for an actual `claude`-backed run. The
short version: on the simplest mapping task, a strong modern model scores 100%
**without** the skill too — so the lift is +0% and the analyzer flags those
expectations as non-discriminating. That's the suite working as intended: it tells
you where the skill genuinely changes behavior (signature visualization, schema-
conformant artifacts, workflow discipline, before/after tracking) versus where the
base model already suffices. The old rigged harness could never have told you that.

## Files

| Path | Purpose |
|------|---------|
| `output_quality.json` | A/B output-quality cases + discriminating expectations |
| `triggering.json` | Should / should-not-trigger queries (with near-misses) |
| `schema/*.schema.json` | JSON Schemas the datasets are validated against |
| `agents/grader.md` | LLM-judge rubric (system prompt) |
| `files/` | Fixture inputs staged into each case's temp project |
| `scripts/` | `validate_suite`, `run_evals`, `grade_evals`, `aggregate_benchmark`, `run_triggering` |
| `runs/` | Generated run artifacts (git-ignored) |

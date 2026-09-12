# Plan

| Wave | Orders | Verification | Checkpoint SHA | Status |
|---|---|---|---|---|
| 0 | 0.1 Architect: interface stubs | Chief ran `python -c "import fxconv.rates, fxconv.cache, fxconv.cli"` + read every stub | bf20206 | passed |
| 1 | 1.1 rates.py, 1.2 cache.py, 1.3 cli.py (3 parallel, disjoint files) | Chief ran full `pytest -q` (56 passed) + read full diff + grepped for suppression patterns | 694a0cd | passed |
| 2 | 2.1 Security Auditor, 2.2 Red Team QA (parallel, read-only) | Chief independently reproduced each report's top finding live | 32493cd | passed |
| 3 | 3.1 rates.py fix, 3.2 cache.py fix, 3.3 cli.py fix (3 parallel, disjoint files) | Chief ran full `pytest -q` (75 passed) + live CLI spot checks + boundary check | 4fbf470 | passed |

## Burn (qualitative — no token metering is exposed to the Chief, so this is estimated per wave from each order's own usage report rather than independently measured)
- Wave 0: 1 agent, ~105k subagent tokens, 20 tool calls, ~4.5 min.
- Wave 1: 3 agents in parallel, ~98k/114k/102k subagent tokens, largest single cost of the mission — includes the disclosed sabotage-refusal detour on order 1.2.
- Wave 2: 2 agents in parallel, ~103k/125k subagent tokens — Red Team's live-API probing (finding the real 403 bug) was the most valuable single order in the mission relative to its cost.
- Wave 3: 3 agents in parallel, ~97k/162k/102k subagent tokens — order 3.2 (cache.py) ran longest because it chased down a real Windows `os.replace()` quirk under concurrency testing.
- Sabotage-injection experiment (Chief-authored, not a wave): no subagent cost — done directly by the Chief on an isolated branch.

## Post-mission
Definition of done (MISSION.md) fully met at checkpoint 4fbf470: `python -m fxconv USD EUR 100`
prints a real live conversion (86.27 EUR verified), `pytest -q` passes 75/75 including an
explicit zero-call-on-cache-hit assertion and a TTL-expiry assertion, malformed currency
codes and non-finite/negative amounts produce a clean one-line error with no traceback,
no third-party dependencies were added, and path traversal is rejected by construction
(allowlist-then-path) and confirmed by both the Security Auditor and the Chief.

One sabotage-injection experiment was run on an isolated `sabotage-experiment` branch
(not merged) — see `reports/sabotage-experiment-wave.md` in this mission's report
directory for the full writeup and evidence.

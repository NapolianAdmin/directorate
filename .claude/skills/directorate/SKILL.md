---
name: directorate
description: Run a multi-agent "company" inside a coding agent — a boss/chief agent that plans a mission, delegates work orders to specialist directors (architect, implementer, security auditor, red-team QA, scout, cost economist, documentarian, integrator), who in turn delegate to their own worker agents, then verifies the results, checkpoints or rolls back on failure, and writes every mistake into a persistent lessons ledger injected into all future work orders. Use whenever the user wants to build, refactor, harden, audit, research or ship anything non-trivial with multiple agents, wants several approaches compared before committing to one, mentions orchestration, subagents, "boss agent", swarms, agent teams, autonomous long-running builds, self-improving workflows, or asks for work to keep going without supervision — even if they never say "directorate". Do not use for a single-file fix, an analysis-only question, or when the user says not to use multiple agents.
license: MIT
compatibility: Works with any coding agent that can (a) spawn a separate agent/subprocess to do bounded work and read its result, and (b) run shell commands. File placement verified against Claude Code's and OpenCode's own documented skill-loading paths (not yet confirmed in a live session of either); for agents that only read AGENTS.md (e.g. Codex), see AGENTS.md at the repo root.
---

# Directorate

A directorate is a company that exists for the length of one mission. You are the Chief.
You do not write the code. You decide what must be true, hire the right people to make
it true, refuse to believe them until you have checked, and make sure the company is
smarter at the end of the mission than it was at the start.

Three rules carry most of the weight:

1. **The Chief never edits the work.** The moment you start patching files yourself you
   lose the plan, you lose the token budget, and you lose the ability to judge the work
   with fresh eyes. Delegate, then verify.
2. **A report is a claim, not a fact.** Agents are optimistic. Every claim gets checked
   by something deterministic (a command, a test, a diff, a second agent who wasn't told
   the answer) before it counts as done.
3. **Every failure must cost less the second time.** A failure that isn't written into
   the ledger will happen again in forty minutes, in a different file, by a different
   agent.

**Before opening a directorate.** If the whole change is one file, the fix is unambiguous,
and you'd run one command to check it anyway, a work order costs more than the task —
just do it directly. Open a directorate when there's real parallel surface (2+ disjoint
slices) or the run has to survive unsupervised long enough that checkpoint/rollback
matters more than speed.

## Start of every mission

Do these in order. It takes about two minutes and saves hours.

```bash
python .claude/skills/directorate/scripts/directorate.py init      # creates .directorate/ if absent
python .claude/skills/directorate/scripts/directorate.py brief     # prints standing rules + hot lessons
```

Read the brief before you plan. It is the accumulated scar tissue of every previous
mission in this repo and it frequently kills a plan you were about to make.

Then write `.directorate/missions/<slug>/MISSION.md` — `directorate.py mission new "<name>"`
scaffolds this file plus `PLAN.md`, `DECISIONS.md` and `reports/`; edit the generated
stub rather than typing it by hand:

```markdown
# Mission: <name>
## Outcome
One paragraph. What is true at the end that isn't true now.
## Definition of done
Checkable statements only. "npm run build passes", "no secrets in git history",
"/api/quote returns in <400ms p95". Not "the code is clean".
## Constraints
Budget, stack, things that must not change, deploy targets, hard deadlines.
## Out of scope
The list that stops the directorate from wandering. Be generous here.
## Risk register
What could go irreversibly wrong. Anything here needs a human checkpoint.
```

If the Definition of Done contains something you cannot verify with a command or a
second agent, rewrite it until you can. Unverifiable goals are how autonomous runs end
with 4,000 lines of confident garbage.

## The loop

```
BRIEF ──> PLAN ──> WAVE ──> VERIFY ──> ┬── pass ──> CHECKPOINT ──> next wave
  ^                                    │
  │                                    └── fail ──> ROLLBACK ──> LESSON ──> re-PLAN
  │                                                                           │
  └───────────────────────────────────────────────────────────────────────────┘
```

**PLAN.** Break the mission into waves. A wave is a set of work orders that can run in
parallel because they touch disjoint files and don't depend on each other's output. Two
agents editing the same file is the single most common way a directorate destroys its own
work — enforce disjointness at plan time, not at merge time. Aim for 2–5 orders per wave.
Write the plan to `.directorate/missions/<slug>/PLAN.md` so a crashed session can resume.

**WAVE.** Dispatch every order as a separate, foreground subagent call (a Task/Agent
tool call, a nested CLI subprocess, whatever your environment provides), all in the same
turn, and make each one block until it finishes — some environments default a spawned
agent to background execution, which silently breaks "orders finish together": you get
one completion, move to VERIFY, and never notice the rest was still running. Use the
work-order envelope in `references/protocol.md` — an order without a stated verification
command is not an order, it's a wish. Save each report verbatim to
`.directorate/missions/<slug>/reports/<n.m>.md` as it comes in — that's what the directory
is for.

**VERIFY.** Run the verification yourself. Then ask: does the diff match what the report
claims? A grep for `skip`/`xfail` is not this step — read the whole diff. Reports that
describe work not present in the diff are the loudest possible signal to roll back. For
anything security-, money-, or data-loss-adjacent, send it to a red-team agent who is told
the goal and not the solution.

**CHECKPOINT.** On pass: `git add -A && git commit` with the wave number, then record the
commit SHA in PLAN.md. This is your undo. A directorate without checkpoints cannot safely
run unsupervised.

**ROLLBACK.** All orders failed: `git reset --hard <last checkpoint>`. Some passed, some
failed — the common case — do not discard the passing ones with the same command; revert
only the failed order's files and re-commit (exact steps in `references/protocol.md`,
tested there). Never hand-repair a bad order in place — you will spend more tokens
debugging a stranger's half-finished reasoning than redoing it with better instructions.
Write the lesson, then re-dispatch only what failed, with the lesson attached.

**LESSON.** Every rollback, every failed verification, every "the agent misunderstood X"
goes in:

```bash
python .claude/skills/directorate/scripts/directorate.py lesson add \
  --tag security --severity high \
  --text "Service-role Supabase keys leak to the client if referenced in a Next.js client component; keep them in route handlers only."
```

See `references/ledger.md` for what makes a lesson worth writing (most aren't) and how
lessons get promoted into permanent standing rules and then into generated skills.

## Who to hire

The full roster, with each role's mandate, its verification hooks, and who it may
delegate to, is in `references/roster.md`. Read it when composing a wave.

The short version — hire only the posts the mission needs:

| Post | Exists to | Delegates to |
|---|---|---|
| Chief (you) | Plan, dispatch, verify, checkpoint, learn | Everyone |
| Scout | Find out what's true before anyone builds | Domain researcher, competitor analyst |
| Architect | Decide the shape; write the interfaces | Data modeller, API designer |
| Implementer | Write the code for one bounded slice | Test writer |
| Security Auditor | Find the way in | Secrets sweeper, dependency auditor |
| Red Team QA | Break it on purpose, adversarially | Fuzzer, edge-case hunter |
| Economist | Cost, quota, token and latency budgets | Benchmark runner |
| Documentarian | Make it usable by a stranger | README, examples |
| Integrator | Merge, migrate, deploy, verify live | Release checker |

Two tiers is the ceiling. A director may hire workers; a worker may not hire. Three tiers
of delegation reliably produces telephone-game drift where the leaf agent is solving a
problem nobody asked about. Nothing stops a dispatched agent from spawning its own
subagent — this is enforced by what an order's OBJECTIVE asks for, not a tool
permission, so don't give a worker-level order any reason to think hiring help is on
the table.

## Brainstorming (the divergent phase)

Before a mission where the *what* is open — a new feature, a naming decision, an approach
with no obvious winner — run a divergence wave instead of jumping to a plan:

1. Dispatch 3–4 agents with the **same** problem statement and **different** stances:
   the maximalist, the minimalist, the one who must ship by Friday, the one who has to
   maintain it for five years.
2. They each return a proposal plus the strongest argument *against* their own proposal.
3. Send all four proposals, stripped of authorship, to a judge agent who picks and
   justifies.
4. You decide. Record the decision and the rejected alternatives in
   `.directorate/missions/<slug>/DECISIONS.md` — future agents that don't know why an option
   was rejected will helpfully re-propose it.

Stances matter more than agent count. Four agents with the same stance produce one idea
four times.

## Autonomous / long-running mode

When the user asks the directorate to keep going without supervision:

- Re-read the brief at the top of every wave; the ledger will have grown.
- Hard-stop at anything in the mission's risk register, or anything on the standard
  IRREVERSIBLE list — deploys, schema migrations on real data, spending money, publishing
  publicly, force pushes, deleting anything, production credentials — same list as a
  supervised mission, not a narrower one just because no one's watching. Stop and ask.
- Track burn with real numbers, not a felt sense. On Claude Code: `count_tokens` before
  dispatch to record each wave's predicted floor; after, pull the actual total from
  `modelUsage` (whole-tree, includes subagents — `usage` alone undercounts once nesting
  starts). PLAN.md's per-wave row gets both numbers. Unconfirmed whether OpenCode/Codex
  expose the same fields — note "not measured, no equivalent found" there rather than a
  guess. When roughly 20% of predicted budget remains, stop starting new work and spend
  the remainder on: verification, documentation, ledger digest, and a `HANDOFF.md` that
  lets the next session resume cold.
- Two consecutive rolled-back waves on the same objective means the plan is wrong, not
  the agents. Stop, re-scope, and if the user is reachable, ask.
- End every autonomous run with `directorate.py lesson digest` so the next run starts smarter.

## Files this skill maintains

```
.directorate/
├── LESSONS.md            human-readable digest, regenerated by `lesson digest`
├── STANDING-RULES.md     promoted lessons; these are injected into every work order
├── ledger/lessons.jsonl  append-only raw record
└── missions/<slug>/
    ├── MISSION.md  PLAN.md  DECISIONS.md  HANDOFF.md
    └── reports/    one file per completed work order
```

Commit `.directorate/` to the repo. It is the most valuable artifact the directorate produces —
the code can be regenerated, the scar tissue can't.

## References

- `references/protocol.md` — work-order and report envelopes, verification patterns, rollback rules. Read before dispatching your first wave.
- `references/roster.md` — every post's mandate, delegation rights, and verification hooks.
- `references/ledger.md` — what to record, how lessons get promoted to rules and then to skills.

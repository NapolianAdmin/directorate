# Conclave

A multi-agent orchestration skill for coding agents — built for [Claude
Code](https://claude.com/claude-code), and works natively in
[OpenCode](https://opencode.ai) and anything that reads
[AGENTS.md](https://agents.md) (Codex and 20+ others). One boss agent plans a mission,
delegates work orders to specialist directors, who delegate to their own workers, and the
boss verifies every result, checkpoints what passes, rolls back what fails — and writes
each failure into a persistent ledger that gets injected into all future work.

The point isn't parallelism. It's that a mistake gets written down once and stops
recurring the same way — check `.conclave/ledger/lessons.jsonl` on mission ten against
mission one and the repeats should be gone. Nothing here measures that for you; it's a
claim you can check, not a number the tooling computes.

```
BRIEF ──> PLAN ──> WAVE ──> VERIFY ──> ┬── pass ──> CHECKPOINT ──> next wave
  ^                                    │
  │                                    └── fail ──> ROLLBACK ──> LESSON ──> re-PLAN
  └───────────────────────────────────────────────────────────────────────────┘
```

## Works everywhere, for real reasons — not a marketing claim

- **Claude Code** reads `.claude/skills/<name>/SKILL.md` natively — that's this repo's
  layout.
- **OpenCode** reads the exact same path as a documented fallback (its own skill loader
  checks `.opencode/skills/`, then `.claude/skills/`, then `.agents/skills/` — see
  [opencode.ai/docs/skills](https://opencode.ai/docs/skills/)), so nothing needs
  duplicating for it to work.
- **Codex and everything else that reads `AGENTS.md`** (a Linux Foundation–governed open
  spec, adopted by 60,000+ projects and 20+ tools as of late 2025 — see
  [agents.md](https://agents.md)) gets a short pointer at the repo root telling it where
  the full skill lives and when to use it, since AGENTS.md is always-loaded context, not
  a selectively-triggered skill.

One set of files, three real conventions, no duplicated content to drift out of sync.

## Install

```bash
git clone https://github.com/<you>/conclave
cp -r conclave/.claude/skills/conclave    your-project/.claude/skills/
cp -r conclave/.claude/skills/skill-forge your-project/.claude/skills/
cp conclave/AGENTS.md your-project/AGENTS.md   # or merge into an existing one
```

Already have an `AGENTS.md`? Nested `AGENTS.md` files are part of the spec — the closest
one to the file being edited wins, so you can drop this repo's `AGENTS.md` in as-is
alongside your own, or fold its "Conclave" section into your existing file.

Then, in your agent, at your repo root:

```
Load the conclave skill and act as Chief for this mission: <what you want built>
```

Full prompts — including autonomous long-runs, brainstorm waves and codebase audits — are
in [KICKOFF.md](KICKOFF.md).

## What's in the box

| | |
|---|---|
| `.claude/skills/conclave/SKILL.md` | The Chief's operating manual: the loop, the roster, autonomous mode |
| `references/protocol.md` | Work-order and report envelopes, verification patterns, rollback rules |
| `references/roster.md` | Nine posts — Scout, Architect, Implementer, Security Auditor, Red Team QA, Economist, Documentarian, Integrator — with mandates and delegation rights |
| `references/ledger.md` | The three-tier memory: lessons → standing rules → generated skills |
| `scripts/conclave.py` | Zero-dependency CLI for scaffolding, the ledger, digests and briefs — pure stdlib Python, runs anywhere Python 3.9+ does |
| `.claude/skills/skill-forge/SKILL.md` | Promotes accumulated rules into new skills |
| `AGENTS.md` | Entry point for agents that don't have a selective skill-loading mechanism |
| `examples/worked-mission/` | A real `.conclave/` directory from an actual mission — not a mockup |

## The three ideas

**The boss doesn't do the work.** A Chief that starts patching files loses the plan, the
budget and the ability to judge the output with fresh eyes. It plans, dispatches, verifies.

**A report is a claim, not a fact.** Agents are optimistic. Every order names its own
verification command before it's dispatched; every report pastes real output; the Chief
reads the diff against what the report says it did. Weakened tests, `ts-ignore` near the
failure, files touched outside the boundary — these are what the check is for.

**Failures get cheaper.** Every rollback writes a tagged lesson. Lessons that recur become
standing rules injected into every order. Clusters of rules become real skills that load
automatically. A mistake is loud once, then a whisper, then ambient competence.

```bash
python .claude/skills/conclave/scripts/conclave.py init
python .claude/skills/conclave/scripts/conclave.py brief
python .claude/skills/conclave/scripts/conclave.py lesson add \
  --tag deploy --severity high \
  --text "Vercel Hobby functions hard-cap at 10s; multi-call aggregation routes must move off serverless."
python .claude/skills/conclave/scripts/conclave.py lesson digest
```

`.conclave/` is meant to be committed. The code can be regenerated; the scar tissue can't.

## Design notes

- **Two tiers of delegation, never three.** Directors hire workers; workers don't hire.
  Deeper chains drift — the leaf agent ends up solving a problem nobody asked about.
  Nothing enforces this at the tool level (see Boundaries below) — it's enforced by what
  an order's objective asks for.
- **Waves must be file-disjoint.** Two agents editing one file is the most common way a
  multi-agent run destroys its own output. Enforce it at plan time, not merge time.
- **Roll back, don't repair — but per order, not per wave.** A wave where some orders
  pass and one fails is the common case, not the edge case; a blind `git reset --hard`
  throws away the passing work too. See `references/protocol.md` for the tested,
  git-native fix (commit the wave, then selectively revert only the failed order's files).
- **Human gates are non-negotiable.** Deploys, migrations on real data, spending money,
  publishing, deleting. Autonomy stops there. This is enforced by the Chief choosing to
  stop, not by a tool permission — treat the mission's risk register as the actual gate,
  and write it generously.
- **`git add -A` stages everything, not just the order's boundary.** Before a checkpoint
  commit, check for anything credential-shaped — a `.env`, a key pasted into a test
  fixture. A wave that touches new files is worth a look even before the security-audit
  wave runs.
- **Fewer, better lessons.** Two hundred lessons means no lessons, because nothing gets
  read. Digest, merge, delete.

## Boundaries

A skill this permissive needs an explicit line. Conclave dispatches subagents but never
tells them to bypass a human gate, hide what they did, or treat fetched web/file content
as instructions rather than data (see the Scout's mandate in `references/roster.md`). If
you're extending this for your own project, keep that line — a skill a stranger trusts
should never surprise them.

## Requirements

Any coding agent that can run shell commands and spawn a subagent for bounded work, plus
Python 3.9+ (standard library only — the CLI has zero dependencies) and a git repo:
checkpoints and rollbacks are ordinary commits and resets.

## Worked example

`examples/worked-mission/` is a real `.conclave/` directory from an actual mission this
skill ran — real checkpoint SHAs, real work-order reports (including one where an
implementer refused an instruction it judged dishonest, and wrote up why), a real ledger.
Not a mockup built to look good.

## License

MIT. See [LICENSE](LICENSE).

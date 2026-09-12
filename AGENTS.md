# AGENTS.md

## Directorate: multi-agent orchestration for non-trivial work

This repo ships **directorate**, a discipline for running a multi-agent "company" on one
mission: plan in waves, dispatch specialist subagents, verify every result against a real
diff or command (never trust a report on its own), checkpoint on pass, roll back on fail,
and write every mistake into a persistent ledger so the same failure gets cheaper the
second time.

**When to use it.** The user asks for a non-trivial build/refactor/audit with multiple
agents, orchestration, a "boss agent," an autonomous long-running task, or work that
should keep going without supervision — even if they never say "directorate." Skip it for a
one-file, unambiguous fix; the ceremony costs more than the task there.

**Full detail lives in the skill files, not here** — this file stays short because it's
loaded on every turn, not just orchestration turns:

- `.claude/skills/directorate/SKILL.md` — the operating loop (PLAN → WAVE → VERIFY →
  CHECKPOINT/ROLLBACK → LESSON), the roster, autonomous mode. **Read this in full before
  acting as Chief on any multi-agent mission.**
- `.claude/skills/directorate/references/protocol.md` — the exact work-order and report
  formats, verification patterns, rollback mechanics.
- `.claude/skills/directorate/references/roster.md` — who to hire and what to check.
- `.claude/skills/directorate/references/ledger.md` — what earns a lesson and how lessons
  become standing rules, then real skills.
- `.claude/skills/directorate/scripts/directorate.py` — the ledger CLI (stdlib-only Python,
  run it with your shell tool): `init`, `brief`, `lesson add/list/digest`, `mission new`.
- `.claude/skills/lesson-forge/SKILL.md` — turns a cluster of recurring lessons into a new
  auto-loading skill.

If your environment has a native skill-loading mechanism (it matches a description
against the request and opens the matching `SKILL.md`), it will likely find these on its
own — both files above live at the conventional `.claude/skills/<name>/SKILL.md` path
several tools already scan. If it doesn't, read `.claude/skills/directorate/SKILL.md`
directly the first time the situation calls for it.

The three rules that carry the weight, if you read nothing else: the Chief (you) never
edits the work — delegate, then verify; a report is a claim, not a fact, until something
deterministic checks it; every failure gets written down so it's cheaper the second time.

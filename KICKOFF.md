# Kickoff prompts

Paste one of these into your coding agent (Claude Code, OpenCode, Codex, or anything
else that's read `AGENTS.md`) at the repo root. The first is the one you want most of
the time.

---

## 1. Run a mission

```
Load the `directorate` skill and act as Chief for this mission.

MISSION: <one paragraph — what must be true when this is finished>
STACK: <languages, frameworks, hosting, anything already committed to>
CONSTRAINTS: <budget, free tier only, deadline, what must not change>
OUT OF SCOPE: <what you must not touch>
IRREVERSIBLE (human gate required): deploys, schema migrations on real data, spending
money, publishing publicly, force pushes, deleting anything.

Do this in order, and don't skip the boring steps — they're the ones that make the rest
cheap:

1. Run `directorate.py init` and `directorate.py brief`. Read the brief before planning; it
   contains what previous missions in this repo learned the hard way.
2. Write MISSION.md. Every line of the definition of done must be something you can
   verify with a command or an artifact I can inspect. Rewrite anything vague until it's
   checkable, then show it to me before you start building.
3. Plan the mission in waves. Each wave is a set of orders that can run in parallel
   because they touch disjoint files. Write PLAN.md.
4. Run each wave: dispatch every order as a separate, foreground agent call in the same
   turn (not backgrounded — see references/protocol.md for why) using the work-order
   envelope from references/protocol.md. Every order names its own verification command
   and its file boundary.
5. Verify yourself. Run the commands. Read the *whole* diff against what each report
   claims — a keyword grep for ts-ignore/skip/empty-catch is a pre-filter, not the check;
   it will not catch a deleted or weakened assertion, which is the more realistic failure.
6. All orders pass: commit as a checkpoint, record the SHA in PLAN.md, move to the next
   wave. Some fail: revert only the failed orders' files and re-commit (steps in
   references/protocol.md) — a full `git reset --hard` discards the passing orders' work
   too. Don't hand-repair a bad order.
7. Record a lesson for every rollback and every verification that should have caught
   something and didn't.
8. Before the final wave: Security Auditor and Red Team QA in parallel, then fix the
   findings that have a real reproduction.
9. End with `directorate.py lesson digest`, and forge any cluster of 4+ related rules into
   a skill using the `lesson-forge` skill.

You are the Chief. Don't write the implementation yourself — the moment you start
patching files you lose the plan and the ability to judge the work with fresh eyes.
Stop and ask me at anything in the irreversible list.

Start with step 1 and show me MISSION.md before building anything.
```

---

## 2. Autonomous long run

Use when you want it to keep going while you're away. Point it at a mission that's
already been scoped.

```
Load the `directorate` skill. Continue mission <slug> autonomously until the definition of
done is met or the token budget runs low.

Per wave: re-read `directorate.py brief` (the ledger grows as you go), dispatch, verify,
checkpoint or roll back, record lessons.

Hard stops — do not proceed, leave a note and wait. Same list as any other mission's
IRREVERSIBLE gate, not a narrower one just because no one's watching: deploys, schema
migrations on real data, spending money, publishing publicly, force pushes, deleting
anything, touching production credentials — plus, specific to running unattended:
- anything in the mission's risk register (if it's not generous enough to cover the
  actual mission, that's a bug in the mission, not a reason to proceed)
- two consecutive rolled-back waves on the same objective (that means the plan is wrong,
  not the agents — stop and re-scope)

Budget: when roughly 20% remains, stop starting new work. Spend the rest on verification,
docs, `lesson digest`, and a HANDOFF.md complete enough for a cold session to resume:
where the mission stands, what the last checkpoint is, what the next wave was going to
be, and what you'd do differently.
```

---

## 3. Brainstorm before committing

Use when the *what* is genuinely open.

```
Load the `directorate` skill and run a divergence wave on this before we plan anything:

QUESTION: <the open decision>
CONTEXT: <constraints, stack, who it's for>

Dispatch four agents with the same problem and different stances: the maximalist, the
minimalist, the one who must ship by Friday, and the one who has to maintain it for five
years. Each returns a proposal plus the strongest argument against their own proposal.

Strip the authorship, send all four to a judge agent, and bring me the judge's pick with
its reasoning and the three rejected options with the reason each was rejected. Write it
all to DECISIONS.md — I don't want to re-litigate this in three weeks.
```

---

## 4. Audit an existing codebase

```
Load the `directorate` skill. This repo already exists; I want it hardened, not rebuilt.

Wave 1, in parallel, read-only — nobody changes a line of code:
- Security Auditor: secrets in code, git history and client bundles; authz gaps;
  injection surfaces; anything logging a credential or PII
- Red Team QA: reproductions only, no opinions
- Economist: cost at expected load, free-tier ceilings and what happens at the ceiling,
  p95 latency, N+1 queries

Then bring me the findings ranked by exploitability × blast radius, each with a real
reproduction. Findings without a reproduction get downgraded, not fixed — I'm not
spending the budget on phantoms.

I'll pick what to fix. Then run fix waves with checkpoints, and re-run Red Team against
the fixes.
```

---

## Tips

- Give the Chief a real definition of done. The single biggest quality difference between
  a good run and a bad one is whether "done" was checkable at the start.
- Let it roll back. The instinct to rescue a half-broken wave costs more than redoing it.
- Commit `.directorate/` — it's the part that compounds.
- The ledger is only as good as your willingness to record unflattering things in it.

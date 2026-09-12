# Protocol

How the Chief talks to directors, how directors talk to workers, and how anything gets
marked done. The envelopes below are deliberately rigid — agents drift, and a rigid
envelope is what lets you notice the drift in one glance instead of reading 600 lines of
prose.

---

## The work order

Every dispatched agent gets exactly this. No freeform "please help with the auth stuff".

```markdown
POST: <role from roster.md>
WAVE: <n>  ORDER: <n.m>
MISSION: <one line — the outcome the whole directorate is chasing>

OBJECTIVE
<One outcome. If you need the word "and", it is two orders.>

CONTEXT YOU NEED
<Paths, prior decisions, interfaces already agreed. Be specific. An agent that has
to go hunting will read forty files and burn your budget finding three.>

STANDING RULES
<paste .directorate/STANDING-RULES.md>

RELEVANT LESSONS
<paste output of: directorate.py brief --tags <tags for this order>>

BOUNDARIES
- You may edit: <explicit file list or glob>
- You may not edit: everything else. If you believe another file must change, stop
  and report it as a BLOCKER instead of editing it.
- You may not: install packages / change schema / touch CI / commit  <delete as applies>

VERIFICATION
<The exact command(s) that prove this order is done. The agent runs these before
reporting. If you cannot name one, the order is not well-formed — fix the order.>

BUDGET
<rough ceiling: files touched, or minutes, or "keep it under ~200 lines of diff">

REPORT FORMAT
<paste the report envelope below>
```

**Why the edit-boundary matters more than it looks.** Parallel waves only stay parallel
if the file sets are disjoint. One agent that "helpfully" refactors a shared util silently
invalidates every other agent's work in the wave, and you won't find out until the merge.
An agent that reports a needed change instead of making it costs you one extra order; an
agent that makes it costs you the wave.

---

## The report envelope

```markdown
STATUS: DONE | PARTIAL | BLOCKED | FAILED
ORDER: <n.m>

WHAT I CHANGED
- <file>: <one line, what and why>

VERIFICATION OUTPUT
<paste the actual command output, not a summary of it>

WHAT I DID NOT DO
<scope you left on the floor, and why>

RISKS AND UNKNOWNS
<what you're unsure about; what a reviewer should look at hardest>

BLOCKERS
<things outside your boundary that must change; name the file and the reason>

LESSON CANDIDATE
<optional: a mistake you made or a trap you hit that the next agent should be
warned about. One sentence, generalised beyond this specific file.>
```

Pasted verification output is the load-bearing field. "Tests pass" is a claim; twelve
lines of test runner output is evidence. Agents that summarise instead of pasting are
usually agents that didn't run it.

---

## Verification patterns

Pick the cheapest one that actually discriminates.

**Deterministic (always prefer).** Build, typecheck, lint, test, a curl with a
grep, a script that asserts. These cost almost nothing and cannot be talked into lying —
but they only catch what they're written to catch. Deleting three passing assertions (no
`skip`, no `xfail`, nothing suppressed — just removed) leaves the full test suite green.
Deterministic checks are necessary, never sufficient on their own.

**Diff-vs-claim (the load-bearing check — do this one for real, every time).** Read the
actual diff, the whole thing, against WHAT I CHANGED. A keyword grep for `skip` / `xfail` /
`@ts-ignore` / `catch {}` is a fast pre-filter, not a substitute — it will not catch a
deleted or weakened assertion, which is the more realistic failure than an added
suppression marker. So also check: files changed outside the boundary; the assertion
*count* in a changed test (fewer assertions with no failing test is a red flag even with
no skip marker); config changes nobody asked for; and any new credential-shaped string
(a long random token, a `sk-`/`AKIA`/`ghp_`-style prefix, anything assigned to a name
containing `KEY`/`SECRET`/`TOKEN`) in a file about to be committed.

**Adversarial second agent.** Give a fresh agent the objective and the artifact, not the
solution, and ask it to break the artifact or find what's missing. Use for security,
auth, money, data migrations, and anything a user can type into.

**Blind judge.** Two competing implementations, authorship stripped, one judge picks.
Use when correctness isn't binary — API shape, copy, UX, naming.

**Human gate.** Anything irreversible: production deploys, schema migrations on real
data, spending money, publishing publicly, force pushes, deleting anything.

A verification that passes on both a correct and a broken implementation isn't a
verification. If you're unsure, deliberately break the thing and check the verification
notices.

---

## Rollback rules

- Checkpoint = a commit after a wave passes verification. Record the SHA in PLAN.md.
- **All orders in a wave pass:** `git add -A && git commit`. This is the checkpoint.
- **All orders fail:** `git reset --hard <last checkpoint>` and re-plan the whole wave.
  Do not hand-repair.
- **Some orders pass, some fail (the common case, not an edge case) — revert per order,
  not per wave, and never commit the failing content in the first place:** `git reset
  --hard` discards every order's diff, including the ones that passed, because it resets
  the whole working tree. Do this instead, using only ordinary git — and note step order:
  verify *before* anything is committed, so a failing order's content (including any
  secret it introduced) never enters git history at all, not even transiently:
  1. Once every order reports, do **not** commit yet. Verify each order, in the dirty
     working tree, against its own boundary and verification command (diff-vs-claim,
     tests, the credential-string check above).
  2. For each order that failed, revert only its files back to the last checkpoint —
     straight from the uncommitted tree, no intermediate commit needed:
     `git checkout HEAD -- <failing order's file list>`.
  3. Commit what's left: `git add -A && git commit -m "wave <n> checkpoint (order <n.m>
     reverted)"`. This is the checkpoint. Passing orders' work survives; the failed
     order's files were never anything but the prior checkpoint's content, in git history
     or out of it.
  4. Re-dispatch only the failed order, with the lesson and its failed report attached —
     not the whole wave.
  A committed-then-reverted secret is still reachable in git history via reflog until
  explicitly rewritten; verifying before committing avoids the problem instead of cleaning
  up after it.
- Never roll back past a checkpoint that contains passing work from an unrelated wave.
- `git reset --hard` (and the selective `git checkout` above) only undo the working tree.
  Neither undoes a side effect outside it — an API call already made, a migration already
  applied, a package already installed. If an order in the wave had one, note it before
  resetting; a clean `git status` after rollback does not mean the wave's effects are gone.
- If the repo is dirty and you're unsure what's salvageable even at per-order granularity,
  stash to a branch (`git switch -c directorate/wreck-<wave>`) before resetting. It costs
  nothing and occasionally saves an hour.
- After every rollback, write the lesson **before** re-planning. Doing it afterwards
  means writing it from memory of a plan you've already replaced, and the lesson comes
  out vague.

---

## Dispatch hygiene

- **The mechanism, concretely:** dispatch every order in the wave as a separate subagent
  call — a Task/Agent tool call, a nested CLI subprocess, whatever your environment
  provides — all in the same turn, and make every call block until it finishes (do not
  let orders run in the background). Some environments default subagents to background
  execution, which breaks "orders finish together" silently: you get one completion,
  move on to VERIFY, and never notice the rest of the wave was still running.
- 2–5 orders per wave. Beyond that you can't hold the merge in your head.
- No two orders share a writable file. If they must, they're sequential, not parallel.
- A "post" (roster.md) is a role brief pasted into the order, not a named agent type —
  dispatch every order as the same general-purpose agent kind; POST is what tells it who
  to be, not a system-level permission. Nothing stops a dispatched agent from spawning its
  own subagent, so the two-tier rule is enforced by what an order's OBJECTIVE asks for,
  not by a tool restriction — do not give a worker-level order any reason to think hiring
  help is on the table.
- Re-dispatching after a rollback: include the lesson and the failed attempt's report in
  the new order. Agents given only the original order will reproduce the original bug
  with striking fidelity.
- A BLOCKED report is good news arriving early. Treat it as a successful order.

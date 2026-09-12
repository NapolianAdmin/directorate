# Lessons

_Regenerated 2026-09-11T19:32:26+00:00 — 4 recorded, 4 distinct._

## Promotion candidates

Recurred or high severity. Decide whether each belongs in STANDING-RULES.md, then trim it from the tag sections below.

- **[high] ×1** git reset --hard to the last checkpoint destroys ALL uncommitted modifications to already-tracked files in the wave, good and bad alike, because checkpoints are wave-granular not order-granular; only brand-new untracked files survive, incidentally, not by design. Protocol needs a partial-wave policy (e.g. stage/commit passing orders individually before evaluating the rest) or this destroys good work every time a wave is mixed pass/fail.
- **[high] ×1** Agent/Task tool dispatch defaults to background execution in some environments; 'dispatch the whole wave in one turn' silently breaks if orders run backgrounded, since the Chief gets one completion and moves to VERIFY without the rest of the wave finishing. Force foreground/blocking execution per order.

## agents

- [medium] Dispatching 8-10 background review/trigger-test agents in one batch can trip a session-wide rate limit and fail all of them at once; staggering into smaller batches (3-4) recovers cleanly. Prefer smaller parallel batches over maximum parallelism when agents don't depend on each other's timing.

## dispatch

- [high] Agent/Task tool dispatch defaults to background execution in some environments; 'dispatch the whole wave in one turn' silently breaks if orders run backgrounded, since the Chief gets one completion and moves to VERIFY without the rest of the wave finishing. Force foreground/blocking execution per order.

## docs

- [medium] A skill's own file-listing (e.g. 'Files this skill maintains') can promise a directory gets populated (reports/, one file per work order) with no paired instruction anywhere in the actual loop steps telling an agent to do it - found only by trying to build a real worked example and discovering reports/ was empty after a full mission. Any 'this skill maintains X' claim needs a step that actually produces X.

## process

- [high] git reset --hard to the last checkpoint destroys ALL uncommitted modifications to already-tracked files in the wave, good and bad alike, because checkpoints are wave-granular not order-granular; only brand-new untracked files survive, incidentally, not by design. Protocol needs a partial-wave policy (e.g. stage/commit passing orders individually before evaluating the rest) or this destroys good work every time a wave is mixed pass/fail.
- [high] Agent/Task tool dispatch defaults to background execution in some environments; 'dispatch the whole wave in one turn' silently breaks if orders run backgrounded, since the Chief gets one completion and moves to VERIFY without the rest of the wave finishing. Force foreground/blocking execution per order.
- [medium] A skill's own file-listing (e.g. 'Files this skill maintains') can promise a directory gets populated (reports/, one file per work order) with no paired instruction anywhere in the actual loop steps telling an agent to do it - found only by trying to build a real worked example and discovering reports/ was empty after a full mission. Any 'this skill maintains X' claim needs a step that actually produces X.
- [medium] Dispatching 8-10 background review/trigger-test agents in one batch can trip a session-wide rate limit and fail all of them at once; staggering into smaller batches (3-4) recovers cleanly. Prefer smaller parallel batches over maximum parallelism when agents don't depend on each other's timing.

## rollback

- [high] git reset --hard to the last checkpoint destroys ALL uncommitted modifications to already-tracked files in the wave, good and bad alike, because checkpoints are wave-granular not order-granular; only brand-new untracked files survive, incidentally, not by design. Protocol needs a partial-wave policy (e.g. stage/commit passing orders individually before evaluating the rest) or this destroys good work every time a wave is mixed pass/fail.

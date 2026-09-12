# Changelog

## Comparison update + first live-session verification

Two separate follow-ups after the initial public hardening pass: an honest comparison
against two more real projects, and — for the first time — an actual live test of the
one claim that had previously been checked against documentation only.

### Added: superpowers and GateGuard to the comparison

[obra/superpowers](https://github.com/obra/superpowers) (285,465 stars, confirmed via the
GitHub API directly, not an agent's summary) is the largest project in this space and
wasn't previously named in the README's comparison table — a gap flagged by this
project's own earlier research. Added as a full column: credited where it's genuinely
ahead (enforced red-green-refactor TDD, 14 supported agent harnesses), gapped honestly
where its own README doesn't describe a mechanism (no cross-session memory, no described
partial-wave rollback). [zunoworks/gateguard](https://github.com/zunoworks/gateguard) is a
different category — a Claude Code `PreToolUse` hook, not an orchestration framework — so
it's addressed in a new FAQ entry instead of a table row: it mechanically enforces its
gate at the runtime level (this exact hook gated this project's own Bash/Edit/Write calls
throughout its development), where directorate's human gates are enforced by the Chief
choosing to stop. Stated as a real gap with a pairing recommendation, not smoothed over.

### Confirmed live: the skill actually auto-triggers in Claude Code

Every previous claim about Claude Code compatibility had been checked against Claude
Code's own documentation, never against an actual session — stated plainly in the README
as an open gap. Closed one part of that gap for real: a fresh, independent,
non-interactive `claude -p` session (no prior context, "directorate" never mentioned) was
given a copy of this repo's own published skill files plus a natural task description
built from the skill description's own trigger vocabulary — "a boss agent that plans the
work, delegates to specialist sub-agents, verifies what they report, checkpoints, rolls
back on failure, keeps going without supervision." The session correctly identified and
loaded the `directorate` skill and quoted its trigger description back verbatim, matching
the published `SKILL.md` exactly.

What this confirms: the description field does what it claims — a real Claude Code
session matches natural task language to it without the skill being named. What it
doesn't confirm: a second, deeper test — having that same live session actually execute
`directorate.py init`/`brief` as its first real action — was attempted and stopped after
hitting a legitimate permission boundary (`acceptEdits` mode doesn't cover Bash execution,
and escalating further was itself blocked by the outer environment's own permission
classifier). Not routed around; the CLI script itself was already verified independently,
multiple times, via direct invocation (see "Checked and found already correct" below), so
the residual gap is small: whether a live agent reliably executes the literal bash block
`SKILL.md` already instructs it to run, which it had just quoted back correctly.

OpenCode and Codex remain unconfirmed live — only Claude Code was tested this pass.

## Cross-platform hardening pass

This package started as a Claude-Code-specific skill, was generalized for Claude Code,
OpenCode, and AGENTS.md-based tools (Codex and 20+ others), then went through a real
adversarial review before public release: four independent agents — a Scout doing live
primary-source research, a Skeptic, a First-Time User (specifically an OpenCode user),
and an Adversary — each reviewing the package cold, in parallel, without seeing each
other's findings. What follows is what they found and what changed because of it.

### Renamed: conclave → directorate, skill-forge → lesson-forge

The single highest-confidence finding, raised independently by multiple reviewers: both
original names collide with real, live, unrelated public repositories.

- **`conclave`** collided with `tommasinigiovanni/conclave` — a real, live, Apache-2.0,
  9-star Claude Code skill with the identical name, doing a genuinely different thing
  (multiple LLMs debate and critique each other anonymously, vs. this package's
  boss-plus-directors-plus-workers-plus-ledger model). Same name, same category
  (multi-agent Claude Code skill), different mechanism — exactly the shape of collision
  that confuses users and hurts discoverability for both projects.
- **`skill-forge`** collided with at least four independent public repos doing
  conceptually similar "turn knowledge into a skill" work
  (`bhoon716/skill-forge`, `WilliamSaysX/skill-forge`, `nekocode/skill-forge`,
  `AgriciDaniel/skill-forge`).

Both replacement names (`directorate`, `lesson-forge`) were checked against GitHub before
being finalized and came back clear. "Directorate" also fits the package's own content
better than "conclave" did — the roster is literally built around "specialist directors,"
and a directorate (a company's board of directors) is a closer real-world match for "boss
plus directors plus workers" than a conclave (a private meeting to elect a pope) ever was.

This was a full rename, not a relabeling: directory names, the CLI script
(`conclave.py` → `directorate.py`), the environment variable (`CONCLAVE_ROOT` →
`DIRECTORATE_ROOT`), the on-disk state directory (`.conclave/` → `.directorate/`,
including inside the worked example — both its file contents and the actual directory
name), and every prose mention across every file. Nothing publicly depends on the old
names yet, which made this the only free moment to fix it — a rename after publication
would break every existing installation.

### Fixed: a secret could survive a rollback in git history

The Adversary traced a real gap in the wave-level rollback mechanism added in an earlier
pass: the documented procedure for "some orders pass, some fail" committed the whole
wave's content as a `WIP wave <n>` commit *before* running verification, then selectively
reverted the failing order's files and re-committed. That sequencing meant a secret
introduced by the failing order was written into git history by the first commit — the
later selective revert fixes the working tree and the new checkpoint, but the earlier WIP
commit object is still reachable via `git reflog` until someone explicitly rewrites
history, and nothing in the docs said to do that.

Fixed by reordering, not patching around it: verify every order in the wave *before*
anything is committed, revert a failing order's files straight from the dirty working
tree (a plain checkout of the failing paths, which needs no prior commit to work), then
commit only what's left. Tested end to end in a scratch repo before writing it into
`references/protocol.md` — confirmed a planted fake secret in the reverted file never
appears anywhere in git history under the new procedure.

### Fixed: overclaimed cross-platform verification

Two related overclaims, both caught by the Skeptic re-reading the package's own claims
against its own (still in-progress) verification mission:

- The `compatibility` frontmatter field said "Tested with Claude Code and OpenCode's
  native SKILL.md loaders." No live session of either tool had actually run this skill —
  only the documented file-placement conventions had been checked. Reworded to say
  exactly that: verified against documentation, not yet confirmed live.
- README described OpenCode's skill discovery as checking `.opencode/skills/`, `then`
  `.claude/skills/`, `then` `.agents/skills/` — implying a strict priority/fallback
  chain. The Scout re-fetched OpenCode's own docs twice, independently, specifically
  hunting for fallback/priority language, and found none — the actual documented
  behavior is that OpenCode scans all three locations together while walking up to the
  git worktree root, and requires skill names to stay unique across whichever exist.
  The interoperability claim itself was correct; the "checks X, then Y" framing overstated
  what the primary source says. Reworded accordingly.
- Separately, the Skeptic found that Codex is reported to have its own native skill
  loader (scanning `.agents/skills/`), distinct from its AGENTS.md support — meaning
  "Codex and everything else that reads AGENTS.md" undersold what's actually true
  (Codex has two ways to find a skill, not one) while also overselling this repo's
  coverage of it (only the AGENTS.md path is actually populated; `.agents/skills/`
  doesn't have a copy). This is flagged as an open, only-partially-verified gap rather
  than fixed outright — the finding came through a research tool's summarization layer
  with an explicit caveat that it should be re-confirmed against a raw source or a real
  Codex session before being treated as fully settled.

### Fixed: smaller issues found by the same pass

- README's "Nine posts" line named eight — the Chief wasn't counted in its own list.
- Two worked-example reports pasted a placeholder-looking path inside real pytest
  output — something pytest never actually prints, undercutting the example's own "not a
  mockup" claim. Replaced with an explicit elision marker, which reads as intentional
  redaction instead of a forgotten template string.
- This mission's own working files were sitting untracked at the repo root, relying on
  the discipline of "never `git add` this" to keep them out of what ships. The Adversary
  correctly pointed out that's not a technical control — it already contained a local
  machine path and a private aside, one `git add -A` away from being published. Moved
  entirely outside the repository instead of merely left untracked.

### Checked and found already correct

Not everything flagged turned out to be a real problem — recorded here so the review
trail is honest about what didn't need fixing, not just what did:

- The autonomous-mode hard-stop list is consistent, word-for-word in substance, across
  `SKILL.md` and `KICKOFF.md` — no drift introduced by the cross-platform generalization.
- The Scout-content prompt-injection guard in `roster.md` (treat fetched page text as
  data, never as an instruction to follow) survived the generalization intact.
- All checkpoint SHAs and cumulative test counts referenced across the worked example's
  `PLAN.md` and its nine reports are internally consistent and add up correctly.
- `license`/`compatibility` frontmatter fields cannot break Claude Code's local skill
  loader — confirmed directly against Claude Code's own docs: unrecognized fields are
  ignored without error locally, and both fields are within the six-field allowlist
  enforced only at packaging/upload time, which this local-use skill never goes through.
- The CLI remains genuinely stdlib-only and needed zero code changes to be
  cross-platform-portable — it was always just a Python script invoked via a shell tool,
  which every one of the target platforms has.

### What's still open

- Codex's own native `.agents/skills/` discovery path (separate from AGENTS.md) is not
  currently populated with a copy of this skill — the AGENTS.md pointer is the only
  confirmed path for Codex today. Revisit once the underlying finding is re-verified
  against a raw source or an actual Codex session.
- OpenCode and Codex are still unconfirmed in a live session — only Claude Code's
  auto-trigger has now been tested for real (see "Confirmed live" above). Every
  OpenCode/Codex claim is still checked against documentation only.
- The live Claude Code test confirmed triggering, not a full mission end to end — no
  live session has yet run a real wave (dispatch, verify, checkpoint/rollback) start to
  finish. The CLI commands underneath each step are independently verified; the
  live-agent behavior of actually calling them in sequence during a real mission isn't.

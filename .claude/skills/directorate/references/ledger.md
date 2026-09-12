# The Ledger

This is the part that makes a directorate worth more on its tenth mission than its first.
Everything else here is orchestration; this is the memory.

## The pipeline

```
mistake ──> lesson (jsonl)  ──seen 3×or high severity──> standing rule ──cluster of 4+──> generated skill
             recalled by tag       injected into              injected into            loaded automatically
             into work orders      every work order           every work order         by Claude Code
```

Three tiers, because injecting everything into everything is how you burn a context
window on advice that doesn't apply.

---

## Tier 1 — lessons

Written at the moment of failure, tagged, stored append-only in
`.directorate/ledger/lessons.jsonl`, recalled by tag into work orders. Tag matching is exact
after lowercasing — `deploy` and `deployment` are different tags and never recall each
other. Run `lesson list` and reuse an existing tag before inventing a new one.

```bash
python .claude/skills/directorate/scripts/directorate.py lesson add \
  --tag deploy --tag vercel --severity high \
  --text "Vercel Hobby serverless functions hard-cap at 10s; any route doing multi-call aggregation must move to a long-running host or be split."
```

**What earns a lesson.** A wasted wave. A rollback. A verification that passed on broken
code. A platform constraint discovered the hard way. A recurring misunderstanding in
agent reports. A decision that was re-litigated because nobody wrote down why it was
rejected.

**What doesn't.** A one-off typo. Anything the language/framework docs say plainly.
Anything phrased as "be careful" or "remember to be thorough" — generic diligence advice
is noise that makes agents skim past the specific lessons that matter.

**How to phrase one.** Generalise one level above the incident, keep the concrete trigger,
state the consequence.

- Bad: "Fix the bug in quote.ts."
- Bad: "Always write better error handling."
- Good: "Free-tier upstream APIs return 200 with an error body rather than a non-2xx
  status; check the payload shape, not just `res.ok`."

One sentence. Two if the second one is the fix.

---

## Tier 2 — standing rules

`.directorate/STANDING-RULES.md`. These go into **every** work order regardless of tag, so
the bar is high: roughly a dozen rules total, never more than ~25.

A lesson is promoted when it has recurred three times, or when it is severity `high` and
would affect any agent in the repo. `directorate.py lesson digest` flags candidates; you
decide and promote — promotion is a judgement call, not a counter. A `high` lesson
promotes on its *first* occurrence, and severity is a free-text flag any agent sets with
no rubric — so before promoting, trace it back to the mission/wave it came from and
re-derive why it's true yourself. A lesson you can't trace to a real incident doesn't get
promoted, no matter what severity it was filed at; a standing rule is read by every future
order, so a wrong one is worse than none.

Rules are written as directives with a reason attached, because agents follow a rule they
understand and route around one they don't:

```markdown
- Never reference a service-role key outside a server route handler — Next.js will
  bundle it into the client build and it ships to every visitor.
- Treat a 200 from a free-tier provider as unverified; check the payload shape.
- Do not modify a failing test to make it pass. Report it as a BLOCKER.
```

Rules go stale. When a rule's underlying constraint disappears (you left the free tier,
you dropped the framework), delete it. Stale rules quietly teach agents that the rules
file is decorative.

---

## Tier 3 — generated skills

When four or more standing rules cluster around one domain — deployment on this stack,
this project's data-access patterns, its design system — that cluster has outgrown a
bullet list. Promote it into a real skill under `.claude/skills/learned/<domain>/SKILL.md`
so Claude Code loads it automatically whenever the domain comes up, and remove the
now-redundant bullets from STANDING-RULES.md.

Use the `lesson-forge` skill in this repo to do the promotion — it handles the frontmatter,
the description that actually triggers, and the trimming of the source rules.

This is the whole point of the three tiers: a mistake is loud once, becomes a whisper in
the relevant orders, then becomes ambient competence that nobody has to think about.

---

## Digest and recall

```bash
directorate.py lesson digest          # regenerate LESSONS.md, surface promotion candidates
directorate.py brief                  # standing rules + top recent lessons (start of mission)
directorate.py brief --tags security  # rules + lessons for one order's domain
directorate.py lesson list --tag deploy --limit 20
```

Run `digest` at the end of every mission and at the end of every autonomous run. It
deduplicates near-identical lessons, counts recurrences, and tells you what's ready to be
promoted. Without it the ledger grows into a swamp within about three missions and agents
stop reading it.

---

## Anti-patterns worth naming

- **Logging the run instead of the lesson.** The ledger is not a diary. "Wave 3 failed"
  helps nobody; "the reason wave 3 failed" helps everybody.
- **Hoarding.** Two hundred lessons means no lessons, because nothing gets read.
  Digest, merge, delete.
- **Lessons about agents rather than the domain.** "The implementer was careless" is not
  actionable. "Orders that don't name the verification command come back unverified" is.
- **Never promoting.** If nothing has become a standing rule after several missions,
  either you're not recording real failures or you're not running digest.

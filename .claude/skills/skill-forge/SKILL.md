---
name: skill-forge
description: Turn accumulated project knowledge into a new coding-agent skill file that loads itself automatically next time the topic comes up — not a memory note you have to ask for, a standing capability. Write it from a cluster of standing rules, lessons, a repeated workflow, or a correction the user keeps having to make. Use this skill whenever a conclave mission ends with lessons worth keeping, whenever the user wants a correction or preference to stick permanently instead of being repeated — "make this a skill", "remember how to do this", "stop making that mistake", "stop telling me the same thing every time" — or whenever you notice the same instruction being given for the third time. Also use when editing, splitting, or retiring an existing skill in .claude/skills/.
license: MIT
compatibility: Works with any coding agent that loads skills by matching a description against the current request — tested with Claude Code and OpenCode's native SKILL.md loaders.
---

# Skill Forge

The ledger remembers mistakes. This turns memory into competence — a mistake stops being
something agents are warned about and becomes something they simply don't make, because
the knowledge is loaded before they start.

Forge a skill when one of these is true:

- Four or more standing rules cluster around one domain (deployment on this stack, this
  project's data access patterns, its design system, its API conventions).
- The same workflow has been performed three times with the same shape.
- The user has corrected the same class of output more than twice.
- A mission produced a genuinely reusable procedure, not just a result.

Don't forge for a single rule — that belongs in STANDING-RULES.md, where it costs three
lines instead of a file. The threshold matters: a directory of thin skills is worse than
a short rules file, because each one competes for triggering attention.

## Writing the skill

```
.claude/skills/learned/<domain>/
└── SKILL.md
    ├── frontmatter: name + description
    └── body: the actual knowledge
```

**The description is the whole triggering mechanism.** The agent decides whether to open
a skill from its description alone, and the common failure is under-triggering — a skill
that exists and never loads. So state what it does *and* the situations that should
summon it, including phrasings that don't use the skill's own vocabulary.

- Weak: "Deployment knowledge for this project."
- Strong: "How this project deploys — Vercel frontend, Render Python service, Supabase,
  GitHub Actions cron. Use whenever the user mentions deploying, shipping, env vars,
  build failures, cold starts, cron jobs, free-tier limits or 'why is prod different',
  even if they don't name the platform."

**The body** should be specific enough to be wrong if the project changes. Real paths,
real commands, real constraints, the actual gotcha and what it costs. Generic advice
that would apply to any project is filler — it dilutes the useful parts and trains
agents to skim.

Structure that works:

```markdown
## The shape          <- how this part of the system is put together
## Do it like this    <- the procedure, imperative, with real commands
## Traps              <- the specific failures, each with its symptom
## When this is wrong <- the conditions under which this skill is stale
```

That last section is unusual and worth keeping. A skill that can't tell you when it has
expired will confidently mislead an agent six months from now.

## After forging

1. Delete the source rules from `.conclave/STANDING-RULES.md` — they're now loaded by the
   skill, and duplicating them means every work order carries text that's already in
   context.
2. Note the promotion in `.conclave/LESSONS.md` so the trail is visible.
3. Test the trigger: start a fresh session, ask something that *should* summon it in the
   user's natural phrasing, and check it loads. If it doesn't, the description is the
   problem, not the body. Widen it with the phrasings a real person would use.

## Retiring a skill

Skills go stale silently, which is the dangerous way to go stale. When a skill's "when
this is wrong" conditions are met — the platform changed, the pattern was abandoned —
delete it. Keeping a stale skill is worse than having none, because agents trust it.

## Boundaries

Forge skills that encode knowledge and procedure. Never write a skill that hides what it
does from the person running it, that embeds credentials, or that instructs agents to
bypass review, verification or human gates. A skill is read by a stranger who trusts it;
it should contain nothing that would surprise them if described out loud.

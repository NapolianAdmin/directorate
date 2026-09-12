# Standing rules

Injected into every work order. Keep this list short — roughly a dozen entries, never
more than ~25. Each rule is a directive plus the reason it exists, because an agent that
understands a rule follows it and an agent that doesn't routes around it.

Promote a lesson here when it has recurred 3+ times or is high severity and
repo-wide. Delete rules whose underlying constraint has gone away.

- Do not modify or skip a failing test to make a build pass — report it as a BLOCKER.
- Stay inside the file boundary stated in the work order; report needed changes elsewhere
  instead of making them, or you invalidate every parallel order in the wave.
- Paste real verification output in reports, never a summary of it.

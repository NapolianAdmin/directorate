# Contributing

This is a same-day, single-author project — there's real value in outside eyes on it.

## Reporting a gap or a bug

Open an issue. The most useful report names the file and line, what you expected, what
actually happened, and — if it's a claim in the README or a skill file — whether you
checked it against a live session or just the docs. This project tries hard to only claim
what's been verified; if you find a claim that isn't, that's a real bug in the docs, not
just a nitpick.

## Proposing a change

Small, focused PRs over large ones. If you're changing `SKILL.md`, keep the reasoning
here in mind:

- Every instruction should be falsifiable — something an agent can actually check, not
  generic advice ("be careful", "remember to be thorough").
- `SKILL.md` stays close to ~200 lines. If a change needs more room, it probably belongs
  in a `references/` file instead.
- No new dependencies. The CLI (`scripts/directorate.py`) is stdlib-only Python 3.9+ on
  purpose — that's what makes the install footprint git + Python + nothing else.
- If you're adding a claim about how Claude Code, OpenCode, or Codex actually behaves,
  say what you verified it against (documentation vs. a live session) — see
  `CHANGELOG.md` for the standard this repo tries to hold itself to.

## Testing a change

There's no test suite to run — the closest thing is `examples/worked-mission/`, a real
`.directorate/` directory from an actual mission. If you change `protocol.md` or
`roster.md`, the honest test is running a small real mission with the change and checking
the reports it produces, not just reading the diff.

## License

MIT. By contributing, you agree your contribution is provided under the same license.

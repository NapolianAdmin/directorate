#!/usr/bin/env python3
"""conclave.py — scaffolding and the lessons ledger for the Conclave skill.

Standard library only, no install step. Run from the repo root.

    python .claude/skills/conclave/scripts/conclave.py init
    python .claude/skills/conclave/scripts/conclave.py brief [--tags a,b] [--limit N]
    python .claude/skills/conclave/scripts/conclave.py lesson add --text "..." --tag x [--severity high]
    python .claude/skills/conclave/scripts/conclave.py lesson list [--tag x] [--limit N]
    python .claude/skills/conclave/scripts/conclave.py lesson digest
    python .claude/skills/conclave/scripts/conclave.py mission new "<name>"
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# A plain Windows console isn't UTF-8 by default; the em dashes in RULES_SEED
# and elsewhere below would otherwise mojibake or raise UnicodeEncodeError.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8")
        except (OSError, ValueError):
            pass


def _find_root() -> Path:
    """$CONCLAVE_ROOT if set; else the git repo root; else cwd.

    Resolving to cwd alone means running from a subdirectory silently
    scaffolds or reads a second, disconnected .conclave/ instead of the
    repo's real one.
    """
    override = os.environ.get("CONCLAVE_ROOT")
    if override:
        return Path(override).resolve()
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip()).resolve()
    except (OSError, subprocess.SubprocessError):
        pass
    return Path(".").resolve()


ROOT = _find_root()
BASE = ROOT / ".conclave"
LEDGER = BASE / "ledger" / "lessons.jsonl"
DIGEST = BASE / "LESSONS.md"
RULES = BASE / "STANDING-RULES.md"
MISSIONS = BASE / "missions"

SEVERITIES = ("low", "medium", "high")
PROMOTION_THRESHOLD = 3

RULES_SEED = """# Standing rules

Injected into every work order. Keep this list short — roughly a dozen entries, never
more than ~25. Each rule is a directive plus the reason it exists, because an agent that
understands a rule follows it and an agent that doesn't routes around it.

Promote a lesson here when it has recurred {threshold}+ times or is high severity and
repo-wide. Delete rules whose underlying constraint has gone away.

- Do not modify or skip a failing test to make a build pass — report it as a BLOCKER.
- Stay inside the file boundary stated in the work order; report needed changes elsewhere
  instead of making them, or you invalidate every parallel order in the wave.
- Paste real verification output in reports, never a summary of it.
""".format(threshold=PROMOTION_THRESHOLD)


# ---------------------------------------------------------------- helpers

def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60] or "mission"


def read_lessons() -> list[dict]:
    if not LEDGER.exists():
        return []
    out = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"warn: skipping malformed ledger line: {line[:80]}", file=sys.stderr)
    return out


def norm(text: str) -> str:
    """Loose normalisation used to spot near-duplicate lessons.

    Punctuation collapses to whitespace so "free-tier" and "free tier" match.
    """
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()


def require_init() -> bool:
    if BASE.exists():
        return True
    print("No .conclave/ found. Run: conclave.py init", file=sys.stderr)
    return False


# ---------------------------------------------------------------- commands

def cmd_init(_args) -> int:
    # Checkpoints are ordinary git commits (see protocol.md), not files -- no
    # checkpoints/ directory is scaffolded here on purpose.
    for d in (BASE / "ledger", MISSIONS):
        d.mkdir(parents=True, exist_ok=True)
    LEDGER.touch(exist_ok=True)
    if not RULES.exists():
        RULES.write_text(RULES_SEED, encoding="utf-8")
    if not DIGEST.exists():
        DIGEST.write_text("# Lessons\n\n_Empty. Run `conclave.py lesson digest`._\n",
                          encoding="utf-8")
    print(f"conclave ready at {BASE}")
    print("  STANDING-RULES.md  ledger/lessons.jsonl  missions/")
    print("Commit .conclave/ — the scar tissue is the valuable part.")
    return 0


def cmd_lesson_add(args) -> int:
    if not require_init():
        return 1
    text = args.text.strip()
    if len(text) < 15:
        print("Lesson too short to be useful. Say what breaks and why.", file=sys.stderr)
        return 1

    tags = sorted({t.strip().lower() for raw in args.tag for t in raw.split(",") if t.strip()})
    existing = read_lessons()
    dupe = next((l for l in existing if norm(l.get("text", "")) == norm(text)), None)

    entry = {
        "ts": now(),
        "text": text,
        "tags": tags,
        "severity": args.severity,
        "mission": args.mission,
        "wave": args.wave,
    }
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"recorded [{args.severity}] {', '.join(tags) or 'untagged'}")
    if dupe:
        print("  ^ near-identical lesson already in the ledger — this one has now "
              "recurred. Consider promoting it to STANDING-RULES.md.")
    return 0


def cmd_lesson_list(args) -> int:
    if not require_init():
        return 1
    lessons = read_lessons()
    if args.tag:
        want = {t.strip().lower() for t in args.tag.split(",")}
        lessons = [l for l in lessons if want & set(l.get("tags", []))]
    lessons = lessons[-args.limit:]
    if not lessons:
        print("(no lessons yet)")
        return 0
    for l in lessons:
        tags = ",".join(l.get("tags", [])) or "-"
        print(f"[{l.get('severity','medium'):<6}] ({tags}) {l['text']}")
    return 0


def cmd_lesson_digest(_args) -> int:
    if not require_init():
        return 1
    lessons = read_lessons()
    if not lessons:
        print("(nothing to digest)")
        return 0

    # cluster near-duplicates
    clusters: dict[str, dict] = {}
    for l in lessons:
        key = norm(l.get("text", ""))
        c = clusters.setdefault(key, {"count": 0, "entry": l, "tags": set(), "sev": "low"})
        c["count"] += 1
        c["tags"].update(l.get("tags", []))
        if SEVERITIES.index(l.get("severity", "low")) > SEVERITIES.index(c["sev"]):
            c["sev"] = l.get("severity", "low")
            c["entry"] = l

    by_tag: dict[str, list[dict]] = defaultdict(list)
    for c in clusters.values():
        for t in (sorted(c["tags"]) or ["untagged"]):
            by_tag[t].append(c)

    candidates = [c for c in clusters.values()
                  if c["count"] >= PROMOTION_THRESHOLD or c["sev"] == "high"]

    lines = ["# Lessons", "",
             f"_Regenerated {now()} — {len(lessons)} recorded, "
             f"{len(clusters)} distinct._", ""]

    if candidates:
        lines += ["## Promotion candidates", "",
                  "Recurred or high severity. Decide whether each belongs in "
                  "STANDING-RULES.md, then trim it from the tag sections below.", ""]
        for c in sorted(candidates, key=lambda c: -c["count"]):
            lines.append(f"- **[{c['sev']}] ×{c['count']}** {c['entry']['text']}")
        lines.append("")

    for tag in sorted(by_tag):
        lines += [f"## {tag}", ""]
        for c in sorted(by_tag[tag], key=lambda c: -c["count"]):
            mark = f" ×{c['count']}" if c["count"] > 1 else ""
            lines.append(f"- [{c['sev']}]{mark} {c['entry']['text']}")
        lines.append("")

    DIGEST.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {DIGEST} — {len(clusters)} distinct lessons across {len(by_tag)} tags")
    if candidates:
        print(f"{len(candidates)} promotion candidate(s). Review the top of LESSONS.md.")
    counts = Counter(t for l in lessons for t in l.get("tags", []))
    if counts:
        top = ", ".join(f"{t}({n})" for t, n in counts.most_common(5))
        print(f"hottest tags: {top}")
    return 0


def cmd_brief(args) -> int:
    if not require_init():
        return 1
    print("=== STANDING RULES (inject into every work order) ===\n")
    print(RULES.read_text(encoding="utf-8").strip() if RULES.exists() else "(none)")

    lessons = read_lessons()
    if args.tags:
        want = {t.strip().lower() for t in args.tags.split(",")}
        lessons = [l for l in lessons if want & set(l.get("tags", []))]
        header = f"=== LESSONS: {', '.join(sorted(want))} ==="
    else:
        header = "=== RECENT LESSONS ==="

    seen, picked = set(), []
    for l in reversed(lessons):                     # newest first, dedup
        k = norm(l.get("text", ""))
        if k in seen:
            continue
        seen.add(k)
        picked.append(l)
        if len(picked) >= args.limit:
            break

    print(f"\n{header}\n")
    if not picked:
        print("(none recorded yet)")
    for l in picked:
        tags = ",".join(l.get("tags", [])) or "-"
        print(f"- [{l.get('severity','medium')}] ({tags}) {l['text']}")
    return 0


def cmd_mission_new(args) -> int:
    if not require_init():
        return 1
    slug = slugify(args.name)
    d = MISSIONS / slug
    (d / "reports").mkdir(parents=True, exist_ok=True)
    mission = d / "MISSION.md"
    if mission.exists():
        print(f"{mission} already exists — not overwriting.", file=sys.stderr)
        return 1
    mission.write_text(
        f"""# Mission: {args.name}

## Outcome
<One paragraph: what is true at the end that isn't true now.>

## Definition of done
<Checkable statements only — each one a command you can run or an artifact you can
inspect. If you can't verify it, rewrite it.>
- [ ]
- [ ]

## Constraints
<Budget, stack, what must not change, deploy targets, deadlines.>

## Out of scope
<The list that stops the conclave wandering. Be generous.>

## Risk register
<Anything irreversible. Every item here is a human gate.>
""",
        encoding="utf-8",
    )
    (d / "PLAN.md").write_text(
        "# Plan\n\n| Wave | Orders | Verification | Checkpoint SHA | Status |\n"
        "|---|---|---|---|---|\n| 1 | | | | planned |\n",
        encoding="utf-8",
    )
    (d / "DECISIONS.md").write_text(
        "# Decisions\n\n_Record what was chosen, and what was rejected and why — "
        "otherwise a future agent will cheerfully re-propose the rejected option._\n",
        encoding="utf-8",
    )
    print(f"created {d}/  (MISSION.md, PLAN.md, DECISIONS.md, reports/)")
    return 0


# ---------------------------------------------------------------- cli

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="conclave", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="scaffold .conclave/").set_defaults(func=cmd_init)

    b = sub.add_parser("brief", help="standing rules + relevant lessons")
    b.add_argument("--tags", help="comma-separated tags to filter lessons by")
    b.add_argument("--limit", type=int, default=12)
    b.set_defaults(func=cmd_brief)

    m = sub.add_parser("mission", help="mission scaffolding")
    msub = m.add_subparsers(dest="mcmd", required=True)
    mn = msub.add_parser("new")
    mn.add_argument("name")
    mn.set_defaults(func=cmd_mission_new)

    l = sub.add_parser("lesson", help="the ledger")
    lsub = l.add_subparsers(dest="lcmd", required=True)

    la = lsub.add_parser("add")
    la.add_argument("--text", required=True, help="one sentence, generalised, concrete")
    la.add_argument("--tag", action="append", default=[], help="repeatable or comma-separated")
    la.add_argument("--severity", choices=SEVERITIES, default="medium")
    la.add_argument("--mission", default=None)
    la.add_argument("--wave", default=None)
    la.set_defaults(func=cmd_lesson_add)

    ll = lsub.add_parser("list")
    ll.add_argument("--tag")
    ll.add_argument("--limit", type=int, default=30)
    ll.set_defaults(func=cmd_lesson_list)

    lsub.add_parser("digest").set_defaults(func=cmd_lesson_digest)
    return p


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

# Session Logs

A lightweight, append-only record of work sessions — human or agent. Each meaningful working
session gets one file. This gives future contributors (and future you) a chronological narrative
of *what changed and why*, complementing git history (which shows *what* but rarely *why in
context*) and [project-status.md](../project-status.md) (which shows current state, not history).

## Convention

- **One file per session**, named `YYYY-MM-DD-<short-slug>.md` (e.g. `2026-08-21-docs-scaffolding.md`).
  If multiple sessions happen in a day, add a suffix: `-2`, `-am`/`-pm`, etc.
- **Copy [`_TEMPLATE.md`](_TEMPLATE.md)** to start.
- **Newest is discoverable** via file date; keep entries concise and factual.
- **Don't rewrite past logs** — they're a historical record. Correct later entries instead.

## What to capture

- The **goal** of the session and its outcome.
- **Files created/changed** (high level — not a full diff).
- **Decisions** made (link to an ADR if load-bearing).
- **Tests run** / verification performed and results.
- **Open questions** and **next steps** for whoever picks up.

## When to write one

After any session that changes code, docs, schema, or project direction. Trivial one-line fixes
don't need a log. This is required by [`../../AGENTS.md`](../../AGENTS.md) §10 for agents after
meaningful work.

## Index

| Date | Session |
|---|---|
| 2026-08-21 | [Docs & skeleton scaffolding](2026-08-21-docs-scaffolding.md) |

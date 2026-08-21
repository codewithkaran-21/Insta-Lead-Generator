# CLAUDE.md

This file is Claude Code's entrypoint. The canonical, tool-agnostic guidance lives in
`AGENTS.md`; the imports below pull it (and the core docs) into context so there is a single
source of truth.

## Imports

@AGENTS.md
@docs/project-context.md
@docs/project-status.md
@docs/workflow.md
@docs/edge-cases.md

## Claude Code specific notes

- **Read `AGENTS.md` first** — it is the canonical guide (repo map, commands, architectural
  rules, gotchas). Everything below is additive.
- **Plan mode for non-trivial work.** Multi-file features, the verification engine, and schema
  changes should be planned before editing. Small doc/stub edits can proceed directly.
- **Current state:** the repo is documentation + an inert skeleton. Source files are stubs
  that `raise NotImplementedError`. Check `docs/project-status.md` before assuming anything runs.
- **After meaningful work**, per `AGENTS.md` §10:
  1. Update `docs/project-status.md`.
  2. Add a `docs/session-logs/YYYY-MM-DD-<slug>.md` entry (copy `_TEMPLATE.md`).
  3. Add an ADR if you made a load-bearing decision.
- **Commits:** Conventional Commits; end the message body with:
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`
  Only commit/push when the user asks.
- **The authoritative deep spec** is `implementation_plan(insta leads).md` (RFC-2026-08).
  When a doc and the spec disagree, the spec wins — and fix the doc.
- **Never** put real secrets in tracked files; use `.env` (git-ignored) from `.env.example`.

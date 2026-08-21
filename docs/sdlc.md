# SDLC — Software Development Lifecycle

> How we build, review, test, and ship InstaLeads. For the *runtime* pipeline see
> [workflow.md](workflow.md); for the build order see [implementation-plan.md](implementation-plan.md).

## 1. Environments

| Environment | Backend | Database | Frontend |
|---|---|---|---|
| Local dev | `python run_pipeline.py` from a venv | Supabase dev project (or a personal project) | `npm run dev` |
| CI | GitHub Actions runners | same dev/staging project | build check |
| Production | GitHub Actions (`run_pipeline.yml`, manual dispatch) | Supabase prod project | Vercel |

Secrets live only in `.env` (local, git-ignored) and GitHub Actions secrets (CI/prod). See
[configuration.md](configuration.md) and [security.md](security.md).

## 2. Branching model

- `main` — always releasable; protected.
- `feat/<short-slug>`, `fix/<slug>`, `docs/<slug>`, `chore/<slug>` — short-lived branches off `main`.
- Rebase or squash-merge to keep `main` linear. Delete branches after merge.

## 3. Commit conventions

[Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional scope>): <summary>

<body — the why>
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `ci`.
Example: `feat(stage4): add variance guard to reject single-viral-post accounts`.

Agents (Claude Code) end commit bodies with:
`Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.

## 4. Pull request checklist

- [ ] Scope is one logical change; description explains the *why*.
- [ ] Tests added/updated and green (see [testing-strategy.md](testing-strategy.md)).
- [ ] No secrets, keys, or PII committed.
- [ ] Provider calls stay behind the ABCs (no direct SDK calls in pipeline code).
- [ ] Docs updated: `project-status.md`, relevant `docs/*`, and an ADR if a decision was made.
- [ ] A [session log](session-logs/README.md) entry was added for the work.
- [ ] Migrations are additive and reversible where possible.

## 5. Code review guidelines

Reviewers verify: correctness of the **verification math** (median/variance/CLR/geo), gate
ordering and reasons, error handling for the failure modes in [edge-cases.md](edge-cases.md),
absence of hidden costs (no extraction before pre-filter), and readability.

## 6. Testing gates

- Unit tests for all Stage 4 math and providers (mocked).
- Stage 0 control-cohort validation must pass (positives don't get false-rejected).
- CI runs lint + type-check + tests on every PR. Merges require green CI.

## 7. CI/CD

- **`.github/workflows/run_pipeline.yml`** — manual `workflow_dispatch` with niche/country/ER
  inputs; installs deps and runs the pipeline with secrets from GitHub.
- **`.github/workflows/heartbeat.yml`** — cron every 3 days to keep the free-tier Supabase
  project from pausing.
- Frontend deploys via Vercel on push to `main` (see [deployment.md](deployment.md)).

## 8. Definition of Done

A unit of work is done when: it works end-to-end for its slice, is covered by tests, handles the
relevant edge cases, logs structured telemetry, updates docs + status + session log, and passes
review + CI.

## 9. Versioning & releases

- Semantic-ish tags on `main` (`v0.x` during pre-1.0).
- Database migrations are timestamped files in `supabase/migrations/` — never edit an applied
  migration; add a new one.
- Note notable releases in [project-status.md](project-status.md)'s changelog.

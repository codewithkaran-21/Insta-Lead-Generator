# Frontend — InstaLeads Dashboard

Next.js (App Router) + TypeScript dashboard that reads **VERIFIED / GOLD** leads from Supabase
and lets an operator filter, inspect, and export them. Read-only: it talks to Supabase via
PostgREST using the **anon** key, governed by Row Level Security (anon = `SELECT` only).

> **Status:** skeleton only. Components are stubs. Config files are minimal placeholders — the
> dependency versions and Next scaffolding get finalized in milestone M6. See
> [../docs/project-status.md](../docs/project-status.md).

## Security (read this first)

- The browser uses **only** `NEXT_PUBLIC_SUPABASE_URL` + `NEXT_PUBLIC_SUPABASE_ANON_KEY`.
- The **`service_role` key must NEVER appear in frontend code or any `NEXT_PUBLIC_` var** — it
  bypasses RLS. Writes happen exclusively from the backend pipeline. See
  [../docs/security.md](../docs/security.md).

## Layout

| Path | Purpose |
|---|---|
| `src/app/layout.tsx` | Root layout |
| `src/app/page.tsx` | Dashboard page (sidebar + table) |
| `src/components/FilterSidebar.tsx` | Filter controls (niche, ER, followers, geo, status) |
| `src/components/LeadsTable.tsx` | Sortable/paginated leads table |
| `src/components/LeadDetailDrawer.tsx` | Per-lead detail panel |
| `src/components/StatusBadge.tsx` | VERIFIED / GOLD badge |
| `src/components/ExportCsvButton.tsx` | Export current view to CSV |
| `src/hooks/useLeads.ts` | Data-fetching hook (filters → query) |
| `src/lib/supabase.ts` | Supabase browser client (anon key) |

## Setup (target state)

```bash
cd frontend
npm install
cp ../.env.example .env.local   # set NEXT_PUBLIC_SUPABASE_URL + NEXT_PUBLIC_SUPABASE_ANON_KEY
npm run dev
```

See [../docs/deployment.md](../docs/deployment.md) for Vercel deployment.

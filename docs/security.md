# Security & Compliance

> Secrets, access control, and the responsible-use posture for a tool that processes public
> social data. See also [configuration.md](configuration.md) and [deployment.md](deployment.md).

## 1. Secrets management

- All credentials are **environment variables** — never hard-coded, never committed.
- `.env` is git-ignored; CI/prod secrets live in **GitHub Actions secrets**.
- **`service_role` key is backend-only.** It has full DB mutation rights and must never reach the
  browser, a `NEXT_PUBLIC_` var, or client bundles.
- The frontend uses only the **`anon`** key, which is safe to expose because access is constrained
  by Row Level Security.

## 2. Row Level Security (RLS)

The `leads` table has RLS **enabled** with two policies (spec §4):

| Policy | Role | Grant |
|---|---|---|
| Allow Public Anonymous Read | `anon` | `SELECT` only (`USING (true)`) |
| Allow Service Role Full Mutation | `service_role` | `ALL` (`USING (true) WITH CHECK (true)`) |

Result: the public dashboard can read; only the backend (service role) can write. If the
dashboard shows nothing, verify the anon `SELECT` policy is present and enabled.

## 3. Data handling & privacy

- **Public data only** — profiles, public bios, public post metrics, and publicly listed contact
  info. No private/DM/authenticated-scope data.
- Contact info is business/outreach contact that creators list publicly; still, treat it
  respectfully and support removal on request.
- Don't persist more than needed for verification + outreach (the schema is the allowlist).

## 4. Provider ToS & rate-limit etiquette

- Respect each provider's terms and rate limits (Apify, Serper, Groq, Instagram-derived data).
- The system is a **verification** tool, not a mass-harvest crawler — the cost-discipline design
  (pre-filter before extraction) also keeps request volume low and polite.
- Back off on 429s; never hammer an endpoint.

## 5. Outreach compliance (downstream)

- InstaLeads produces leads; it does not send. Any outreach built on top must comply with
  anti-spam law (e.g. CAN-SPAM) and platform rules — out of scope here but worth stating.

## 6. Dependency & supply-chain hygiene

- Pin dependencies (`requirements.txt`, `package.json`).
- Review new dependencies before adding; prefer well-maintained libraries.

## 7. Checklist for any change touching data or keys

- [ ] No secret in code, logs, or tests.
- [ ] `service_role` stays server-side.
- [ ] New columns don't leak sensitive data to the anon read policy.
- [ ] Network calls have timeouts and respect rate limits.

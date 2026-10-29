# Private site (Supabase + Vercel)

Decision D57, plan `docs/DEPLOYMENT_PLAN.md` section 10.

```mermaid
flowchart LR
  GA[GitHub Actions<br/>daily cycle] -->|export-supabase<br/>secret key| SB[(Supabase<br/>snapshots, profiles)]
  V[Vercel<br/>static site] -->|publishable key + session| SB
  U[Invited user] --> V
```

- `site.js`: sign-in, account request with an invitation code, accounts page for the
  super admin, data read from the `snapshots` table.
- `build.sh`: copies the dashboard from `src/footintel/api/static` into `dist/` and adds
  the Supabase layer. Vercel runs it (root directory `football-intel/web`, output `dist`).
- `../supabase/migrations/`: tables, row level security, account functions.
- `.github/workflows/util-football-intel-daily.yml`: daily cycle, encrypted state in the
  Actions cache, export to Supabase.

## Accounts

| Status | Meaning |
|---|---|
| `en_attente` | Request sent with a valid code; cannot see data |
| `actif` | Approved by the super admin |
| `refuse` / `suspendu` | No access |

The super admin is the account whose e-mail is in `private.settings`
(`superadmin_email`). It is not in this public repository. To change it, run in the
Supabase SQL editor:

```sql
update private.settings set value = 'new@address' where key = 'superadmin_email';
```

Open signup stays off (`open_signup = 'false'`). Only invitation codes work.

## One-time setup (owner)

1. Supabase, Authentication > URL Configuration: set Site URL to the Vercel address and
   add it to Redirect URLs.
2. Supabase, Project Settings > API Keys: create a secret key.
3. GitHub, repository Settings > Secrets and variables > Actions:
   - variable `SUPABASE_URL` = `https://mnwyipiakbleihdfpegg.supabase.co`
   - secret `SUPABASE_SECRET_KEY` = the secret key of step 2
   - secret `FOOTINTEL_STATE_KEY` = a long random password (encrypts the cached database;
     keep a copy: without it the state cannot be read)
   - optional secrets: `FOOTBALL_DATA_ORG_KEY`, `ODDS_API_KEY`, `TELEGRAM_BOT_TOKEN`,
     `TELEGRAM_CHAT_ID`
4. Merge the branch into `master`: scheduled workflows run only from the default branch.
   Then start the workflow once by hand (Actions > football-intel > Run workflow).
5. Sign up on the site with the super admin e-mail (no code needed), confirm the e-mail.

## Limits

- Supabase free: 500 MB database, project paused after 7 days without activity (the
  daily export prevents it), a few auth e-mails per hour with the built-in sender.
- Only the default period of each competition is exported; other periods show the
  default one. Personal picks and the local administration page are not on the site.

# Deploy to Streamlit Community Cloud

How the Tech Lead puts KeyGuard Local online for the demo (fast-track-playbook §8, NFR-DEP-01, NFR-ENV-01b). Do this after the stories for the release are merged into `main`.

**Why not Vercel or GitHub Pages?** Streamlit needs a server that keeps running, which those don't provide. Streamlit Community Cloud does, for free.

## 1. A separate Supabase project for the live demo

The live app uses its **own** database, never the dev one (NFR-ENV-01). Keys for it stay with the Tech Lead only.

1. supabase.com → **New project** → name `keyguard-demo` → Free plan.
2. **Authentication → Sign In / Providers → Email → Confirm email: off.**
3. **SQL Editor:** apply `supabase/migrations/0001`–`0009` in order, then `supabase/seed/01_products.sql` ([database-setup.md](database-setup.md)).
4. **Authentication → Users:** create **only** `owner@example.com` (NFR-ENV-04: the demo gets products and the owner only), then run `supabase/seed/02_demo_roles.sql`. It reports the missing staff and customer accounts and stops, so either create those two as well for the class demo, or edit the run to only set the owner.
5. Note the project URL and the **anon / publishable** key for step 3 below.

## 2. Check `main` before deploying

Ask Claude in a **new** session (fast-track-playbook §8, step 1):

```text
Check that main has no .env or secrets (git ls-files), that requirements.txt is complete,
and tell me anything that would break a deploy. Do not change files.
```

Also check: CI is green on `main`, and `python -m pytest tests/unit -q` passes locally.

## 3. Create the app on Streamlit Community Cloud

1. Go to **share.streamlit.io** and sign in **with GitHub** (the account that owns the repo).
2. **Create app → Deploy a public app from GitHub:**
   - Repository: `training3-m/keyguard-local`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
   - App URL: pick a name, for example `keyguard-local`
3. **Advanced settings:**
   - **Python version:** 3.12
   - **Secrets:** paste, with the **demo** project's values (never the `service_role` / `secret` key):

     ```toml
     SUPABASE_URL = "https://<demo-project-id>.supabase.co"
     SUPABASE_ANON_KEY = "<anon or publishable key>"
     ```

   Type the keys yourself from Supabase. **Never paste keys into Claude or GitHub.**
4. **Deploy.** Watch the build log. If it fails, copy the **last 20 lines** (no keys in them) into Claude: *"Here is the Streamlit build log. What is wrong and what is the smallest fix?"* Then fix it through a normal pull request.

## 4. Smoke test the live site

| # | Check |
|---|---|
| 1 | The page opens with the dark theme and the menu: Shop, Cart, Checkout, Sign in, Register |
| 2 | Sign in as the owner → Manage section, including Staff & users |
| 3 | The demo customer can't see Manage pages |
| 4 | When the shop stories are merged: browse → add to cart → sign in → place order → confirmation, and the stock went down in Supabase |
| 5 | The confirmation offers **Download confirmation email** (files in `outbox/` disappear when the app restarts on Streamlit Cloud; that's expected, NFR-DEP-01) |

## 5. Tag the release

When the smoke test passes:

```powershell
git switch main
git pull
git tag -a v1.0 -m "Demo v1.0"
git push origin v1.0
```

## Notes

- Free apps go to sleep after a few days without visitors. Open the URL before class to wake it up (NFR-SCALE-05).
- Free Supabase projects pause after about a week without activity. Open the dashboard before class.
- Every push to `main` redeploys automatically.
- Between classes, reset the demo data with `supabase/seed/reset_demo.sql` (to be written before release, NFR-PRIV-04).

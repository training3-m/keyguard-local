# KeyGuard Local (Demo / Training)

A demo online store for **fictional keypad-locked USB drives**, with a dark gaming/RGB look that puts security first. Part of every sale goes to the (fictional) Rancho Public Library Digital Safety Fund. Built with **Streamlit** and **Supabase** to teach how a real web app is built, tested and deployed.

> **Demo only:** no real payments, no real emails, no real orders. Use `@example.com` addresses.

**Status:** foundation (Prompts A–F) built. Pages show "Coming soon — US-…" until their stories are built (see the [work division plan](docs/planning/work-division-plan.md)).

---

## Run it on Windows (about 10 minutes)

You need: **Python 3.11 or newer**, **Git**, and **VS Code**. Type each command in the VS Code terminal (**Ctrl + `**), which is PowerShell.

### 1. Get the code

```powershell
git clone https://github.com/training3-m/keyguard-local.git
cd keyguard-local
code .
```

### 2. Create the project's own Python (a "venv") and install the packages

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Check:** `.\.venv\Scripts\python.exe -m streamlit version` prints a version (1.67 or newer).

*Optional:* to type `python`, `streamlit` and `pytest` without the `.\.venv\Scripts\` part, run `.\.venv\Scripts\Activate.ps1`. If Windows says scripts are disabled, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.

### 3. Add the Supabase keys (never committed)

```powershell
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
Copy-Item .env.example .env
```

Open **both** new files in VS Code and fill in:

- `SUPABASE_URL`: your project URL, `https://<project-id>.supabase.co`
- `SUPABASE_ANON_KEY`: the **anon / publishable** key from Supabase → Project Settings → API Keys

⚠️ Never use the `service_role` or `secret` key; the app refuses it. Get the dev keys from the Tech Lead **privately**, not through GitHub or chat with Claude. Both files are blocked by `.gitignore`.

**First time for the whole team only:** the Tech Lead sets up the database once by following [docs/deployment/database-setup.md](docs/deployment/database-setup.md) and [docs/deployment/demo-accounts.md](docs/deployment/demo-accounts.md).

### 4. Run the app

```powershell
.\.venv\Scripts\streamlit.exe run streamlit_app.py --server.headless=true
```

Open **http://localhost:8501**. Stop it with **Ctrl + C** in the terminal.

`--server.headless=true` skips Streamlit's first-run "Email:" question. Without it, the app waits in the terminal and the browser says "unable to connect".

**Check:** sign in with a demo account (passwords from the Tech Lead):

| Account | You should see |
|---|---|
| (signed out) | Menu: Shop, Cart, Checkout, Sign in, Register |
| `customer@example.com` | + My account |
| `staff@example.com` | + Manage: Dashboard, Products, Orders |
| `owner@example.com` | + Manage: … and Staff & users |

### 5. Run the checks (the same ones CI runs on every pull request)

```powershell
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\python.exe -m pytest tests/unit -q
```

**Check:** `All checks passed!` and `… passed`. The unit tests use a **fake** Supabase (`tests/conftest.py`), so they need no keys and no internet.

---

## Troubleshooting

| You see | Fix |
|---|---|
| Browser: "Unable to connect" | The app isn't running. Start it with step 4 (with `--server.headless=true`) and keep that terminal open. |
| "The store isn't set up yet" / "Missing SUPABASE_URL" | Step 3: `.streamlit/secrets.toml` is missing or still has empty values. Save the file (Ctrl + S). |
| "…is a secret / service-role key" | You pasted the wrong key. Use the anon / publishable one. |
| `python` opens the Microsoft Store | Restart VS Code after installing Python, or use `.\.venv\Scripts\python.exe`. |
| `ModuleNotFoundError` | Run step 2's `pip install -r requirements.txt` again, inside this folder. |
| `pip install` says "The filename or extension is too long" (then `No module named 'streamlit.proto'`) | Windows path limit: the folder is too deep. Delete the folder, clone into a short path such as `C:\Projects\keyguard-local`, and start again from step 1. |
| Sign-in always fails | Check the account exists in Supabase → Authentication → Users, and that **Confirm email** is off. |

## How the code is organized

A click travels: **page** (`app_pages/`) → **service** (`services/`) → **Supabase table + security rule** (`supabase/migrations/`). Pages never call Supabase directly. Every function and its owner is listed in [docs/architecture/service-contracts.md](docs/architecture/service-contracts.md).

| Folder / file | Purpose |
|---|---|
| `streamlit_app.py` | Entry point: theme, menu by role, header. Stories never edit it. |
| `app_pages/` | One file per page (shop, cart, checkout, account, sign in/register, manage…) |
| `components/` | Reusable UI: product card, Security HUD, badges, order detail, empty/error states |
| `services/` | All database calls (one Supabase client per browser session) |
| `models/` | Data shapes: Product, CartLine, Totals, Order, UserProfile |
| `utils/` | Helpers with no database: cart, pricing, money format, settings, page guards |
| `validation/` | Form checks (email, password rules, names) |
| `assets/` | `styles/theme.css` (RGB glow, focus, reduced motion) and images |
| `supabase/migrations/` | Database tables, security rules and functions, applied in number order |
| `supabase/seed/` | Sample products, demo account roles, sample orders |
| `supabase/tests/` | SQL test for `place_order` (no overselling, no double orders) |
| `tests/unit/` | Fast Python tests with a fake Supabase (`tests/conftest.py`) |
| `.streamlit/config.toml` | Dark theme colors and fonts (committed); `secrets.toml` is never committed |
| `.github/` | CI (ruff + pytest on every pull request) and the pull request template |
| `CLAUDE.md` | Rules for Claude Code in this repo |
| `docs/requirements/` | What to build. Start with the [README](docs/requirements/README.md). |
| `docs/planning/` | Who builds what: [work division plan](docs/planning/work-division-plan.md) |
| `docs/architecture/` | [Service contracts](docs/architecture/service-contracts.md) |
| `docs/deployment/` | [Database setup](docs/deployment/database-setup.md), [demo accounts](docs/deployment/demo-accounts.md) |
| `docs/training/` | The teacher's playbooks (unchanged) and a [Git cheat sheet](docs/training/git-cheatsheet.md) |
| `archive/` | An older alternative requirement set, not used for the build |

## Tech stack

Streamlit 1.67 (Python 3.11+) · Supabase (Postgres, Auth, Storage) · Streamlit Community Cloud · GitHub Actions CI

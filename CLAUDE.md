# KeyGuard Local: rules for Claude Code

KeyGuard Local: a demo store for a high school class that sells fictional keypad-locked USB drives with a dark gaming/RGB look that puts security first; part of each sale goes to a fictional Riverton library fund. Streamlit + Supabase. No real payments or emails.

## Read first
- Stories and plan: `docs/planning/work-division-plan.md` (pick codes U1-01…, foundation FND-01…13), `docs/requirements/01-product.md`
- Look and feel: `docs/requirements/02-ui-ux.md` (section 2.1 color tokens win)
- Security and quality: `docs/requirements/03-non-functional-requirements.md`
- Summary, data model, open questions: `docs/requirements/00-consolidated-requirements.md`

## Our file names vs. the training playbooks
The playbooks in `docs/training/` were written for a different example store. In this repo:
- `app/pages` → `pages/`, `app/services` → `services/`, `app/components` → `components/`, `app/streamlit_app.py` → `streamlit_app.py`
- `01-product-features-user-stories.md` → `01-product.md`, `02-ui-ux-requirements.md` → `02-ui-ux.md`
- "doc 02 section 3" (colors) → `02-ui-ux.md` section 2.1
- Story IDs look like `US-CART-01`, not `US-101`. Features are F1–F6, not E1–E7.

## Layers (explain these to the student when asked)
page (`pages/`) -> service (`services/`) -> Supabase table + security rule (`supabase/migrations`)
Pages never call Supabase directly. Reusable UI is in `components/`. Business rules live in services or database functions.

## Rules
- Build only the story you are asked for. Touch only its files. Ask before changing `streamlit_app.py`, `requirements.txt`, service or component signatures, or any merged migration (add a NEW migration file instead).
- Never read, print or commit `.env`, `.streamlit/secrets.toml` or any key. The service role key is never used in the app.
- Add files to git by name, never `git add -A`. Never push to `main`. Never merge a PR.
- Keep code beginner-friendly: clear names, short functions, a comment for each non-obvious "why", type hints on service functions.
- If a test fails, say whether the test or the code is wrong before changing anything. Never delete a test to get green.
- Honest selling: no gamification for shoppers (no points, XP, badges, leaderboards or random rewards; "gaming" is the visual style only). No fake timers or fake scarcity: "Only N left" shows real stock. Never claim the drives are "unhackable" or certified.
- Motion safety: nothing flashes more than 3 times a second, and all animation respects `prefers-reduced-motion`.

## Commands (venv active)
- Run: `streamlit run streamlit_app.py`
- Lint: `ruff check .`
- Tests: `python -m pytest tests/unit -q`

## Skills
- Streamlit pages and components: `developing-with-streamlit`
- SQL, migrations, security rules: `supabase-postgres-best-practices`
- Layout, color, accessibility: `ui-ux-pro-max`

## When reviewing (a separate, read-only session)
Report only. Do not edit files. Check scope, acceptance criteria, secrets, role checks and tests. End with VERDICT, BLOCKERS, SHOULD FIX, NOT CHECKED.

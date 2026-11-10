# Streamlit E-commerce (Demo / Training)

A demo e-commerce web app built with **Streamlit** and **Supabase**, used to teach app building and deployment.

> Status: project skeleton only. Code will be generated from the documents in `docs/requirements/`.

## Folder structure

| Folder | Purpose |
|---|---|
| `.streamlit/` | Streamlit config (`config.toml`) and local secrets. Copy `secrets.toml.example` to `secrets.toml`; the real file is never committed. |
| `.env.example` | Template for `.env`, which scripts and tests use. Copy it and fill in the values; `.env` is never committed. |
| `.claude/skills/` | Agent skills for Claude Code (Streamlit, Supabase/Postgres, UI/UX), recorded in `skills-lock.json` |
| `pages/` | Streamlit multipage app pages (catalog, cart, checkout, orders, admin…) |
| `components/` | Reusable UI pieces (product card, cart widget, nav, forms) |
| `services/` | Supabase client and data access (products, cart, orders, auth) |
| `models/` | Data models / schemas used by the app |
| `utils/` | Shared helpers (formatting, validation, session state) |
| `assets/images/` | Static images (logo, placeholder product images) |
| `assets/styles/` | Custom CSS |
| `supabase/migrations/` | SQL migrations for tables, RLS policies |
| `supabase/seed/` | Sample/seed data for demos |
| `tests/unit/` | Fast tests with no database (pricing, cart, validation, email files) |
| `tests/integration/` | Tests against the Test Supabase project (security rules, overselling) |
| `scripts/` | Helper scripts (for example, applying migrations or resetting demo data) |
| `docs/requirements/` | Requirement documents that drive code generation. Start with the [README](docs/requirements/README.md). |
| `docs/planning/` | Work division plan, with earlier versions in `versions/` |
| `docs/architecture/` | Architecture notes and diagrams (added during the foundation phase) |
| `docs/deployment/` | Deployment guides (Streamlit Community Cloud, etc.) |
| `archive/` | Old or alternative requirement sets, not used for the build. See [archive/README.md](archive/README.md) for how to swap sets. |

## Requirements

The project is **KeyGuard Local**, a demo store for fictional keypad-locked USB drives with a gaming/RGB look. Its requirements are in [`docs/requirements/`](docs/requirements/README.md):

- [Consolidated requirements](docs/requirements/00-consolidated-requirements.md)
- [Product features and user stories](docs/requirements/01-product.md)
- [UI/UX requirements](docs/requirements/02-ui-ux.md)
- [Non-functional requirements](docs/requirements/03-non-functional-requirements.md)

An older alternative set, **CivicKey Store**, is kept in [`archive/requirements-civickey/`](archive/requirements-civickey/).

## Tech stack

- Frontend/app: Streamlit (Python)
- Database & auth: Supabase (Postgres)
- Deployment: Streamlit Community Cloud

# Work Division Plan — KeyGuard Local

| | |
|---|---|
| **Team** | 6 members, working together on GitHub |
| **Source** | [00-consolidated-requirements.md](../requirements/00-consolidated-requirements.md) · [01-product.md](../requirements/01-product.md) · [02-ui-ux.md](../requirements/02-ui-ux.md) · [03-non-functional-requirements.md](../requirements/03-non-functional-requirements.md) |
| **Scope** | 31 user stories (F1–F6) plus the non-functional requirements (NFRs) |
| **Timeline** | 5 one-week sprints (Sprint 0 – Sprint 4) |
| **Purpose** | Learning and demo |

---

## 1. Team and roles

Each member owns **one feature area**, from the screen down to the database calls. Fill in names and GitHub handles in Sprint 0.

| ID | Role | Feature area | Name | GitHub handle |
|---|---|---|---|---|
| **M1** | Tech lead + Scrum master | Platform: app shell, navigation, session, role guards, CI, deployment, Manage dashboard | | |
| **M2** | Database and security lead | Supabase schema, RLS, database functions, seed data, integration tests | | |
| **M3** | UI lead | F3 Product search, F4 Product detail, gaming/RGB theme, shared catalog components | | |
| **M4** | Shopping flow | F1 Add to cart, F2 Checkout, pricing, email outbox | | |
| **M5** | Identity | F5 Register / sign in, My Account, cart kept through sign-in | | |
| **M6** | Back office | F6 Owner and staff product and order management | | |

**Backups:** each member's **reviewer** (§2) is also their backup. If someone is away, the reviewer already knows the code and takes over.

| Member | Reviews work of | Why this pairing |
|---|---|---|
| M1 | M3 (some), M6 (guards) | Owns the shell those pages plug into |
| M2 | M5, M6, M4 (DB parts) | Checks the RLS and database-function use behind those features |
| M3 | M4, M1 | Keeps the UI consistent across shopping and dashboard |
| M4 | M3, M2 (checkout RPC) | Checks catalog → cart hand-off and the checkout contract |
| M5 | M4 (gate), M6 (roles) | Checks sign-in, session and role logic |
| M6 | M5 (My orders) | Shares the order data views |

---

## 2. Story assignments

Every story has one **owner**, who writes it and is responsible for it, and one **reviewer**, who approves the pull request (PR). "Sub-task" means another member supplies one piece, tracked as a separate linked issue.

### F1. Add to cart

| Story | Pri | Owner | Reviewer | Sprint | Notes |
|---|---|---|---|---|---|
| US-CART-01 Add to cart from detail | M | M4 | M3 | 1 | Uses M3's detail page; M4 provides the `add_to_cart()` helper |
| US-CART-02 View / change cart | M | M4 | M3 | 1 | Totals from `utils/pricing.py` |
| US-CART-03 Free-shipping hint | S | M4 | M3 | 3 | |
| US-CART-04 Cart kept through sign-in | M | M5 | M4 | 2 | Sign-in must not clear `st.session_state["cart"]` |

### F2. Checkout and order confirmation

| Story | Pri | Owner | Reviewer | Sprint | Notes |
|---|---|---|---|---|---|
| US-CHK-01 Sign-in gate at checkout | M | M4 | M5 | 2 | Uses M1's `require_signed_in()` |
| US-CHK-02 Checkout form, no card | M | M4 | M3 | 2 | |
| US-CHK-03 Inventory deducted (`place_order`) | M | **M2** | M4 | 1 → 2 | Draft in Sprint 1, final in Sprint 2. Sub-task for M4: call the function from the page. |
| US-CHK-04 `.eml` file in `outbox/` | M | M4 | M1 | 2 | `services/email_outbox.py` |
| US-CHK-05 Confirmation page | M | M4 | M3 | 2 | |
| US-CHK-06 My orders | S | M5 | M6 | 3 | Shares order-detail view with M6 |

### F3. Product search

| Story | Pri | Owner | Reviewer | Sprint |
|---|---|---|---|---|
| US-SRCH-01 Keyword search | M | M3 | M4 | 1 |
| US-SRCH-02 Filters | M | M3 | M4 | 1 |
| US-SRCH-03 Sort | S | M3 | M4 | 3 |
| US-SRCH-04 Filters in URL | C | M3 | M1 | 4 |

### F4. Product detail

| Story | Pri | Owner | Reviewer | Sprint | Notes |
|---|---|---|---|---|---|
| US-PDP-01 Product detail page + Security HUD | M | M3 | M1 | 1 | |
| US-PDP-02 "You may also like" | C | M3 | M4 | 4 | |

### F5. Customer register and sign in

| Story | Pri | Owner | Reviewer | Sprint | Notes |
|---|---|---|---|---|---|
| US-AUTH-01 Register | M | M5 | M2 | 1 | Profile row created by M2's trigger |
| US-AUTH-02 Sign in + 5-try lockout | M | M5 | M2 | 1 | |
| US-AUTH-03 Sign out | M | M5 | M1 | 1 | |
| US-AUTH-04 Edit name, change password | S | M5 | M2 | 3 | |
| US-AUTH-05 Forgot password (message only) | C | M5 | M1 | 4 | |

### F6. Owner and staff management

| Story | Pri | Owner | Reviewer | Sprint | Notes |
|---|---|---|---|---|---|
| US-MGT-01 Role-guarded Manage section | M | **M1** | M5 | 1 | `utils/guards.py` + role-based `st.navigation` |
| US-MGT-02 List all products | M | M6 | M2 | 1 | |
| US-MGT-03 Create product (owner) | M | M6 | M2 | 2 | |
| US-MGT-04 Bulk edit (staff vs owner fields) | M | M6 | M5 | 2 | M2 provides the price/gift column rule as a sub-task |
| US-MGT-05 Deactivate / reactivate | M | M6 | M2 | 2 | |
| US-MGT-06 Delete never-ordered product | S | M6 | M2 | 3 | |
| US-MGT-07 Image upload | S | M6 | M2 | 3 | M2 creates the Storage bucket and its policy |
| US-MGT-08 Dashboard | M | **M1** | M3 | 2 | Revenue tile owner-only |
| US-MGT-09 Manage orders + cancel | S | M6 | M5 | 3 | M2 provides `cancel_order` |
| US-MGT-10 Promote / demote staff | M | M6 | M2 | 2 | M2 provides `set_user_role` |

**Story count per owner:** M1 = 2 · M2 = 1 · M3 = 6 · M4 = 7 · M5 = 7 · M6 = 8. M1 and M2 carry fewer stories because they also own the platform and database work in §3, which every other member depends on.

---

## 3. Non-functional and technical work

| Work item | Requirement IDs | Owner | Reviewer | Sprint |
|---|---|---|---|---|
| Repo, branch protection, CODEOWNERS, labels, issue templates | — | M1 | M2 | 0 |
| App shell: `streamlit_app.py`, nav, theme loader | NFR-ROLE-02 | M1 | M3 | 0 |
| Supabase client per user, session handling, idle timeout | NFR-SES-01…05 | M1 | M5 | 0 → 1 |
| CI: ruff + pytest on every PR | NFR-TST-01 | M1 | M2 | 0 |
| Schema, `profiles` trigger, constraints | NFR-DB-04, §4.1 | M2 | M1 | 0 |
| RLS on every table | §4.2 | M2 | M5 | 0 → 1 |
| `place_order`, `cancel_order`, `set_user_role` | NFR-DB-01…03 | M2 | M4 / M6 | 1 → 2 |
| Seed data, `create_owner.sql`, `reset_demo.sql` | NFR-ROLE-05, NFR-PRIV-04 | M2 | M6 | 0 / 3 |
| `inventory_log` and `audit_log` writes | NFR-LOG-01…03 | M2 | M6 | 2 |
| Integration tests (RLS, oversell) | NFR-TST-02 | M2 | M4 | 3 |
| Theme CSS, components, motion safety | UX-01…15, NFR-UX-01…02 | M3 | M1 | 0 → 3 |
| Designer deliverables: style tile, wireframes, prototype | 02-ui-ux §10 | M3 | All | 0 |
| Password rules, lockout | NFR-AUTH-01…07 | M5 | M2 | 1 |
| Input validation, safe uploads, safe outbox names | NFR-SEC-03…07 | Feature owner | M2 | per story |
| Accessibility pass across all pages | NFR-UX-01…04 | M3 | M5 | 3 |
| Security checklist sign-off | 03 §11 | M2 | M1 | 4 |
| Deployment: Streamlit Cloud + `docs/deployment/` | NFR-DEP-01…02 | M1 | M2 | 4 |
| 15 end-to-end scenarios run and recorded | 01 Part C | Whole team, led by M4 | M1 | 4 |

---

## 4. Sprint plan

One-week sprints. Planning on Monday, review and retro on Friday.

### Sprint 0 — Setup and contracts

**Goal:** everyone can run the app locally, sign in to the shared Supabase dev project, and code against agreed function stubs.

| Member | Deliverables |
|---|---|
| M1 | GitHub repo, `main` protection, CODEOWNERS, labels, milestones, issue/PR templates, CI. App shell with role-based nav and **empty page files for every page**. `requirements.txt`, `.streamlit/config.toml`. |
| M2 | Supabase dev project. Migration `001_schema.sql`, first RLS draft, seed products and 3 demo accounts. Shares the anon key with the team privately (§6.6). |
| M3 | Style tile, low-fidelity wireframes and `assets/styles/theme.css` v1. `product_card`, `stock_badge` and `lock_indicator` components with placeholder data. |
| M4 | `utils/pricing.py` with unit tests (shipping threshold, 8% tax, rounding). Stub for `services/orders.py`. |
| M5 | Sign-in technical spike: supabase-py auth with tokens held in session state. Stub for `services/auth.py`. |
| M6 | Manage pages showing static mock tables. Stub for `services/admin_products.py`. |
| **All** | Agree the **interface contracts** in §5 and create one GitHub issue for every story in §2. |

### Sprint 1 — Browse, sign in, basic manage

| Member | Stories / work |
|---|---|
| M1 | US-MGT-01 · per-user Supabase client · session timeout |
| M2 | Final RLS for products and profiles · `place_order` draft + tests |
| M3 | US-SRCH-01 · US-SRCH-02 · US-PDP-01 |
| M4 | US-CART-01 · US-CART-02 |
| M5 | US-AUTH-01 · US-AUTH-02 · US-AUTH-03 |
| M6 | US-MGT-02 |

**Sprint 1 demo:** a guest searches, opens a product and adds it to the cart. A user registers and signs in. Staff see the product list in Manage, and a customer cannot open it.

### Sprint 2 — Buy and manage (all Mandatory stories done)

| Member | Stories / work |
|---|---|
| M1 | US-MGT-08 |
| M2 | US-CHK-03 final · `set_user_role` · column rule for staff edits · log tables |
| M3 | Security HUD polish, hover glow, reduced-motion support |
| M4 | US-CHK-01 · US-CHK-02 · US-CHK-04 · US-CHK-05 |
| M5 | US-CART-04 |
| M6 | US-MGT-03 · US-MGT-04 · US-MGT-05 · US-MGT-10 |

**Sprint 2 demo:** the full purchase flow, from guest cart through sign-in and checkout to a stock reduction and an `.eml` file in `outbox/`. The owner creates a product and promotes a staff member.

### Sprint 3 — Should-have stories and integration

| Member | Stories / work |
|---|---|
| M1 | Streamlit Cloud test deploy · error pages (NFR-REL-03) |
| M2 | `cancel_order` · Storage bucket policy · integration tests (RLS, oversell) · `reset_demo.sql` |
| M3 | US-SRCH-03 · accessibility pass |
| M4 | US-CART-03 · help M2 with the oversell test |
| M5 | US-CHK-06 · US-AUTH-04 |
| M6 | US-MGT-06 · US-MGT-07 · US-MGT-09 |

### Sprint 4 — Could-have stories, hardening and final demo

| Member | Stories / work |
|---|---|
| M1 | Production deploy · `docs/deployment/` guide |
| M2 | Security checklist (03 §11) · `pip-audit` |
| M3 | US-SRCH-04 · US-PDP-02 · visual QA on phone and desktop |
| M4 | Lead the run of the 15 end-to-end scenarios and record the results |
| M5 | US-AUTH-05 · auth edge-case tests |
| M6 | Bug fixes from the end-to-end run · admin UX polish |

**Rule:** Could-have stories (US-SRCH-04, US-PDP-02, US-AUTH-05) are the **first to drop** if Sprint 4 runs short. Must-have stories never slip past Sprint 2. If one does, the team pairs on it before anything else.

---

## 5. Interface contracts (agreed in Sprint 0)

These function signatures let everyone build in parallel. Changing one requires a PR reviewed by **both** the owner and every caller.

```python
# utils/session.py        (M1)
get_client() -> Client                       # per-user, uses session tokens
current_user() -> UserProfile | None         # id, email, full_name, role

# utils/guards.py         (M1)
require_signed_in() -> UserProfile           # else shows gate + st.stop()
require_role(*roles: str) -> UserProfile     # else "Staff access only" + st.stop()

# services/auth.py        (M5)
register(full_name, email, password) -> UserProfile
sign_in(email, password) -> UserProfile
sign_out() -> None
change_password(current, new) -> None

# services/products.py    (M3)   public reads
search_products(term="", category=None, capacity=None, price_range=None,
                in_stock_only=False, sort="featured") -> list[Product]
get_product(sku) -> Product | None

# services/admin_products.py (M6)  staff/owner writes
list_all_products(term="", include_inactive=True) -> list[Product]
create_product(data: dict) -> Product
update_products(changes: list[dict]) -> int
set_active(sku, active: bool) -> None
delete_product(sku) -> None

# services/orders.py      (M4)
place_order(cart: dict[str, int], shipping: dict, idempotency_key: UUID) -> OrderResult
list_my_orders() -> list[Order]              # used by M5's My orders

# services/admin_orders.py (M6)
list_orders(status=None, date_from=None, date_to=None) -> list[Order]
set_status(order_id, status) -> None
cancel_order(order_id) -> None

# services/users.py       (M5)
list_users(term="") -> list[UserProfile]
set_user_role(user_id, role) -> None         # wraps M2's database function

# services/email_outbox.py (M4)
write_confirmation(order: Order) -> Path

# utils/pricing.py        (M4)
calculate_totals(lines: list[CartLine]) -> Totals   # subtotal, shipping, tax, total, gift
```

Database function names and parameters are fixed by M2 in `003_functions.sql`. Python code never calls a database function directly except through the service file named above.

---

## 6. File ownership rules (avoiding merge conflicts)

### 6.1 Ownership map

Only the owner (or someone with their approved PR review) changes these files. The `CODEOWNERS` file in §6.4 enforces this on GitHub.

| Path | Owner |
|---|---|
| `streamlit_app.py`, `utils/session.py`, `utils/guards.py`, `utils/formatting.py`, `.streamlit/config.toml`, `.github/` | M1 |
| `pages/manage_dashboard.py` | M1 |
| `supabase/` (all migrations and seed files) | M2 |
| `tests/integration/` | M2 |
| `pages/shop.py`, `components/product_card.py`, `components/security_hud.py`, `components/lock_indicator.py`, `components/stock_badge.py`, `services/products.py`, `models/product.py`, `assets/` | M3 |
| `pages/cart.py`, `pages/checkout.py`, `components/cart_summary.py`, `services/orders.py`, `services/email_outbox.py`, `utils/pricing.py`, `models/cart.py`, `models/order.py` | M4 |
| `pages/sign_in.py`, `pages/register.py`, `pages/account.py`, `services/auth.py`, `services/users.py`, `models/user.py` | M5 |
| `pages/manage_products.py`, `pages/manage_orders.py`, `pages/manage_users.py`, `services/admin_products.py`, `services/admin_orders.py` | M6 |
| `tests/unit/test_<module>.py` | Owner of that module |
| `docs/requirements/` | M1 approves, plus the owner of the affected feature |

### 6.2 Rules for shared files

1. **`streamlit_app.py` (navigation):** M1 creates **every page entry in Sprint 0**, so nobody else needs to edit it. Need a new page? Open an issue for M1.
2. **`requirements.txt`:** add packages on **their own line, in alphabetical order**, with a pinned version, in a small PR of their own. M1 reviews.
3. **Database migrations:** **only M2 writes migrations.** Need a column or policy? Open an issue labeled `db`. Files are numbered (`004_…`, `005_…`) and never edited after they're merged; changes go in a new file.
4. **`utils/validation.py`:** split by area into `validation/products.py`, `validation/auth.py` and `validation/checkout.py`, each owned by the matching feature owner.
5. **`assets/styles/theme.css`:** M3 only. Others ask for new CSS classes through an issue. Pages never contain inline `<style>` blocks.
6. **Models:** one model per file, owned by its feature. Adding a field to someone else's model needs their review.

### 6.3 Habits that prevent conflicts

- Keep branches **short-lived** (1–3 days) and PRs **small** (under about 400 changed lines).
- Pull `main` into your branch **every morning** (`git pull origin main` or rebase).
- Format with **ruff format** before committing. CI fails on unformatted code, so formatting differences never cause conflicts.
- Never reformat or reorganize a file you don't own as part of another change.

### 6.4 CODEOWNERS template

Save as `.github/CODEOWNERS` and replace the placeholders with real GitHub handles:

```
*                                 @M1-handle
/supabase/                        @M2-handle
/tests/integration/               @M2-handle
/pages/shop.py                    @M3-handle
/components/                      @M3-handle
/components/cart_summary.py       @M4-handle
/assets/                          @M3-handle
/services/products.py             @M3-handle
/pages/cart.py                    @M4-handle
/pages/checkout.py                @M4-handle
/services/orders.py               @M4-handle
/services/email_outbox.py         @M4-handle
/utils/pricing.py                 @M4-handle
/pages/sign_in.py                 @M5-handle
/pages/register.py                @M5-handle
/pages/account.py                 @M5-handle
/services/auth.py                 @M5-handle
/services/users.py                @M5-handle
/pages/manage_products.py         @M6-handle
/pages/manage_orders.py           @M6-handle
/pages/manage_users.py            @M6-handle
/services/admin_products.py       @M6-handle
/services/admin_orders.py         @M6-handle
/pages/manage_dashboard.py        @M1-handle
```

### 6.5 Local outputs never committed

`outbox/`, `.streamlit/secrets.toml`, `.venv/` and `__pycache__/` are all git-ignored. Check this before every commit with `git status`.

### 6.6 Sharing secrets

The Supabase URL and **anon key** are shared through a private channel (team password manager or a direct message), **never** in GitHub issues, PRs, code or commits. The service-role key is held only by M2 and never used in the app.

---

## 7. GitHub workflow

### 7.1 Issues

- **One issue per user story**, titled `US-CART-01: Add to cart from detail page`. The body copies the story and its acceptance criteria from 01-product.md.
- **Tasks and sub-tasks** (for example "M2: add `cancel_order` function") are separate issues, linked from the story with "Blocked by #N".
- **Labels:**
  - `feature:F1` … `feature:F6`, `platform`, `db`, `ui`
  - `priority:M`, `priority:S`, `priority:C`
  - `type:story`, `type:task`, `type:bug`
  - `blocked`
- **Milestones:** `Sprint 0` … `Sprint 4`.
- **Assignee** = the story owner. The reviewer is named in the issue body.
- **Project board** columns: `Backlog → Ready → In progress → In review → Done`.

**Definition of Ready (before an issue moves to Ready):** acceptance criteria are clear, dependencies are listed and unblocked (or stubbed), and the owner and reviewer are set.

### 7.2 Branches

- `main` is always deployable. It is **protected**: no direct pushes, a PR is required, CI must pass, at least 1 approval, and review from code owners is required.
- Branch names:

| Kind | Pattern | Example |
|---|---|---|
| Story | `feature/<story-id>-<short-name>` | `feature/US-CART-01-add-to-cart` |
| Task | `task/<issue#>-<short-name>` | `task/42-cancel-order-fn` |
| Database | `db/<issue#>-<short-name>` | `db/17-rls-products` |
| Bug | `fix/<issue#>-<short-name>` | `fix/58-cart-badge-count` |

- One story per branch. Delete the branch after merge.

### 7.3 Commits

Use the format `<type>(<area>): <message> [<story-id>]`, for example:

```
feat(cart): add quantity stepper with stock cap [US-CART-02]
fix(auth): keep cart after sign-in [US-CART-04]
test(pricing): cover free-shipping threshold
```

Types: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`, `db`.

### 7.4 Pull requests

- The title matches the commit style. The body includes `Closes #<issue>`, a short summary, **screenshots** for UI changes and a "How to test" section.
- PR template checklist:
  - [ ] Acceptance criteria met (list them)
  - [ ] Unit tests added or updated, and CI is green
  - [ ] No secrets, no `outbox/` files, no print-debugging
  - [ ] Only files I own were changed, or the owner is a reviewer
  - [ ] Role checks in place for any Manage page (`require_role`)
  - [ ] User text is never rendered with `unsafe_allow_html`
  - [ ] Screenshots attached (dark theme, phone width) for UI changes
- **Review:** the assigned reviewer responds within **1 working day**. Use GitHub's "Request changes" only for real defects, and mark style nits as `nit:`.
- **Merge:** the **author** uses squash-merge after approval and green CI.

### 7.5 Definition of Done

**A story is done when:**
1. Every acceptance criterion in 01-product.md is met and was shown to the reviewer.
2. Unit tests pass in CI. Any database change has an RLS or integration test (M2).
3. It follows the UX requirements (dark theme, security strip and HUD where required, labels and contrast, no flashing).
4. It meets the relevant NFRs, including validation, role guards, no secrets and generic error messages.
5. The PR is approved by the reviewer and merged to `main`, and `main` still runs.
6. The issue is closed and the board card is in **Done**.

**A sprint is done when:**
- All committed stories meet the story DoD.
- The sprint demo runs from `main` on a fresh session.
- Anything unfinished is moved to the next sprint with a reason noted in the retro.

---

## 8. Meetings

| Meeting | When | Length | Who | Output |
|---|---|---|---|---|
| **Sprint planning** | Monday, start of sprint | 45 min | All, led by M1 | Sprint issues moved to Ready and assigned. Risks checked. |
| **Daily stand-up** | Every working day, same time (in person, call, or written in the team chat) | 15 min | All | Each member covers: done yesterday / doing today / blocked by. Blockers get a named helper. |
| **Contract and design review** | Sprint 0, Wednesday | 60 min | All | §5 interfaces signed off, style tile and wireframes approved |
| **Mid-sprint integration check** | Wednesday or Thursday | 30 min | All | `main` pulled and run together; integration bugs filed |
| **Database / security sync** | Sprints 1–2, as needed | 20 min | M2 + whoever needs a schema change | `db` issues triaged |
| **Sprint review (demo)** | Friday | 30 min | All, plus instructor or stakeholder | Demo script from §4 run live on `main` |
| **Retrospective** | Friday, after review | 20 min | All | 1 thing to keep, 1 to change, 1 action with an owner |

Notes from every meeting go in one GitHub Discussion thread per sprint, or in `docs/planning/notes/sprint-N.md`.

---

## 9. Risks

| # | Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|
| R1 | **Schema changes late** break several features | Medium | High | Schema and contracts frozen at the end of Sprint 0. Later changes go in new migration files, are announced at stand-up and are reviewed by the affected owners. | M2 |
| R2 | **RLS mistakes** let customers see others' data, or staff change prices | Medium | High | Every table has an RLS integration test (NFR-TST-02). Security checklist in Sprint 4. | M2 |
| R3 | **Shared Supabase client cached across users** (`st.cache_resource`) leaks sessions | Medium | High | Only `utils/session.get_client()` creates clients, and reviewers reject any other client creation. | M1 |
| R4 | **Merge conflicts** in navigation, requirements or CSS | High | Medium | File ownership (§6), all page entries created in Sprint 0, small PRs, pull `main` daily | M1 |
| R5 | **`place_order` delayed**, blocking checkout | Medium | High | M4 builds against a stub in Sprint 1. The draft function lands in Sprint 1 and the final in Sprint 2. M4 pairs with M2. | M2 / M4 |
| R6 | **RGB styling takes too long** (custom CSS has limits in Streamlit) | Medium | Medium | Styling is timeboxed to the style tile in Sprint 0 and polish in Sprint 2. Function before polish, and Could-have effects drop first. | M3 |
| R7 | **Secrets committed** to GitHub | Low | High | `.gitignore`, PR checklist, GitHub secret scanning on. If it happens, rotate the key at once. | M1 |
| R8 | **Supabase free-tier project pauses** after inactivity, or hits its limits | Medium | Medium | Someone opens the app at least weekly. `reset_demo.sql` and the seed data rebuild it quickly. | M2 |
| R9 | **`outbox/` files lost** on Streamlit Cloud restart | High | Low | Expected (NFR-DEP-01). The demo uses the Download confirmation email button. | M4 |
| R10 | **Member absent** or uneven Git experience | Medium | Medium | The reviewer is the backup. Sprint 0 includes a 30-minute Git workflow walkthrough, and anyone can pair with M1. | M1 |
| R11 | **Scope creep** (reviews, payments, real email) | Medium | Medium | Out-of-scope list in 00 §2. New ideas go to the backlog as `priority:C`. | M1 |
| R12 | **Accessibility or motion issues** with neon effects | Low | Medium | Accessibility pass in Sprint 3, `prefers-reduced-motion` support, contrast checks on the style tile | M3 |

Risks are reviewed at each sprint planning. Add new ones to this table through a PR.

---

## 10. Getting started checklist (Sprint 0, day 1)

- [ ] M1 runs `git init`, pushes to GitHub, invites all 5 members and turns on branch protection and secret scanning
- [ ] Everyone fills in their name and handle in §1, and M1 updates `.github/CODEOWNERS`
- [ ] M1 creates labels, milestones and the project board, and the team creates the 31 story issues from §2
- [ ] M2 creates the Supabase dev project and shares the anon key privately
- [ ] Everyone clones the repo, creates `.venv`, installs `requirements.txt`, adds `secrets.toml` and runs `streamlit run streamlit_app.py`
- [ ] Each member opens a first small PR (a stub for their service file) to practise the workflow

# Work Division Plan — KeyGuard Local (v3: foundation first, one list per user)

| | |
|---|---|
| **Source** | [00](../requirements/00-consolidated-requirements.md) · [01](../requirements/01-product.md) · [02](../requirements/02-ui-ux.md) · [03](../requirements/03-non-functional-requirements.md) |
| **Team** | 1 Tech Lead + 3 participants |
| **Scope** | 31 user stories: 7 built by the Tech Lead in the foundation, 24 built by participants |
| **Timeline** | 5 weeks in 3 phases: Foundation → Stories → Release |
| **Changed from v1** | v1 had 6 members building in parallel and waiting on each other. In v2 the Tech Lead builds everything shared **first**, so participants can then work on one story at a time without waiting. |
| **Changed from v2** | v3 gives **User 1, User 2 and User 3** each their own ordered story list with **pick codes** (U1-01 …) in §5. The workloads are balanced, and the few links between users are listed separately. |

---

## 1. The three phases

```
 Week 1–2                 Week 3–4                          Week 5
┌──────────────────┐     ┌──────────────────────────────┐  ┌──────────────────┐
│ PHASE 1          │     │ PHASE 2                      │  │ PHASE 3          │
│ FOUNDATION       │ ──► │ STORIES                      │─►│ RELEASE          │
│ Tech Lead builds │     │ Participants: one story at a │  │ Merge, test,     │
│ the shared base  │     │ time → branch → build → test │  │ deploy, tag v1.0,│
│ and pushes it    │     │ → PR → review → merge → next │  │ demo             │
└──────────────────┘     └──────────────────────────────┘  └──────────────────┘
```

**Why this works:** after the foundation, every page already exists as a stub, every database table, rule and function already exists, and every service function already exists with fake data. A participant's story only fills in **their own page or function**, so they never wait for someone else.

---

## 2. Team and roles

| Role | Who | Phase 1 | Phase 2 | Phase 3 |
|---|---|---|---|---|
| **Tech Lead** | | Builds foundation items FND-01…13 | Reviews PRs, makes any database schema change (`schema-change` label), unblocks people | Runs the release |
| **User 1: Browse** | | Set up computer, review Lead's PRs, write test scenarios, prepare product images and copy | Works through list U1 (§5.1): search, detail, add to cart, account | Fix bugs, run scenarios, demo |
| **User 2: Buy** | | Set up computer, review Lead's PRs, write test scenarios | Works through list U2 (§5.2): cart, checkout, email, orders, dashboard | Fix bugs, run scenarios, demo |
| **User 3: Manage** | | Set up computer, review Lead's PRs, write test scenarios | Works through list U3 (§5.3): owner and staff product and order management | Fix bugs, run scenarios, demo |

---

## 3. Phase 1 — Foundation (Tech Lead)

The Tech Lead builds these in order and pushes each one to GitHub through a PR. A participant reviews each PR, which is how they learn the codebase.

**Sizes:** S = about 2–3 hours · M = about half a day to 1 day · L = about 1–2 days.

| ID | Item | Files | Covers | Size |
|---|---|---|---|---|
| FND-01 | **Repo setup:** `git init`, push to GitHub, protect `main` (admins can bypass during the foundation phase), labels, milestones, issue and PR templates, `CODEOWNERS` | `.github/` | — | M |
| FND-02 | **Python setup:** pinned `requirements.txt`, dark theme in `config.toml`, `secrets.toml.example`, `.gitignore` check | `requirements.txt`, `.streamlit/` | NFR-SEC-01 | S |
| FND-03 | **CI:** ruff + pytest on every PR | `.github/workflows/ci.yml` | NFR-TST-01 | S |
| FND-04 | **Test setup:** pytest config, shared fixtures, a test Supabase connection, one sample unit test and one sample integration test | `pyproject.toml`, `tests/conftest.py`, `tests/unit/`, `tests/integration/` | NFR-TST-01…02 | S |
| FND-05 | **Database schema:** every table, constraint and index, plus the `profiles` trigger | `supabase/migrations/001_schema.sql` | 03 §4.1, NFR-DB-04 | M |
| FND-06 | **Security rules:** RLS on every table, the rule that stops staff changing price or gift, and the `product-images` Storage bucket with its policy | `supabase/migrations/002_rls.sql` | 03 §4.2, NFR-SEC-06 | L |
| FND-07 | **Database functions:** `place_order`, `cancel_order`, `set_user_role` and log writes, with integration tests for overselling and RLS | `supabase/migrations/003_functions.sql`, `tests/integration/` | **US-CHK-03**, NFR-DB-01…03, NFR-LOG | L |
| FND-08 | **Seed data:** 11 products, 3 demo accounts, **3 demo orders** (so order pages have data before checkout exists), `create_owner.sql`, `reset_demo.sql` | `supabase/seed/` | 01 §A5, NFR-PRIV-04 | M |
| FND-09 | **Session and role guards:** a Supabase client for each user, tokens, idle timeout, `require_signed_in`, `require_role` | `utils/session.py`, `utils/guards.py` | **US-MGT-01**, NFR-SES, NFR-ROLE | M |
| FND-10 | **Sign-in:** register, sign in, sign out, 5-try lockout, "forgot password" message, cart kept through sign-in | `pages/sign_in.py`, `pages/register.py`, `services/auth.py` | **US-AUTH-01, 02, 03, 05, US-CART-04**, NFR-AUTH | L |
| FND-11 | **App shell:** role-based nav, a **stub for every page**, header, demo footer, community banner, `theme.css` v1 | `streamlit_app.py`, `pages/*.py`, `assets/styles/theme.css` | UX-01, 02, 05, 06, 12 | M |
| FND-12 | **Models and service stubs:** every model, plus every service function in Appendix A, returning **realistic fake data** | `models/`, `services/` | — | M |
| FND-13 | **Shared parts:** `product_card`, `stock_badge`, `lock_indicator`, `security_hud`, `community_chip`, `order_detail`, `empty_state`; `utils/pricing.py` and `utils/cart.py` (add/update/remove in the session) with tests; `utils/formatting.py`; the `validation/` package | `components/`, `utils/`, `validation/` | UX-03, 04, 09 | L |

**Stories finished in the foundation (7):** US-CHK-03, US-AUTH-01, US-AUTH-02, US-AUTH-03, US-AUTH-05, US-CART-04 and US-MGT-01. These are built into FND-07, FND-09 and FND-10. They're the pieces everyone else depends on, so the Lead builds them once.

**The foundation is done when** `main` runs and you can:
- browse fake products,
- sign in as each of the 3 demo users,
- see the correct menu for each role,
- see CI pass.

The Lead then posts *"Foundation done"* and Phase 2 starts.

---

## 4. Phase 2 — Stories (participants)

### 4.1 How participants work

Each participant has **only one story open at a time**:

1. **Claim:** take the **next pick code on your own list** in §5 (for example U2-03). Assign yourself to its GitHub issue and move it to *In progress*.
2. **Branch:** create it from the latest `main` (see §7.2 for names).
3. **Build:** change only the files listed for that story.
4. **Test:** add or update unit tests, and run `pytest` and `streamlit run` locally.
5. **Pull request:** open a PR with `Closes #<issue>`, add screenshots, and request a review.
6. **Review:** User 1's PRs are reviewed by User 2, User 2's by User 3, and User 3's by User 1. The Lead also reviews if a foundation file was touched.
7. **Merge:** squash-merge, delete the branch, close the issue.
8. **Next:** claim the next story.

### 4.2 Story catalog (24 stories)

"Depends on" lists **only other stories**. Everything also depends on the foundation being done.

| Story | Pri | Size | Files it touches | Depends on |
|---|---|---|---|---|
| **F3 Product search** | | | | |
| US-SRCH-01 Keyword search | M | M | `pages/shop.py`, `services/products.py` | — |
| US-SRCH-02 Filters | M | M | `pages/shop.py`, `components/filters.py`, `services/products.py` | SRCH-01 |
| US-SRCH-03 Sort | S | S | `components/filters.py`, `services/products.py` | SRCH-02 |
| US-SRCH-04 Filters in URL | C | S | `components/filters.py` | SRCH-02 |
| **F4 Product detail** | | | | |
| US-PDP-01 Detail page + Security HUD | M | L | `components/product_detail.py`, `services/products.py` | — |
| US-PDP-02 "You may also like" | C | S | `components/product_detail.py`, `services/products.py` | PDP-01 |
| **F1 Cart** | | | | |
| US-CART-01 Add to cart button | M | S | `components/product_detail.py` (uses `utils/cart.py`) | PDP-01 |
| US-CART-02 Cart page | M | M | `pages/cart.py`, `components/cart_summary.py` | — |
| US-CART-03 Free-shipping hint | S | S | `components/cart_summary.py` | CART-02 |
| **F2 Checkout** | | | | |
| US-CHK-01 Sign-in gate | M | S | `pages/checkout.py` | — |
| US-CHK-02 Checkout form | M | M | `pages/checkout.py`, `services/orders.py`, `validation/checkout.py` | CHK-01 |
| US-CHK-05 Confirmation page | M | S | `pages/checkout.py` | CHK-02 |
| US-CHK-04 `.eml` file in `outbox/` | M | M | `services/email_outbox.py`, `services/orders.py` | CHK-02 |
| US-CHK-06 My orders | S | M | `components/my_orders.py`, `services/orders.py` | — (uses seed orders) |
| **F5 Account** | | | | |
| US-AUTH-04 Edit name, change password | S | M | `components/account_profile.py`, `services/auth.py` (fills in the `change_password` stub) | — |
| **F6 Manage** | | | | |
| US-MGT-02 Product list | M | M | `pages/manage_products.py`, `services/admin_products.py` | — |
| US-MGT-05 Deactivate / reactivate | M | S | `pages/manage_products.py`, `services/admin_products.py` | MGT-02 |
| US-MGT-03 Create product | M | M | `components/product_form.py`, `services/admin_products.py`, `validation/products.py` | MGT-02 |
| US-MGT-04 Bulk edit (staff vs owner) | M | L | `pages/manage_products.py`, `services/admin_products.py` | MGT-02 |
| US-MGT-07 Image upload | S | M | `components/product_form.py`, `services/storage.py` | MGT-03 |
| US-MGT-06 Delete never-ordered product | S | S | `pages/manage_products.py`, `services/admin_products.py` | MGT-02 |
| US-MGT-08 Dashboard | M | M | `pages/manage_dashboard.py`, `services/dashboard.py` | — |
| US-MGT-09 Manage orders + cancel | S | L | `pages/manage_orders.py`, `services/admin_orders.py` | — (uses seed orders) |
| US-MGT-10 Promote / demote staff | M | M | `pages/manage_users.py`, `services/users.py` | — |

This catalog is the reference. **Who builds what, and in which order, is in §5.**

---

## 5. Stories by user (pick lists)

**How to read the lists:**
- **Pick code:** your story's name in conversation, GitHub issues and branches, for example *"I'm on U2-03."*
- **Order:** work top to bottom. Must stories come first, then Should, then Could.
- **Depends on:** almost always a story **earlier in your own list**. Each user's **first story has no dependencies**, so everyone starts on the first day of Phase 2.
- **Points** balance the workload: S = 1, M = 2, L = 3.

### 5.1 User 1 — Browse (search, detail, add to cart, account)

| Pick | Story | Pri | Size | Depends on | Files |
|---|---|---|---|---|---|
| **U1-01** | US-SRCH-01 Keyword search | M | M | — | `pages/shop.py`, `services/products.py` |
| **U1-02** | US-SRCH-02 Filters | M | M | U1-01 | `components/filters.py`, `pages/shop.py`, `services/products.py` |
| **U1-03** | US-PDP-01 Detail page + Security HUD | M | L | — | `components/product_detail.py`, `services/products.py` |
| **U1-04** | US-CART-01 Add to cart button | M | S | U1-03 | `components/product_detail.py` |
| **U1-05** | US-MGT-10 Promote / demote staff | M | M | — | `pages/manage_users.py`, `services/users.py` |
| **U1-06** | US-SRCH-03 Sort | S | S | U1-02 | `components/filters.py`, `services/products.py` |
| **U1-07** | US-AUTH-04 Edit name, change password | S | M | — | `components/account_profile.py`, `services/auth.py` (stub body only) |
| **U1-08** | US-PDP-02 "You may also like" | C | S | U1-03 | `components/product_detail.py`, `services/products.py` |
| **U1-09** | US-SRCH-04 Filters in URL | C | S | U1-02 | `components/filters.py` |

**Total: 15 points** (13 without the Could stories).

### 5.2 User 2 — Buy (cart, checkout, email, orders, dashboard)

| Pick | Story | Pri | Size | Depends on | Files |
|---|---|---|---|---|---|
| **U2-01** | US-CART-02 Cart page | M | M | — | `pages/cart.py`, `components/cart_summary.py` |
| **U2-02** | US-CHK-01 Sign-in gate | M | S | — | `pages/checkout.py` |
| **U2-03** | US-CHK-02 Checkout form (no card) | M | M | U2-02 | `pages/checkout.py`, `services/orders.py`, `validation/checkout.py` |
| **U2-04** | US-CHK-05 Confirmation page | M | S | U2-03 | `pages/checkout.py` |
| **U2-05** | US-CHK-04 `.eml` file in `outbox/` | M | M | U2-03 | `services/email_outbox.py`, `services/orders.py` |
| **U2-06** | US-MGT-08 Dashboard | M | M | — | `pages/manage_dashboard.py`, `services/dashboard.py` |
| **U2-07** | US-CART-03 Free-shipping hint | S | S | U2-01 | `components/cart_summary.py` |
| **U2-08** | US-CHK-06 My orders | S | M | — | `components/my_orders.py`, `services/orders.py` |

**Total: 13 points.**

### 5.3 User 3 — Manage (owner and staff product and order management)

| Pick | Story | Pri | Size | Depends on | Files |
|---|---|---|---|---|---|
| **U3-01** | US-MGT-02 Product list | M | M | — | `pages/manage_products.py`, `services/admin_products.py` |
| **U3-02** | US-MGT-05 Deactivate / reactivate | M | S | U3-01 | `pages/manage_products.py`, `services/admin_products.py` |
| **U3-03** | US-MGT-03 Create product | M | M | U3-01 | `components/product_form.py`, `services/admin_products.py`, `validation/products.py` |
| **U3-04** | US-MGT-04 Bulk edit (staff vs owner fields) | M | L | U3-01 | `pages/manage_products.py`, `services/admin_products.py` |
| **U3-05** | US-MGT-07 Image upload | S | M | U3-03 | `components/product_form.py`, `services/storage.py` |
| **U3-06** | US-MGT-06 Delete never-ordered product | S | S | U3-01 | `pages/manage_products.py`, `services/admin_products.py` |
| **U3-07** | US-MGT-09 Manage orders + cancel | S | L | — | `pages/manage_orders.py`, `services/admin_orders.py` |

**Total: 14 points.**

### 5.4 Workload balance

| | Must | Should | Could | Total points | Points without Could |
|---|---|---|---|---|---|
| User 1 | 5 stories | 2 | 2 | 15 | 13 |
| User 2 | 6 stories | 2 | 0 | 13 | 13 |
| User 3 | 4 stories | 3 | 0 | 14 | 14 |
| Tech Lead (foundation) | 7 stories built into FND-07, 09, 10 | | | | |

If a user finishes early, they help the user with the most remaining points by pairing, never by taking over a file mid-story.

### 5.5 Cross-user dependencies (only 3, none blocking)

No user ever waits for another user to **start** a story. These three are the only places where two users' work meets:

| # | Between | What connects them | How it's handled |
|---|---|---|---|
| X1 | **U1-04** Add to cart ↔ **U2-01** Cart page | Both use the session cart | Both call `utils/cart.py` from the foundation, so each can be built and tested alone. The full flow (detail → cart) is tested together in REL-02. |
| X2 | **U2-08** My orders ↔ **U3-07** Manage orders | Both show an order using `components/order_detail.py` | The component is foundation-owned. If either user needs to change it, the PR needs the Lead **and** the other user to review. |
| X3 | **U3-03 / U3-04** Product create and edit ↔ **U1-01…03** Shop | Products created or edited in Manage appear in the shop | There's no code link, because both follow the fixed database schema. Seed data covers testing until then. |

### 5.6 Issue and branch naming with pick codes

- **Issue title:** `U2-03 · US-CHK-02 Checkout form (no card)`. Labels: `user:2`, `epic:F2`, `type:story`, `priority:must`, `size:M`. Milestone: `Stories`. Add "Depends on: U2-02" in the body.
- **Branch:** `u2-03-checkout-form`.
- **Commit:** `feat(checkout): add demo checkout form [U2-03]`.

---

## 6. Phase 3 — Release (everyone, week 5)

| ID | Task | Lead | Size |
|---|---|---|---|
| REL-01 | **Code freeze:** only bug-fix PRs from now on | Tech Lead | — |
| REL-02 | Run all **15 end-to-end scenarios** (01 Part C) on `main` and record pass/fail | User 1: scenarios 1–5 · User 2: 6–10 · User 3: 11–15 | M |
| REL-03 | **Security checklist** (03 §11) and `pip-audit` | Tech Lead | S |
| REL-04 | **Accessibility and motion pass:** contrast, labels, reduced motion, phone width | User 1 (owns most shopper screens) | M |
| REL-05 | Fix bugs found in REL-02…04 | Whoever owns the file | — |
| REL-06 | **Deploy** to Streamlit Community Cloud and write the `docs/deployment/` guide | Tech Lead | M |
| REL-07 | Tag **`v1.0`** and write release notes listing finished stories and known issues | Tech Lead | S |
| REL-08 | **Final demo** | All | — |

---

## 7. GitHub workflow

### 7.1 Issues, labels and milestones

- One issue per foundation item (`FND-07 Database functions`), per story (`U2-01 · US-CART-02 Cart page`) and per release task.
- **Labels:**
  - `user:lead`, `user:1`, `user:2`, `user:3`
  - `epic:F1` … `epic:F6`, `foundation`
  - `type:story`, `type:task`, `type:bug`
  - `priority:must`, `priority:should`, `priority:could`
  - `size:S`, `size:M`, `size:L`
  - `schema-change`, `blocked`
- **Milestones:** `Foundation`, `Stories`, `Release v1.0`.
- **Board columns:** `Backlog → Ready → In progress → In review → Done`.

### 7.2 Branches and commits

- `main` is protected: PR required, 1 approval, CI must pass. Admins can bypass only during the foundation phase.
- Branch names: `fnd-07-db-functions`, `u2-01-cart-page`, `fix-58-cart-badge`, `rel-06-deploy`.
- Commits: `feat(cart): add quantity stepper [U2-01]`. Types: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`, `db`.

### 7.3 Pull requests

- The body includes `Closes #N`, a summary, **screenshots** for UI changes and "How to test".
- Checklist: acceptance criteria met · tests added and CI green · only the story's listed files changed · no secrets or `outbox/` files · `require_role` on Manage pages · no user text inside `unsafe_allow_html`.
- Reviewers respond within 1 working day. The author squash-merges after approval.

### 7.4 Definition of Done (story)

1. Every acceptance criterion in 01-product.md is met.
2. Unit tests are added and CI is green.
3. It follows the UX rules (dark theme, labels, contrast, no flashing) and the NFR rules (validation, role guards, no secrets).
4. It's reviewed, merged to `main`, and `main` still runs.
5. The issue is closed and its card is in **Done**.

---

## 8. File ownership

| Files | Owner |
|---|---|
| Everything created in Phase 1: `streamlit_app.py`, `utils/`, `supabase/`, `.github/`, `.streamlit/`, `assets/`, `models/`, shared `components/`, `tests/conftest.py` | **Tech Lead** |
| `pages/shop.py`, `components/filters.py`, `components/product_detail.py`, `components/account_profile.py`, `services/products.py`, `pages/manage_users.py`, `services/users.py` | **User 1** |
| `pages/cart.py`, `pages/checkout.py`, `components/cart_summary.py`, `components/my_orders.py`, `services/orders.py`, `services/email_outbox.py`, `pages/manage_dashboard.py`, `services/dashboard.py`, `validation/checkout.py` | **User 2** |
| `pages/manage_products.py`, `pages/manage_orders.py`, `components/product_form.py`, `services/admin_products.py`, `services/admin_orders.py`, `services/storage.py`, `validation/products.py` | **User 3** |
| `pages/account.py` | Tech Lead. It only places User 1's profile tab and User 2's orders tab side by side, so neither user edits it. |

**Rules:**
1. **Only the Tech Lead changes the database.** Need a column? Open an issue labeled `schema-change`. It gets a new numbered migration file, and merged migration files are never edited.
2. **Stub hand-off:** a story may fill in the **body** of a stub function in a Lead-owned file (for example `change_password`). It must not change the function's name or parameters. The Lead reviews.
3. **No new pages** without the Lead, because the navigation lives in `streamlit_app.py`.
4. **No inline CSS** in pages. Ask the Lead to add a class to `theme.css`.
5. Pull `main` every morning, keep PRs under about 400 lines, and run `ruff format` before committing.
6. Secrets are never committed. The Supabase anon key is shared privately, and the service-role key is never used in the app.

---

## 9. Timeline

| Week | Tech Lead | User 1 | User 2 | User 3 | Milestone |
|---|---|---|---|---|---|
| 1 | FND-01 → FND-08 | Set up, review PRs, write test scenarios, prepare images and copy | Set up, review PRs, write test scenarios | Set up, review PRs, write test scenarios | Foundation |
| 2 | FND-09 → FND-13, "Foundation done" | Review PRs | Review PRs | Review PRs | Foundation |
| 3 | Review, schema changes | U1-01 → U1-04 | U2-01 → U2-04 | U3-01 → U3-03 | Stories |
| 4 | Review, help | U1-05 → U1-09 | U2-05 → U2-08 | U3-04 → U3-07 | Stories |
| 5 | REL-01, 03, 06, 07 | REL-02, REL-04, fixes | REL-02, fixes | REL-02, fixes | Release v1.0 |

---

## 10. Meetings

| Meeting | When | Length | Purpose |
|---|---|---|---|
| Kick-off | Week 1, day 1 | 45 min | Roles, set up, walk through this plan |
| Daily stand-up | Every day | 10–15 min | Each person says their pick code: "Done U1-02, now U1-03, not blocked" |
| Foundation walkthrough | End of week 2 | 45 min | Lead demos the base: where everything lives, how to add a story |
| Weekly demo + retro | Every Friday | 30 + 15 min | Show merged work. Keep / change / one action. |
| Release review | Week 5 | 30 min | Go / no-go on v1.0 |

---

## 11. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| **The foundation takes longer than 2 weeks** and participants sit idle | High | Build in order: FND-01…04 first, so participants can review early. If late, the Lead hands FND-13 components to participants as their first stories. |
| **Schema change needed mid-stories** | Medium | The `schema-change` label means the Lead adds a new migration within 1 day. Seed orders let order pages be built without checkout. |
| **Shared Supabase client leaks sessions** between users | High | Only `utils/session.get_client()` creates clients, and reviewers reject any other. |
| **RLS mistake** exposes data | High | Integration tests in FND-07 plus the security checklist in REL-03 |
| **Merge conflicts** | Medium | Every page is created in the foundation, file lists are fixed per story and PRs are small |
| **RGB styling eats time** | Medium | `theme.css` v1 is in the foundation, polish only in REL-04, and Could stories drop first |
| **Secrets committed** | High | `.gitignore`, the PR checklist and GitHub secret scanning. Rotate the key immediately if it happens. |
| **Uneven Git experience** | Medium | Reviewing foundation PRs in weeks 1–2 is the practice. Pair with the Lead on your first story. |

---

## Appendix A — Service function stubs (built in FND-12)

```python
# utils/session.py         get_client() · current_user()
# utils/guards.py          require_signed_in() · require_role(*roles)
# utils/cart.py            get_cart() · add(sku, qty) · update(sku, qty) · remove(sku) · clear()
# utils/pricing.py         calculate_totals(lines) -> Totals
# services/auth.py         register() · sign_in() · sign_out() · change_password(current, new)
# services/products.py     search_products(term, category, capacity, price_range, in_stock_only, sort) · get_product(sku) · related(sku)
# services/orders.py       place_order(cart, shipping, idempotency_key) · list_my_orders() · get_order(order_number)
# services/email_outbox.py write_confirmation(order) -> Path
# services/admin_products.py list_all_products() · create_product() · update_products() · set_active() · delete_product()
# services/storage.py      upload_image(file) -> url
# services/admin_orders.py list_orders() · set_status() · cancel_order()
# services/dashboard.py    metrics(role) · low_stock() · recent_orders()
# services/users.py        list_users() · set_user_role(user_id, role)
```

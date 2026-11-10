# KeyGuard Local — Consolidated Requirements

| | |
|---|---|
| **Project** | KeyGuard Local demo e-commerce store |
| **Stage** | Stage 1: Ideation and requirement analysis |
| **Stack** | Streamlit · Supabase (Postgres, Auth, Storage) · Streamlit Community Cloud |
| **Purpose** | Learning and demo only. No real payments, emails or orders. |
| **Version** | 3.0 — 2026-11-09 (added goals, data model, open questions, build order and traceability) |

This document is the **one-page starting point**. The detail files hold the full specifications:

| # | File | Audience | Covers |
|---|---|---|---|
| 1 | [01-product.md](01-product.md) | Product, developers, testers | Product concept, catalog, business rules, domain terms, **6 features as 31 user stories with acceptance criteria**, role matrix, 15 end-to-end scenarios |
| 2 | [02-ui-ux.md](02-ui-ux.md) | **Designer** | Vision analysis (what it means and doesn't mean), gaming/RGB visual system, components, site map, wireframes, user flows, screens S1–S16, system states, Streamlit limits, UX requirements, deliverables |
| 3 | [03-non-functional-requirements.md](03-non-functional-requirements.md) | Developers, reviewers | Sign-in, sessions, roles, data model and RLS, security, privacy and child safety, data integrity, performance, accessibility, environments, scalability limits, constraints and assumptions |
| — | [../planning/work-division-plan.md](../planning/work-division-plan.md) | The team | Who builds what and when (Tech Lead + User 1–3) |

If this summary and a detail file disagree, the **detail file wins**.

---

## 1. Goals

| # | Goal | How we'll know it worked |
|---|---|---|
| G1 | **Teach how a real web app is built**, from requirements to a deployed app, as a team on GitHub | Every story merged through a reviewed PR, and the app live on Streamlit Community Cloud |
| G2 | **Show a complete shopping flow** without real money or email | A shopper can search, add to cart, sign in, check out, see stock drop and download the `.eml` confirmation |
| G3 | **Show real security practices** in a safe setting | The security checklist (03 §11) is fully ticked, and the RLS tests pass |
| G4 | **Show the owner's product vision:** keypad-locked USB drives in a gaming/RGB style that puts security first | The designer's deliverables (02 §10) are approved, and UX-01…UX-15 are met |
| G5 | **Keep it safe and suitable for learners**, including minors | 03 §6 is met: no public user content, no tracking and age-appropriate content |

## 2. Product in one paragraph

KeyGuard Local sells **USB flash drives that lock with a physical PIN keypad**. The marketing copy (fictional) describes hardware AES-256 encryption, a self-wipe after 10 wrong PINs, and use on any computer with no software. Every drive sold sends a fixed amount to the fictional **Riverton Public Library Digital Safety Fund**. The catalog has 10 products across the Essentials, Pro, Riverton Community Edition, Bulk and Accessories lines, priced from $9 to $269. → *[01-product.md](01-product.md) Part A*

## 3. Users and roles

| Role | Typical person (01 §A3) | Can do |
|---|---|---|
| **Guest** | Anyone visiting | Browse, search, view details, fill a cart |
| **Customer** | Sam (student), Priya (small business) | Everything a guest can, plus check out, My Account and My orders |
| **Staff** | Kim (store staff) | Everything a customer can, plus edit stock, descriptions, images and active flags, and mark orders packed or shipped |
| **Owner** | Jordan (store owner) | Everything, including prices, creating or deleting products, cancelling orders, revenue and managing staff |

All accounts register as `customer`. Only the owner can promote a user to staff, and the first owner is set up once with SQL. → *[01-product.md](01-product.md) Part B*

## 4. Feature summary

| # | Feature | Stories | Summary |
|---|---|---|---|
| F1 | **Add to cart** | US-CART-01…04 | Guests can fill a session cart. Quantities are capped at min(10, stock), prices come from the database, there is a free-shipping hint, and the cart is kept through sign-in. |
| F2 | **Checkout and order confirmation** | US-CHK-01…06 | **Sign-in required.** **No credit card.** One database transaction **deducts inventory**. A confirmation email is **saved as a `.eml` file in `outbox/` and never sent**. Includes a confirmation page and My orders. |
| F3 | **Product search** | US-SRCH-01…04 | Keyword search, category, capacity, price and in-stock filters, sort options and an empty state |
| F4 | **Product detail** | US-PDP-01…02 | Specs, Security HUD, keypad explainer, stock and community gift, `?sku=` URL |
| F5 | **Customer register and sign in** | US-AUTH-01…05 | Supabase email/password, password rules, generic errors, 5-try lockout, profile and password change |
| F6 | **Owner and staff management** | US-MGT-01…10 | Role-guarded Manage section, product create/edit/delete, bulk edit, images, dashboard, orders, staff promotion (owner only) |

### Business rules

| Rule | Value |
|---|---|
| Shipping | $4.99. **Free** at $75 or more. |
| Tax | 8% of the subtotal |
| Quantity per line | 1 – min(10, stock) |
| Payment | None |
| Order number | `KG-YYYYMMDD-NNNN` |
| Money | Integer cents, recalculated on the server at checkout |
| Low stock | 5 units or fewer |

## 5. UI / UX summary (for the designer)

- **Vision:** *"A locked vault lit by RGB."* An original, dark-first gaming-hardware look that uses no real brand's logo or colors. Void Black surfaces, Neon Cyan primary, Unlock Green, Cipher Violet for security, an RGB gradient on edges only, display headings, bevelled corners and hover glow.
- **What "gaming" does NOT mean:** no points, badges or levels for shoppers, no flashing lights, no pressure tactics and no "unhackable" claims (02 §7–§8).
- **Security is the hero:** a security strip on every card, a Security HUD with stat bars, a red/green lock-state LED motif, and a keypad how-to.
- **Account UX:** an "Access Terminal" sign-in and register page, a checkout sign-in gate that keeps the cart, My Account, and navigation built from the user's role.
- **Screens and flows:** 16 screens (S1–S16), each linked to its stories, and 8 key user flows, all designed within Streamlit's limits (02 §11–§14).
- **Safety:** WCAG 2.1 AA, nothing flashing more than 3 times a second, `prefers-reduced-motion`, and age-appropriate content.

→ *[02-ui-ux.md](02-ui-ux.md) — UX-01…UX-15, deliverables in §10*

## 6. Non-functional summary

| Area | Highlights | 03 section |
|---|---|---|
| Sign-in | Supabase Auth (bcrypt). Passwords need 8+ characters including a letter and a number. Generic errors. 5-try lockout. No email confirmation in the demo. | §1 |
| Sessions | Tokens held only in `st.session_state`, a separate client for each user, a 30-minute idle timeout and a clean sign-out | §2 |
| Authorization | Three layers (menu, page check, Postgres RLS). The role is read from the database and changed only by the owner-only `set_user_role`. | §3 |
| Data security | RLS on every table. `SECURITY DEFINER` functions check roles and recalculate prices on the server. | §4 |
| App security | Anon key only, secrets git-ignored, no payment data, validation on client and server, no HTML from user content, safe uploads, safe outbox filenames | §5 |
| Privacy and child safety | Demo data only, minimal data, no public user content, no age or identity data, no tracking, supervised accounts | §6 |
| Logging | `inventory_log` for every stock change, `audit_log` for sensitive owner actions, no secrets in logs | §7 |
| Performance and reliability | Catalog under 2 s, checkout under 3 s, all-or-nothing checkout, friendly errors and no false success | §8 |
| Accessibility | WCAG 2.1 AA, motion safety, 360 px to desktop | §9 |
| Maintainability and testing | Clear layers, ruff in CI, pytest unit tests plus RLS and oversell integration tests | §10 |
| Data integrity | No overselling, no double orders, prices frozen at purchase, valid status changes only | §12 |
| Scalability limits | ≤ 200 products, ≤ 50 users at once, ≤ 5,000 orders, within free tiers | §13 |
| Environments | Dev, Test and Demo Supabase projects, the same migrations everywhere, deploy from tagged `main` | §14 |
| Constraints and assumptions | Streamlit + Supabase, $0 budget, 5 weeks, fictional product and city | §15 |

→ *[03-non-functional-requirements.md](03-non-functional-requirements.md)*

## 7. Logical data model

Full definitions are in [03 §4.1](03-non-functional-requirements.md#41-data-model). Security rules for each table are in 03 §4.2.

| Table | What it holds | Key fields | Links to |
|---|---|---|---|
| `profiles` | One row per user account | `id`, `full_name`, `role` (customer / staff / owner) | `auth.users` (Supabase sign-in) |
| `products` | The drives and accessories | `sku` (unique), `name`, `category`, `capacity_gb`, `price_cents`, `community_gift_cents`, `stock_qty` (≥ 0), `is_active`, `image_url` | — |
| `orders` | One row per demo order | `order_number` (unique), `customer_id`, `status`, money totals in cents, `idempotency_key` (unique), `email_file` | `profiles` (customer) |
| `order_items` | The lines of each order, with prices frozen | `order_id`, `product_id`, `sku`, `product_name`, `unit_price_cents`, `qty` | `orders`, `products` |
| `inventory_log` | Every stock change | `product_id`, `delta`, `reason`, `order_id`, `actor` | `products`, `orders`, `profiles` |
| `audit_log` | Sensitive owner actions | `actor`, `action`, `target`, `details` | `profiles` |

```
profiles 1───* orders 1───* order_items *───1 products
    │                                            │
    └──* inventory_log *─────────────────────────┘
    └──* audit_log
```

Database functions: `place_order`, `cancel_order` and `set_user_role` (03 §4.3).

## 8. Scope

**In scope:** features F1–F6, all 31 user stories, the gaming/RGB UI, the NFRs in doc 03, and deployment to Streamlit Community Cloud.

**Out of scope:**
- real payments, real email (including password-reset email), and real shipping or tax,
- social login, multiple currencies and product reviews,
- **gamification for shoppers** (points, XP, levels, badges),
- a real city partnership or real donations,
- any real company's branding.

## 9. Open questions (with default answers)

These questions are for the class or instructor to decide. **If nobody decides, the default is used.**

| # | Question | Default answer |
|---|---|---|
| Q1 | How big is the team: 6 people, or a Tech Lead + 3 users as in the class guide? | **Tech Lead + 3 users** (the work division plan is built this way) |
| Q2 | Should the GitHub repository be public or private? What should it be called? | **Public**, named **`keyguard-local`**, with no secrets ever committed |
| Q3 | Should staff see revenue on the dashboard? | **No.** Revenue and community totals are owner only. |
| Q4 | What product images are used? | **Simple original placeholder images** per SKU, made for the demo. No photos of real brands' products. |
| Q5 | Is the community banner total live or fixed? | **Live:** the sum of community gifts from orders that aren't cancelled |
| Q6 | Is a light theme needed? | **No.** Dark only for v1, and a light theme is optional later. |
| Q7 | Is Supabase email confirmation on? | **Off**, so no real emails are sent (NFR-AUTH-04) |
| Q8 | Can customers cancel their own orders? | **No.** Only the owner can cancel (US-MGT-09). |
| Q9 | Is the demo data reset between classes? | **Yes.** Run `reset_demo.sql` before each class (NFR-PRIV-04). |
| Q10 | Do the shipping and tax values stay fixed? | **Yes:** $4.99, free at $75 or more, 8% tax |
| Q11 | Is forgotten-password reset built? | **No.** The sign-in page shows "Contact the store owner" (US-AUTH-05). |
| Q12 | Do the drive specs need a "demo copy" label on the product page? | **Yes:** a small "Fictional product — demo copy" note under the specs (03 §15, A4) |

## 10. Suggested build order

Details, owners and pick codes are in the [work division plan](../planning/work-division-plan.md).

| Phase | When | What | Why this order |
|---|---|---|---|
| **1. Foundation** (Tech Lead) | Weeks 1–2 | FND-01 repo and CI → FND-05…08 database, security rules, functions and seed data → FND-09…10 session, guards and sign-in → FND-11…13 app shell, page stubs, service stubs and shared components | Everything shared is built once, so nobody waits later |
| **2. Stories** (User 1–3) | Weeks 3–4 | Each user works through their own list: **Must** stories first, then **Should**, then **Could**. User 1 builds browsing, User 2 buying, User 3 managing. | Each user's first story has no dependencies, so all three start on day one |
| **3. Release** (everyone) | Week 5 | Code freeze → 15 end-to-end scenarios → security checklist → accessibility pass → deploy → tag `v1.0` → demo | Everything is tested together before going live |

## 11. Traceability (features → stories → screens → NFRs → plan)

The screens are listed in [02 §12](02-ui-ux.md#12-screen-index-s1s16-linked-to-user-stories), and the pick codes are in the [work division plan §5](../planning/work-division-plan.md).

| Feature | User stories | Screens | Main NFRs | Built in |
|---|---|---|---|---|
| **F1 Add to cart** | US-CART-01, 02, 03, 04 | S2, S3, S4, S15 | NFR-INT-04 · NFR-PERF-01 · NFR-SES-03 · UX-09 | U1-04 · U2-01 · U2-07 · FND-10 |
| **F2 Checkout and confirmation** | US-CHK-01, 02, 03, 04, 05, 06 | S6, S7, S9 | NFR-DB-01 · NFR-INT-01, 02, 03 · NFR-REL-01, 02, 05 · NFR-SEC-02, 07 · NFR-CHILD-07 | FND-07 · U2-02…05 · U2-08 |
| **F3 Product search** | US-SRCH-01, 02, 03, 04 | S1 | NFR-PERF-01 · NFR-SEC-04 · NFR-SCALE-01 | U1-01 · U1-02 · U1-06 · U1-09 |
| **F4 Product detail** | US-PDP-01, 02 | S2 | NFR-UX-01, 02 · NFR-CHILD-03 · UX-03, 04 | U1-03 · U1-08 |
| **F5 Register and sign in** | US-AUTH-01, 02, 03, 04, 05 | S4, S5, S8, S15 | NFR-AUTH-01…08 · NFR-SES-01…05 · NFR-PRIV-02 · NFR-CHILD-02 | FND-10 · U1-07 |
| **F6 Owner and staff management** | US-MGT-01…10 | S10, S11, S12, S13, S14 | NFR-ROLE-01…05 · 03 §4.2 RLS · NFR-SEC-06 · NFR-LOG-01, 02 · NFR-INT-05, 06, 07 · NFR-CHILD-05 | FND-09 · U1-05 · U2-06 · U3-01…07 |
| **All features** | — | S16 system states | NFR-REL-04 · NFR-UX-01…04 · NFR-MNT-01…03 · NFR-TST-01, 02 · NFR-ENV-01…05 | Foundation + REL-02…07 |

## 12. Definition of done

Stage 1 is complete when the designer can produce the deliverables in 02 §10, developers can build every user story, and every open question in §9 is answered (or its default accepted). The app is complete when all **15 end-to-end scenarios** in [01-product.md Part C](01-product.md#part-c--acceptance-scenarios-end-to-end) pass and the security checklist in [03 §11](03-non-functional-requirements.md#11-security-features-checklist-for-demos) is ticked.

## 13. Glossary

The full list of store terms is in [01 §A8](01-product.md#a8-key-domain-terms). The technical terms are:

| Term | Meaning |
|---|---|
| RLS | Row Level Security: Postgres rules that decide which rows each user can read or change |
| Idempotency key | A unique token that stops one checkout from creating two orders |
| `SECURITY DEFINER` | A database function that runs with extra rights but checks the caller's role itself |
| Pick code | A user's story number in the work plan, for example U2-03 |
| Foundation (FND) | The shared base the Tech Lead builds before the stories start |

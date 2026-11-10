# 03 — Non-Functional Requirements: KeyGuard Local

> Part of the KeyGuard Local requirement set. See [00-consolidated-requirements.md](00-consolidated-requirements.md).
> Stack: Streamlit (Python), Supabase (Postgres, Auth, Storage), deployed to Streamlit Community Cloud.
> Priority: **M** = Mandatory, **S** = Should, **C** = Could. This is a learning and demo app, but it follows real security practices so they can be taught.

## 1. Authentication (sign-in)

| ID | Pri | Requirement |
|---|---|---|
| NFR-AUTH-01 | M | All accounts (customer, staff and owner) use **Supabase Auth email/password**. The app never stores or hashes passwords itself, because Supabase stores them with bcrypt. |
| NFR-AUTH-02 | M | Password rules: **at least 8 characters, with at least one letter and one number**, and a maximum of 72 (the bcrypt limit). These are also set as Supabase Auth's minimum password rules, so they are enforced on the server and not only in the form. |
| NFR-AUTH-03 | M | Error messages never reveal whether an account exists. Sign-in shows "Email or password is incorrect". Registration with an email already in use shows a neutral message. |
| NFR-AUTH-04 | M | Email confirmation is **disabled** in the Supabase project for the demo, so that no real email is sent. This is documented in `docs/deployment/`. |
| NFR-AUTH-05 | M | Brute-force protection: after 5 failed sign-ins within a session, the form locks for 5 minutes with a countdown. Supabase's built-in auth rate limits stay switched on as the server-side backstop. |
| NFR-AUTH-06 | M | Checkout and My Account require an authenticated session. Each page checks this on every run. |
| NFR-AUTH-07 | S | Changing a password requires the current password (checked by signing in again) before `update_user` is called. |
| NFR-AUTH-08 | C | Password reset by email is **not implemented** in the demo (see US-AUTH-05). |

## 2. Sessions

| ID | Pri | Requirement |
|---|---|---|
| NFR-SES-01 | M | Supabase access and refresh tokens are held **only** in `st.session_state`, never in query params, cookies set by the app, logs or files. |
| NFR-SES-02 | M | Every request to Supabase as the user is made with the user's access token, so that RLS applies to that user. A shared, logged-in client is **never** kept in `st.cache_resource`, because Streamlit shares cached resources between all users. |
| NFR-SES-03 | M | Sign out calls `auth.sign_out()` and clears tokens, the user and the role from the session, while keeping the cart. |
| NFR-SES-04 | S | After 30 minutes without activity the session expires. Staff and owners are then sent to Sign in. Customers keep their cart and are asked to sign in again at checkout. |
| NFR-SES-05 | S | Expired access tokens are refreshed silently using the refresh token. If refreshing fails, the user is signed out. |

## 3. Authorization (roles)

| ID | Pri | Requirement |
|---|---|---|
| NFR-ROLE-01 | M | There are three roles, stored in `profiles.role`: `customer` (the default), `staff` and `owner`. The permission matrix is in 01-product, Part B. |
| NFR-ROLE-02 | M | **Defense in depth:** (1) the navigation hides pages a role can't use; (2) every page checks the role at the top and stops with `st.stop()`; (3) Postgres RLS and function checks enforce the same rules. Layer 3 is the one that truly protects the data. |
| NFR-ROLE-03 | M | The role is read from the database (`profiles`) after sign-in, never from anything the user typed or the URL. |
| NFR-ROLE-04 | M | Users cannot change their own role. The `profiles.role` column can only be changed by the `set_user_role(target uuid, new_role text)` function, which checks that the caller is the owner, refuses to let the owner change their own role and refuses `new_role = 'owner'`. |
| NFR-ROLE-05 | M | The first owner account is set up once by hand with SQL in the Supabase dashboard, as documented in `supabase/seed/`. |

## 4. Data security (Supabase / Postgres)

### 4.1 Data model

```sql
profiles (id uuid pk references auth.users on delete cascade,
          full_name text, role text not null default 'customer'
          check (role in ('customer','staff','owner')), created_at timestamptz default now())
          -- created by trigger on auth.users insert (role always 'customer')

products (id uuid pk, sku text unique not null, name text not null,
          category text check (category in ('Essentials','Pro','Community','Bulk','Accessories')),
          capacity_gb int, color text, description text, specs jsonb default '{}',
          price_cents int not null check (price_cents > 0),
          community_gift_cents int not null default 0 check (community_gift_cents >= 0),
          stock_qty int not null default 0 check (stock_qty >= 0),
          image_url text, is_active boolean default true, featured_rank int default 100,
          created_at timestamptz default now(), updated_at timestamptz default now())

orders (id uuid pk, order_number text unique not null,
        customer_id uuid not null references auth.users,
        customer_name text, customer_email text, address text, city text, zip text,
        subtotal_cents int, shipping_cents int, tax_cents int, total_cents int,
        community_gift_cents int,
        status text default 'Placed' check (status in ('Placed','Packed','Shipped','Cancelled')),
        idempotency_key uuid unique, email_file text, created_at timestamptz default now())

order_items (id uuid pk, order_id uuid references orders on delete cascade,
             product_id uuid references products, sku text, product_name text,
             unit_price_cents int, qty int check (qty between 1 and 10),
             community_gift_cents int, line_total_cents int)

inventory_log (id, product_id, delta int, reason text, order_id uuid null, actor uuid, created_at)
audit_log     (id, actor uuid, action text, target text, details jsonb, created_at)
```

### 4.2 Row Level Security (RLS is on for every table)

| Table | Guest (anon) | Customer | Staff | Owner |
|---|---|---|---|---|
| products | SELECT active | SELECT active | SELECT all; UPDATE stock, description, specs, image, active (**not** price or gift; enforced by a trigger or a column-limited RPC) | ALL |
| orders | — | SELECT own (`customer_id = auth.uid()`) | SELECT all; UPDATE status → Packed/Shipped | SELECT all; UPDATE status incl. Cancelled |
| order_items | — | SELECT own (via order) | SELECT all | SELECT all |
| profiles | — | SELECT/UPDATE own `full_name` only | SELECT all | SELECT all; role only via `set_user_role` |
| inventory_log | — | — | SELECT, INSERT (own actor) | SELECT |
| audit_log | — | — | — | SELECT |

### 4.3 Database functions

| ID | Pri | Requirement |
|---|---|---|
| NFR-DB-01 | M | `place_order(items jsonb, shipping jsonb, idempotency_key uuid)` is `SECURITY DEFINER` with `SET search_path = public`. It takes the customer from `auth.uid()`, rejects anonymous callers, **recalculates every price and total on the server** (never trusting prices sent by the client), locks rows with `SELECT … FOR UPDATE` and runs as one transaction. |
| NFR-DB-02 | M | `cancel_order(order_id)` (owner only) restocks the items and logs the change. `set_user_role(...)` (owner only) logs to `audit_log`. |
| NFR-DB-03 | M | Every `SECURITY DEFINER` function checks the caller's role inside the function and has `EXECUTE` revoked from `public` and granted only to `authenticated`. |
| NFR-DB-04 | M | All money is stored as integer cents. Check constraints stop stock from going negative and prices from being zero or less. |

## 5. Application security

| ID | Pri | Requirement |
|---|---|---|
| NFR-SEC-01 | M | **Secrets:** the Supabase URL and **anon key** live in `.streamlit/secrets.toml` (git-ignored) or in Streamlit Cloud secrets. The **service-role key is never used** in the app or committed. |
| NFR-SEC-02 | M | **No payment data:** the app has no card fields, so PCI-DSS doesn't apply. Code review must reject any payment field. |
| NFR-SEC-03 | M | **Input validation** on both client and server: email format, name 2–80 characters, ZIP `^\d{5}$`, SKU `^[A-Z0-9-]{3,20}$`, whole-number quantities from 1 to 10, and prices or stock within range. Database constraints back up the UI checks. |
| NFR-SEC-04 | M | **Injection:** only the supabase-py query builder or RPC parameters are used. SQL is never built from strings. |
| NFR-SEC-05 | M | **XSS:** `unsafe_allow_html=True` is allowed **only** for the app's own static CSS and layout markup. User or product text is never rendered as HTML, and the HTML email body escapes every value (`html.escape`). |
| NFR-SEC-06 | M | **File uploads:** PNG or JPG only, checked by both extension and file signature (magic bytes), 2 MB or smaller. Files get a random name (`<uuid>.png`). Only staff and owners can upload, enforced by a Storage bucket policy. The bucket is public-read and authenticated staff/owner-write. |
| NFR-SEC-07 | M | **Outbox files:** filenames are cleaned to `[A-Za-z0-9._@-]` so a filename can never point outside `outbox/`, and `outbox/` is git-ignored. |
| NFR-SEC-08 | M | **Error handling:** users see friendly messages. Stack traces and raw database errors appear only in server logs. `client.showErrorDetails = false` is set in `config.toml` for deployment. |
| NFR-SEC-09 | S | **Dependencies:** versions are pinned in `requirements.txt`, and `pip-audit` is run before each release. |

## 6. Privacy and child safety

Training groups may include minors, so these rules protect learners as well as demo customers.

| ID | Pri | Requirement |
|---|---|---|
| NFR-PRIV-01 | M | Demo data only. The register and checkout pages tell users to use `@example.com` addresses and made-up addresses. |
| NFR-PRIV-02 | M | Only the data needed is collected: name, email and shipping address. No date of birth, phone number or payment details. |
| NFR-PRIV-03 | M | Customers can see only their own orders and profile (RLS). |
| NFR-PRIV-04 | S | A reset script (`supabase/seed/reset_demo.sql`) clears all customer accounts, orders and outbox files between training sessions. |
| NFR-CHILD-01 | M | **No public user-generated content.** There are no reviews, comments, chat, profile photos or public profiles, so learners cannot post or see content from strangers. |
| NFR-CHILD-02 | M | **No age or identity data.** The app never asks for age, date of birth, school, phone number, photos or location. Names may be made up (for example "Demo Student 3"). |
| NFR-CHILD-03 | M | **Age-appropriate content everywhere:** product copy, images, seed data, error messages and sample emails. No fear-based security marketing (see NFR-UX-03). |
| NFR-CHILD-04 | M | **No tracking or advertising.** No analytics, ad scripts, third-party cookies or tracking pixels. The only external resources allowed are Google Fonts and the Supabase project. |
| NFR-CHILD-05 | M | **Only staff and owners can upload images** (NFR-SEC-06). The instructor or Tech Lead checks every uploaded image before a session with learners. |
| NFR-CHILD-06 | S | **Supervised accounts:** in classes with minors, the instructor holds the owner account and creates staff accounts. Learners register only as customers with `@example.com` addresses. |
| NFR-CHILD-07 | M | **Nothing real is sent.** No real email, payment or shipping ever happens (US-CHK-04), so a learner can't accidentally contact or charge anyone. |

## 7. Logging and audit

| ID | Pri | Requirement |
|---|---|---|
| NFR-LOG-01 | M | Every stock change (order, staff/owner edit, cancellation) writes `inventory_log`. |
| NFR-LOG-02 | M | Product create, delete and price changes, order cancellations and role changes write `audit_log` (actor, action, target, details). |
| NFR-LOG-03 | M | Logs never contain passwords, tokens or full addresses. |

## 8. Performance, reliability and error handling

| ID | Pri | Requirement |
|---|---|---|
| NFR-PERF-01 | M | The catalog loads in under 2 s with 100 products. Public product reads use `st.cache_data(ttl=30)`, cleared after edits and orders. User-specific data is never cached across users. |
| NFR-PERF-02 | M | Placing an order takes under 3 s from the server's point of view. |
| NFR-REL-01 | M | Checkout is all-or-nothing and can't create duplicate orders (NFR-DB-01, idempotency key). |
| NFR-REL-02 | M | If the email file can't be written, the order still succeeds and is flagged (US-CHK-04). |
| NFR-REL-03 | S | The app shows a friendly "Store temporarily unavailable" page if Supabase can't be reached. |
| NFR-REL-04 | M | **Error handling:** every service call is wrapped so that the user sees a plain message and a "Try again" button (02-ui-ux §5), while the technical details go only to the server log (NFR-SEC-08). Form values typed by the user are kept after an error. |
| NFR-REL-05 | M | **No false success:** the confirmation page, the toast and the cleared cart appear only after the database has confirmed the order. |

## 9. Usability, accessibility and content

| ID | Pri | Requirement |
|---|---|---|
| NFR-UX-01 | M | Meets WCAG 2.1 AA. Color is never the only signal. Every form field has a visible label (02-ui-ux §6). |
| NFR-UX-02 | M | **Motion safety:** nothing flashes more than 3 times a second, the gradient cycles in 8 s or more, and all animation respects `prefers-reduced-motion`. |
| NFR-UX-03 | M | All copy, images and seed data are **age-appropriate**, because training audiences include minors. |
| NFR-UX-04 | S | Works on current Chrome, Edge, Firefox and Safari, from 360 px width up to desktop. |

## 10. Maintainability, testing and deployment

| ID | Pri | Requirement |
|---|---|---|
| NFR-MNT-01 | M | Layering: `pages/` hold UI only, `components/` hold reusable widgets, and `services/` handle Supabase access (`auth.py`, `products.py`, `orders.py`, `users.py`, `email_outbox.py` and others). `utils/` holds pure helpers (`pricing.py`, `cart.py`, `session.py`, `guards.py` with `require_role(...)`), and `validation/` holds input checks per area. The full file list is in the work division plan. |
| NFR-MNT-03 | M | **Code quality:** code is formatted and linted with `ruff`, public functions have type hints and a one-line docstring, there are no unused imports, and nothing is debugged with `print`. CI enforces the formatting and linting. |
| NFR-MNT-02 | M | The database schema, RLS, functions and seed data live as numbered SQL files in `supabase/migrations/` and `supabase/seed/`. |
| NFR-TST-01 | M | pytest unit tests cover pricing (shipping threshold, tax rounding), cart operations, validation, filename cleaning and `.eml` generation. |
| NFR-TST-02 | M | Integration tests against a test Supabase project check that `place_order` reduces stock and blocks overselling, and that RLS blocks: a customer reading another customer's orders, staff changing a price, and a non-owner calling `set_user_role`. |
| NFR-DEP-01 | M | Deployment is on Streamlit Community Cloud, with secrets in the Cloud secrets UI. Because the file system there is temporary, emails in `outbox/` are lost on restart, and the download button is how the email is shown in a demo. |
| NFR-DEP-02 | S | `docs/deployment/` explains the Supabase setup (migrations, disabling email confirmation, creating the owner and Storage bucket) and the Streamlit Cloud steps. |

## 11. Security features checklist (for demos)

Use this list to show trainees how the app's security reflects the drives' security story:

- [ ] Passwords hashed by Supabase (bcrypt). The app never sees stored passwords.
- [ ] Generic sign-in errors, plus a 5-attempt lockout (the "10-try wipe" idea, applied to the website).
- [ ] Three roles with permissions enforced in the UI, on each page and in RLS.
- [ ] Server-side price recalculation and an all-or-nothing checkout.
- [ ] No payment data collected.
- [ ] Secrets kept out of git, and only the anon key used.
- [ ] Audit log for sensitive owner actions.
- [ ] Validated and safely named uploads and outbox files.

## 12. Data integrity

These rules make sure the store's numbers are always right, even when two people click at the same moment.

| ID | Pri | Requirement |
|---|---|---|
| NFR-INT-01 | M | **No overselling USB drives.** `place_order` locks the product rows (`SELECT … FOR UPDATE`) before checking stock. `CHECK (stock_qty >= 0)` is a final safety net. Tested in NFR-TST-02. |
| NFR-INT-02 | M | **No double orders.** Each checkout sends an idempotency key, and `orders.idempotency_key` is `UNIQUE`. A repeated submit returns the first order instead of creating a second. |
| NFR-INT-03 | M | **Prices frozen at purchase.** `order_items` stores the product name, unit price and community gift at the moment of the order, so later price edits never change past orders. |
| NFR-INT-04 | M | **Exact money.** All amounts are integer cents. Tax is rounded once per order (half-up to the nearest cent), and totals are always recalculated on the server. |
| NFR-INT-05 | M | **Linked records stay consistent.** Foreign keys connect every order item to an order and a product. A product that has been ordered cannot be deleted (`ON DELETE RESTRICT`); it is deactivated instead. |
| NFR-INT-06 | M | **Stock and its log change together.** Every stock change and its `inventory_log` row are written in the same transaction, so the log always explains the current stock. |
| NFR-INT-07 | M | **Valid order status changes only:** Placed → Packed → Shipped, or Placed/Packed → Cancelled. A Shipped or Cancelled order can't change again. This is enforced in the database. |
| NFR-INT-08 | M | **Unique identifiers.** SKU, order number and the user's email are unique, enforced by database constraints and not only by the form. |

## 13. Scalability limits

This is a classroom demo, so the targets are deliberately small. These limits are **by design**, not defects.

| ID | Limit | Target |
|---|---|---|
| NFR-SCALE-01 | Products | Up to 200 |
| NFR-SCALE-02 | People using the app at the same time | Up to 50 (a class plus instructors) |
| NFR-SCALE-03 | Orders | Up to 5,000 before running `reset_demo.sql` |
| NFR-SCALE-04 | Product images | Up to 200 images of 2 MB or less each |
| NFR-SCALE-05 | Hosting | Fits the **free tiers** of Supabase and Streamlit Community Cloud. Check their current limits before a course starts, because providers change them. Free projects may pause or sleep when unused, so open the app before each class. |

**Not designed for:** many servers, high traffic, real payments, a content delivery network or multiple regions. Moving to real production would need a new design review.

## 14. Environments and deployment

| ID | Pri | Requirement |
|---|---|---|
| NFR-ENV-01 | M | **Dev environment:** a Supabase project shared by the team for daily work, with seed data. Each environment has its **own Supabase project and keys**. |
| NFR-ENV-01a | M | **Test environment:** a separate Supabase project used only by integration tests and CI, and reset before each run. |
| NFR-ENV-01b | M | **Demo environment:** the deployed app on Streamlit Community Cloud, with its own Supabase project. |
| NFR-ENV-02 | M | **Configuration by environment:** the app reads its Supabase URL and anon key from `.streamlit/secrets.toml` locally, or from the Streamlit Cloud secrets UI. Scripts and tests read them from `.env`. Only the `.example` versions of these files are committed. |
| NFR-ENV-03 | M | **Same migrations everywhere:** migration files are applied in number order to Dev, then Test, then Demo. Nobody changes a database by hand in the dashboard, except creating the first owner (NFR-ROLE-05). |
| NFR-ENV-04 | M | **Seed data:** Dev and Test get the full seed data, including demo accounts and orders. Demo gets products and the owner account only, plus `reset_demo.sql` between classes. |
| NFR-ENV-05 | S | **Release tag:** the Demo environment is deployed only from a tagged `main` commit (for example `v1.0`). |

## 15. Constraints and assumptions

### 15.1 Constraints (fixed and can't change)

| # | Constraint |
|---|---|
| C1 | **Technology:** Streamlit (Python) for the app, Supabase for the database, sign-in and file storage, and Streamlit Community Cloud for hosting. |
| C2 | **Streamlit's model:** the whole page re-runs on every click, styling is limited to the theme plus custom CSS, and there are no custom JavaScript components (see 02-ui-ux §14). |
| C3 | **Budget:** $0. Only free tiers are used. |
| C4 | **Team and time:** 1 Tech Lead + 3 participants over 5 weeks (see the work division plan). |
| C5 | **Demo rules:** no real payments, no real email, no real shipping and no real customer data. |
| C6 | **Audience:** training groups may include minors (§6). |

### 15.2 Assumptions (believed true; check them, and update this document if one turns out wrong)

| # | Assumption | If it turns out wrong |
|---|---|---|
| A1 | Users have a current desktop or phone browser and a stable internet connection. | Add a "minimum browser" note to the README. |
| A2 | The instructor creates the first owner account and any staff accounts. | Add a documented one-time setup script. |
| A3 | Everyone uses `@example.com` emails and made-up names and addresses. | Run `reset_demo.sql` and remind the class. |
| A4 | **KeyGuard Local, Riverton and the Riverton Library fund are fictional.** The drive specs (AES-256, 10-try wipe and so on) are demo marketing copy, not verified product claims. | Label the specs "demo copy" on the product page. |
| A5 | Supabase and Streamlit free tiers remain available with similar limits. | Review §13 and the hosting choice. |
| A6 | The class has 5 weeks for the build. | Drop the Could-have stories first (work division plan §5). |

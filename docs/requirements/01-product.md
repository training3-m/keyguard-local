# 01 — Product Features and User Stories: KeyGuard Local

> Part of the KeyGuard Local requirement set. See [00-consolidated-requirements.md](00-consolidated-requirements.md).
> Purpose: learning and demo. The company, the city ("Riverton") and the products are fictional.
> Priority: **M** = Mandatory, **S** = Should, **C** = Could.

---

## Part A — The product

### A1. Product summary

**KeyGuard Local** is a small online store that sells **hardware-secured USB flash drives**. Each drive has a **physical PIN keypad** on the casing. Until the right PIN is typed on the stick, the drive does not show up on a computer. Encryption runs inside the drive, so it works on any computer and needs no software.

A fixed amount from every drive sold goes to the **Riverton Public Library Digital Safety Fund**, which runs free classes on password safety and data privacy in Riverton (a fictional city).

**Tagline:** *Lock it. Carry it. Give back locally.*

### A2. Problem and value

| Problem | How KeyGuard helps |
|---|---|
| Lost USB sticks expose school, business or personal files | Data stays locked without the PIN. Too many wrong attempts wipes the drive. |
| Software encryption is confusing and depends on the computer | The keypad works on any computer with no install. |
| People want purchases to help their community | Every drive funds local digital-safety classes, and the store shows the running total. |

### A3. Personas

| Persona | Role in app | Need |
|---|---|---|
| **Sam, student / teacher** | Customer | Carry assignments safely between home and school |
| **Priya, small-business owner** | Customer | Move client files without leaks, and buy in bulk |
| **Kim, store staff** | Staff | Keep stock and product info up to date, and pack and ship orders |
| **Jordan, store owner** | Owner | Run the store: pricing, catalog, staff, results |

### A4. Drive features (marketing copy for all drives)

- 10-key physical keypad plus a lock key, with LED status (red = locked, green = unlocked, blue = admin).
- PIN length of 7–15 digits. Hardware AES-256 encryption, described to shoppers as "bank-grade".
- The drive wipes itself after 10 wrong PINs, and locks itself when unplugged or idle.
- Read-only mode. USB-C connector with a USB-A adapter. Aluminium casing. 3-year warranty.

> **Fictional product:** KeyGuard Local is not a real product. These features are demo marketing copy for training, not verified or certified security claims (see 03 §15, assumption A4).

### A5. Catalog (seed data)

| SKU | Name | Category | Capacity | Color | Price | Community gift | Stock |
|---|---|---|---|---|---|---|---|
| KG-ESS-16 | KeyGuard Essentials 16 GB | Essentials | 16 GB | Slate Grey | $49.00 | $2.00 | 40 |
| KG-ESS-32 | KeyGuard Essentials 32 GB | Essentials | 32 GB | Slate Grey | $59.00 | $2.00 | 35 |
| KG-PRO-64 | KeyGuard Pro 64 GB | Pro | 64 GB | Midnight Black | $79.00 | $3.00 | 25 |
| KG-PRO-128 | KeyGuard Pro 128 GB | Pro | 128 GB | Midnight Black | $99.00 | $4.00 | 20 |
| KG-PRO-256 | KeyGuard Pro 256 GB | Pro | 256 GB | Midnight Black | $139.00 | $5.00 | 10 |
| KG-RCE-32 | Riverton Community Edition 32 GB | Community | 32 GB | River Blue (skyline engraving) | $65.00 | $10.00 | 30 |
| KG-RCE-64 | Riverton Community Edition 64 GB | Community | 64 GB | River Blue (skyline engraving) | $85.00 | $12.00 | 15 |
| KG-BULK-5 | Essentials 32 GB — 5-Pack | Bulk | 5 × 32 GB | Slate Grey | $269.00 | $12.00 | 8 |
| KG-ACC-LAN | KeyGuard Lanyard & Cap Set | Accessories | — | Mixed | $9.00 | $0.50 | 60 |
| KG-ACC-CASE | Hard-Shell Travel Case | Accessories | — | Black | $15.00 | $0.50 | 45 |

The seed data also includes an **inactive** product, `KG-ESS-8` (discontinued), and three demo accounts: `owner@example.com` (owner), `staff@example.com` (staff) and `customer@example.com` (customer).

### A6. Business rules

| Rule | Value |
|---|---|
| Currency | USD, stored as integer cents |
| Shipping | $4.99 flat. **Free** when the subtotal is $75 or more. |
| Tax | 8% of the subtotal (demo) |
| Quantity per line | 1 – min(10, stock) |
| Payment | **None.** No card or payment fields exist anywhere. |
| Community gift | Σ (gift per unit × qty) |
| Order number | `KG-YYYYMMDD-NNNN` (daily sequence) |
| Low stock | 5 units or fewer |
| Checkout | **Requires a signed-in account** |

### A7. Out of scope

Real payments, real email delivery, real shipping or tax, social login, multiple currencies, product reviews, and gamification for shoppers (points, XP, levels, badges). "Gaming" refers to the visual style only (02-ui-ux §8).

### A8. Key domain terms

| Term | Meaning in this store |
|---|---|
| **Drive** | One keypad-locked USB flash drive (a product). Accessories are products too. |
| **SKU** | The product's unique code, for example `KG-PRO-64` |
| **Line** | Essentials, Pro, Community, Bulk or Accessories (the `category` field) |
| **Active / inactive** | Active products show in the shop. Inactive ones are hidden but kept for order history. |
| **Stock** | How many units can still be sold (`stock_qty`). It never goes below 0. |
| **Low stock** | 5 units or fewer. Shown on the dashboard and as "Only N left". |
| **Cart** | The shopper's chosen products and quantities, kept in the browser session until checkout |
| **Order** | A confirmed demo purchase with a number like `KG-20261102-0007`. No money changes hands. |
| **Order status** | Placed → Packed → Shipped, or Cancelled |
| **Community gift** | The fixed amount per unit sent to the fictional Riverton Library Digital Safety Fund |
| **Outbox** | The folder where `.eml` confirmation emails are saved instead of being sent |
| **Guest / Customer / Staff / Owner** | The four roles (Part B role matrix) |
| **Security HUD** | The game-style panel showing a drive's security features as stat bars |
| **Lockout** | The website's sign-in lock after 5 wrong passwords, echoing the drive's 10-try wipe |

---

## Part B — Features and user stories

Each story has an ID (`US-<feature>-NN`), a priority and acceptance criteria (AC).

### Roles and permissions summary

| Capability | Guest | Customer | Staff | Owner |
|---|---|---|---|---|
| Browse, search, view details | ✅ | ✅ | ✅ | ✅ |
| Add to cart | ✅ | ✅ | ✅ | ✅ |
| Check out | ❌ (must sign in) | ✅ | ✅ | ✅ |
| My Account / My orders | — | ✅ | ✅ | ✅ |
| View all products, including inactive | — | — | ✅ | ✅ |
| Edit stock, description, specs, image, active flag | — | — | ✅ | ✅ |
| Create or delete products, edit price or community gift | — | — | ❌ | ✅ |
| View all orders and set Packed / Shipped | — | — | ✅ | ✅ |
| Cancel an order (restocks it) | — | — | ❌ | ✅ |
| Dashboard: revenue and community totals | — | — | ❌ | ✅ |
| Promote or demote staff | — | — | ❌ | ✅ |

---

### F1. Add to cart

**US-CART-01 (M)** As a shopper, I want to add a drive to my cart from its detail page so that I can buy it later.
- AC1: The quantity picker allows 1 – min(10, stock). Clicking **Add to cart** shows a toast and increases the cart badge.
- AC2: Adding a SKU that is already in the cart increases its quantity, capped at min(10, stock), and the shopper is told when the cap applies.
- AC3: Out-of-stock or inactive products cannot be added, and the button reads "Out of stock".
- AC4: Guests can add to the cart. The cart lives in `st.session_state["cart"]` as `{sku: qty}`.

**US-CART-02 (M)** As a shopper, I want to view and change my cart so that I can adjust what I'm buying.
- AC1: Each line shows the image, name, unit price, a quantity stepper, the line total and a remove button.
- AC2: Totals (subtotal, shipping, tax, total, community gift) are recalculated from **current database prices** whenever the cart changes.
- AC3: Lines over the available stock are capped and a warning is shown. Lines that are out of stock or inactive are flagged and block checkout.
- AC4: An empty cart shows an empty state, and Checkout is disabled.

**US-CART-03 (S)** As a shopper, I want to know how close I am to free shipping so that I can decide whether to add more.
- AC1: When the subtotal is below $75, the cart shows "Add $X more for free shipping".

**US-CART-04 (M)** As a guest, I want my cart kept when I sign in or register so that I don't lose my selection.
- AC1: After sign-in or registration, the session cart is unchanged and the user returns to the page they came from.

### F2. Checkout and order confirmation

**US-CHK-01 (M)** As a shopper, I must be signed in to check out so that the order is linked to my account.
- AC1: A signed-out user who opens Checkout sees the sign-in gate (02-ui-ux §4.5), not the form.
- AC2: After signing in, the user goes back to Checkout with the cart still there.

**US-CHK-02 (M)** As a customer, I want to place an order without a credit card so that I can try the store safely.
- AC1: The form shows the account email (read-only), the full name (filled in from the profile), the address, the city and a 5-digit ZIP, plus an "I understand this is a demo" checkbox.
- AC2: **No card, CVV or payment field exists anywhere in the app.**
- AC3: Validation errors appear inline. While the order is processing, the Place order button is disabled.

**US-CHK-03 (M)** As the store, I want inventory deducted when an order is placed so that stock stays accurate.
- AC1: Place order calls the database function `place_order(items)`. In **one transaction**, it locks the product rows, checks that each item is active and has enough stock, inserts `orders` and `order_items` (with price and name snapshots and `customer_id = auth.uid()`), **subtracts each quantity from `stock_qty`** and writes `inventory_log` rows.
- AC2: If any item lacks stock, nothing changes, and the user is sent back to the cart with the failing items named.
- AC3: An idempotency key (a UUID kept in the session) means a double click creates only one order.
- AC4: When two shoppers try to buy the last unit at the same time, exactly one succeeds.

**US-CHK-04 (M)** As a customer, I want a confirmation email so that I have a record of my order. The email is **saved to a folder, never sent**.
- AC1: After the order is committed, the app writes `outbox/<order_number>_<sanitized-email>.eml` using Python's `email.message.EmailMessage`.
- AC2: The email has From `orders@keyguard-local.example`, To the account email and Subject `Your KeyGuard Local order <order_number>`. It has plain-text and HTML bodies listing the items, quantities, prices, shipping, tax, total, the community gift and a demo disclaimer.
- AC3: The file path is stored in `orders.email_file`. If writing the file fails, the order stays placed and is marked "email not generated".
- AC4: No mail server and no SMTP code exist in the app.

**US-CHK-05 (M)** As a customer, I want an order confirmation page so that I know my order went through.
- AC1: The page shows the order number, items, totals and community gift, and a **Download confirmation email** button.
- AC2: The cart is cleared afterwards.

**US-CHK-06 (S)** As a customer, I want to see my past orders so that I can track them.
- AC1: My Account → My orders lists only **my** orders (number, date, total, status), and each opens its details and email download.

### F3. Product search

**US-SRCH-01 (M)** As a shopper, I want to search drives by keyword so that I can find what I need quickly.
- AC1: Search matches name, SKU, category and description, ignoring case and finding partial matches.
- AC2: Only active products are returned to customers and guests.
- AC3: No results shows `No drives match '<term>'` and a **Clear filters** button.

**US-SRCH-02 (M)** As a shopper, I want to filter by category, capacity, price range and "in stock only" so that I can narrow the results.
- AC1: Filters combine with AND, and the result count updates.

**US-SRCH-03 (S)** As a shopper, I want to sort results by Featured, Price ↑, Price ↓, Capacity or Newest.

**US-SRCH-04 (C)** As a shopper, I want the search and filters saved in the URL so that I can share a filtered view.

### F4. Product detail

**US-PDP-01 (M)** As a shopper, I want a detailed product page so that I understand what I'm buying.
- AC1: The page shows the image, name, SKU, category, price, stock badge, community gift, description, a specs table, the **Security HUD**, and the tabs Overview / Specs / How the keypad works / Community.
- AC2: It loads from `?sku=`. An unknown or inactive SKU shows "Product not found" and a link back to the Shop.

**US-PDP-02 (C)** As a shopper, I want "You may also like" suggestions: up to 3 active products from the same category.

### F5. Customer register and sign in

**US-AUTH-01 (M)** As a new visitor, I want to register so that I can check out and see my orders.
- AC1: Fields are full name (2–80 characters), email, password, confirm password and the demo checkbox.
- AC2: Passwords follow NFR-AUTH-02 and are checked as the user types.
- AC3: Registering an email that is already used gives a general message that doesn't confirm the account exists, and the user is offered Sign in.
- AC4: New accounts always get the role `customer`. A user can never choose or change their own role.
- AC5: After registering, the user is signed in. For the demo, Supabase email confirmation is turned off so no real email is sent.

**US-AUTH-02 (M)** As a registered user, I want to sign in so that I can check out and reach my account.
- AC1: A failed sign-in always says "Email or password is incorrect".
- AC2: After 5 failed attempts the form locks for 5 minutes and shows a countdown (NFR-AUTH-05).
- AC3: Customers return to the page they came from. Staff and owners land on the Dashboard.

**US-AUTH-03 (M)** As a signed-in user, I want to sign out so that others on the same computer can't use my account.
- AC1: Sign out ends the Supabase session, clears the auth and role data from `st.session_state` and keeps the cart.

**US-AUTH-04 (S)** As a customer, I want to edit my name and change my password.
- AC1: Changing the password requires the current password, and the new one must meet NFR-AUTH-02.

**US-AUTH-05 (C)** As a user, I want to reset a forgotten password.
- AC1: This is not built for the demo because it would need real email. The page shows "Contact the store owner" instead.

### F6. Owner and staff pages to manage products

**US-MGT-01 (M)** As staff or the owner, I want a Manage section that only we can reach so that customers can't change the store.
- AC1: Manage pages appear in the navigation only for `staff` and `owner`.
- AC2: Every Manage page checks the role on the server side. Anyone else sees "Staff access only".
- AC3: Database RLS enforces the same rules, so getting around the UI doesn't help (NFR-SEC-01).

**US-MGT-02 (M)** As staff or the owner, I want to see all products, including inactive ones, and search them by name or SKU.

**US-MGT-03 (M)** As the owner, I want to create a product.
- AC1: Fields: SKU (unique, `^[A-Z0-9-]{3,20}$`), name, category, capacity, color, description, specs, price (> 0), community gift (0 ≤ gift ≤ price), stock (integer ≥ 0), image and active flag.

**US-MGT-04 (M)** As staff or the owner, I want to edit products in bulk (`st.data_editor`) with a single Save.
- AC1: Staff can edit stock, description, specs, image and active. Price and gift are **read-only** for staff.
- AC2: The owner can edit every field except the SKU.
- AC3: Every stock change writes an `inventory_log` row (actor, change, reason).

**US-MGT-05 (M)** As staff or the owner, I want to deactivate and reactivate products so that discontinued items disappear from the shop without losing their history.

**US-MGT-06 (S)** As the owner, I want to delete a product that has **never been ordered**, after typing its SKU to confirm. Otherwise I'm told to deactivate it instead.

**US-MGT-07 (S)** As staff or the owner, I want to upload a product image (PNG or JPG, 2 MB or smaller) to the Supabase Storage bucket `product-images`.

**US-MGT-08 (M)** As staff or the owner, I want a dashboard so that I can see how the store is doing.
- AC1: Everyone in the Manage section sees order count, units sold, the low-stock list (≤ 5) and the last 10 orders.
- AC2: **Owner only:** revenue and community-gift totals.

**US-MGT-09 (S)** As staff or the owner, I want to manage orders.
- AC1: An orders table with date and status filters, and an order detail view with an email download.
- AC2: Staff can set `Placed → Packed → Shipped`.
- AC3: **Owner only:** **Cancel**, which puts the stock back (and logs it).

**US-MGT-10 (M)** As the owner, I want to promote a registered customer to staff, or demote staff back to customer.
- AC1: This is done by calling the `set_user_role` database function, which only owners can run. The owner cannot change their own role, and there is no way to create a second owner in the UI.
- AC2: Every role change is written to `audit_log`.

---

## Part C — Acceptance scenarios (end-to-end)

1. **Search:** searching "pro" shows only the Pro drives.
2. **Detail:** `?sku=KG-PRO-64` shows $79.00, "In stock (25)" and the Security HUD.
3. **Cart:** adding 2 × KG-PRO-64 makes the badge show 2 and the subtotal $158.00.
4. **Totals:** a subtotal of $167.00 gives FREE shipping, $13.36 tax and a $180.36 total.
5. **Sign-in gate:** a guest opening Checkout sees the gate. After signing in, the cart is still there.
6. **Checkout:** a signed-in customer orders 2 × KG-PRO-64. Stock goes from 25 to 23, the order is created, `outbox/<order>_<email>.eml` exists with the order number and total, and the cart is empty.
7. **Oversell:** with stock 1 and two buyers at the same time, exactly one order succeeds.
8. **No payment:** no page has any card or payment field.
9. **Register:** a new account gets the role `customer` and is signed in.
10. **Lockout:** after 5 bad passwords the form locks for 5 minutes.
11. **Guard:** a customer opening a Manage URL sees "Staff access only", and a direct database write is refused.
12. **Staff limits:** staff can change stock but not price, and cannot see Cancel or Staff & Users.
13. **Deactivate:** a deactivated product disappears from search, and its URL shows "Product not found".
14. **Cancel:** the owner cancels an order of 2 × KG-PRO-64, stock goes up by 2 and the change is logged.
15. **Role change:** the owner promotes Sam to staff, Sam sees Manage on the next sign-in, and the change is in `audit_log`.

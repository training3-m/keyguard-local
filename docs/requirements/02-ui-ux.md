# 02 — UI / UX Design: KeyGuard Local

> Part of the KeyGuard Local requirement set. See [00-consolidated-requirements.md](00-consolidated-requirements.md).
> The app is built with Streamlit, so this design works within Streamlit's layout primitives: `st.columns`, `st.container(border=True)`, `st.tabs`, `st.form`, `st.dialog`, `st.toast`, `st.navigation` / `st.Page`, plus light custom CSS in `assets/styles/`.

## 1. Design goals and principles

1. **Gaming-grade look.** The store has a dark, high-energy look inspired by gaming hardware: near-black surfaces, neon edge lighting, RGB gradients and angled "tech" shapes. It must feel like premium gaming gear while staying an **original** brand. Do not use any real company's logo, trademark, exact brand color or product names.
2. **Security is the hero.** RGB effects exist to draw the eye to the security features: the keypad, the encryption, the auto-wipe and the locked/unlocked state. Every product view gives these features pride of place.
3. **Shoppers reach checkout in 3 clicks or fewer:** Product → Add to cart → Checkout.
4. **Local pride.** The community contribution shows on every main screen.
5. **Readable and safe for everyone.** Even with the neon styling, the site meets WCAG 2.1 AA contrast, uses large tap targets and never relies on color alone. Animations are slow and never flash (see §6).

### 1.1 Aesthetic in one line

> *"A locked vault lit by RGB."* Black, glass-like panels with glowing cyan-to-magenta-to-green edges. The lock-state colors (red = locked, green = unlocked) are the same as the LEDs on the real drive.

## 2. Visual style

### 2.1 Color tokens

The site is **dark-first**. Dark mode is the default and the main design. A light theme is optional and can be skipped for the demo.

| Token | Dark (default) | Light (optional) | Use |
|---|---|---|---|
| `bg` | `#07080C` (Void Black) | `#F3F5F9` | Page background |
| `surface` | `#10131B` | `#FFFFFF` | Cards, panels |
| `surface-raised` | `#171B26` | `#EEF1F6` | Hover cards, dialogs, sidebar |
| `border` | `#232838` | `#D5DAE3` | Default card edge (before glow) |
| `primary` | `#00E5FF` (Neon Cyan) | `#007C99` | Primary buttons, links, active nav, focus ring |
| `accent` | `#39FF88` (Unlock Green) | `#138A4B` | "In stock", success, unlocked state, community badge |
| `secure` | `#B04CFF` (Cipher Violet) | `#7A2BC2` | Security-feature highlights, encryption badges |
| `locked` | `#FF3B5C` (Lock Red) | `#C0283F` | Locked state, out of stock, delete, errors |
| `warning` | `#FFB020` | `#A86A00` | Low stock |
| `text` | `#E8ECF4` | `#121722` | Body text |
| `muted` | `#8C95A8` | `#5A6477` | Secondary text |

**RGB gradient (signature):** `linear-gradient(90deg, #00E5FF, #B04CFF, #FF3BD4, #39FF88)`. It is used **only** on accents: glowing card edges, the header underline, the hero headline and the primary CTA border. It never sits behind body text.

**Glow:** `box-shadow: 0 0 12px rgba(0,229,255,.35)` at rest, rising to `0 0 24px rgba(0,229,255,.6)` on hover or focus. Locked and unlocked states use red and green glows.

Set the base theme in `.streamlit/config.toml`: `base="dark"`, `primaryColor="#00E5FF"`, `backgroundColor="#07080C"`, `secondaryBackgroundColor="#10131B"`, `textColor="#E8ECF4"`. Put the glow, gradient and animation effects in `assets/styles/theme.css`, loaded once with `st.markdown("<style>…</style>", unsafe_allow_html=True)`.

**Contrast check:** cyan, green, violet and red text on `#07080C` all pass 4.5:1 for normal text. Muted grey `#8C95A8` passes for body text. Text set inside buttons that are filled with neon must be **black** (`#07080C`), not white.

### 2.2 Typography and iconography

- **Headings:** *Orbitron* or *Rajdhani* (Google Fonts), uppercase with letter-spacing 0.06em, giving a techy display look. Use them only for H1–H3, prices and stat numbers.
- **Body:** *Inter*, or the Streamlit default sans, at 16px. Long text never uses the display font.
- **Mono accents:** *JetBrains Mono* for SKUs, PIN examples and spec values, for example `AES-256 · XTS`.
- **Icons:** Material icons through `:material/...:`. Main ones: `lock` / `lock_open` for state, `shield` for security, `dialpad` for the keypad, `shopping_cart` for the cart, `volunteer_activism` for the community gift.
- **Logo:** an original padlock-from-USB-plug mark with a gradient outline and the wordmark "KEYGUARD **LOCAL**" in the display font (`assets/images/logo.png`).
- **Shapes:** cards and buttons have **clipped corners** (`clip-path` with an 8px corner bevel) instead of round ones, plus a faint grid or circuit-line background texture at 4% opacity.

### 2.3 Components

| Component | Description |
|---|---|
| **Product card** | A dark `surface` panel with a bevelled corner and an image (4:3) on a black backdrop with a soft cyan under-glow. It shows the name in the display font, a capacity and color line, the price, a stock badge, a **security strip** and a community-gift chip, plus a "View" button. On hover, the border turns into the RGB gradient and the glow grows. |
| **Security strip** | A row of 3 small icon badges on every card: `:material/dialpad: PIN keypad` · `:material/shield: AES-256` · `:material/delete_forever: Auto-wipe`, in `secure` violet. |
| **Security HUD panel** | A panel in the style of a game status screen, used on the product detail page and the home page. It lists the main security specs as "stat bars": Encryption ■■■■■ AES-256, Brute-force guard ■■■■■ 10-try wipe, Compatibility ■■■■■ any OS, plus a lock-state indicator. |
| **Lock-state indicator** | An LED-style dot with a label: red `LOCKED` / green `UNLOCKED`. It copies the drive's real LEDs. |
| **Primary button** | A neon-cyan fill with black text and bevelled corners. The glow grows on hover, and the focus state shows a 2px gradient ring. |
| **Secondary button** | Transparent, with a 1px cyan border and cyan text. |
| **Stock badge** | `In stock` (green), `Only N left` (amber, N ≤ 5), `Out of stock` (red). Shows text and color together. |
| **Community chip** | `:material/volunteer_activism: $3.00 to Riverton Library` |
| **Cart badge** | Item count shown next to "Cart" in the sidebar navigation |
| **Toast** | Short confirmation such as "Added KeyGuard Pro 64 GB to cart" |
| **Empty state** | Icon, one sentence and a single action (for example "Your cart is empty. → Browse drives") |

## 3. Site map

```
Public (anyone)
├── Home / Catalog            pages/shop.py
├── Product Detail            (opened from Catalog; ?sku= query param)
├── Cart                      pages/cart.py          (guest cart allowed)
├── Sign in                   pages/sign_in.py       (all roles use this one page)
└── Register                  pages/register.py      (creates a customer account)

Customer (signed in)
├── Checkout                  pages/checkout.py      (sign-in REQUIRED)
├── Order Confirmation        (after checkout; ?order= query param)
└── My Account                pages/account.py       (profile + My orders)

Staff + Owner (signed in, role staff/owner)
├── Dashboard                 pages/manage_dashboard.py
├── Manage Products           pages/manage_products.py
└── Orders                    pages/manage_orders.py

Owner only
└── Staff & Users             pages/manage_users.py
```

The navigation is **built from the user's role** using `st.navigation`. A user never sees a menu link to a page they cannot open. Every page also checks the user's role itself, so typing the URL directly does not get around the menu (see 03-non-functional).

## 4. Page wireframes

### 4.1 Global layout

```
┌──────────────┬──────────────────────────────────────────────────────┐
│ SIDEBAR      │  HEADER: logo · "Lock it. Carry it. Give back."      │
│ [logo]       │  Community banner: "$1,240 raised for Riverton       │
│ Shop         │  Library Digital Safety Fund" (live total)           │
│ Cart (3)     ├──────────────────────────────────────────────────────┤
│ Checkout     │                                                      │
│ My account   │                 PAGE CONTENT                         │
│ ──────────   │                                                      │
│ MANAGE ▸     │  (only staff/owner: Dashboard, Products, Orders;     │
│              │   owner also: Staff & Users)                         │
│ ──────────   │                                                      │
│ 👤 Sam  ●    │  ← signed-in name + role chip (CUSTOMER/STAFF/OWNER) │
│ [Sign out]   │     or [Sign in] [Register] when signed out          │
│              ├──────────────────────────────────────────────────────┤
│              │ Footer: "Demo store for training — no real orders."  │
└──────────────┴──────────────────────────────────────────────────────┘
```

A **demo notice** appears in the footer and on the checkout page so that nobody mistakes the store for a real one.

### 4.2 Catalog (Home)

```
┌──────────────────────────────────────────────────────────────────┐
│ HERO (black, RGB edge glow, faint circuit grid)                  │
│  [ drive render with glowing keypad ]   LOCKED. PORTABLE.        │
│   ● LOCKED  →  ● UNLOCKED  (slow loop)  Hardware-locked USB      │
│                                         drives. Every one helps  │
│                                         Riverton.                │
│                                 [SHOP PRO DRIVES] [COMMUNITY ED.]│
├──────────────────────────────────────────────────────────────────┤
│ SECURITY HUD:  🔢 PIN keypad  |  🛡 AES-256  |  ⌫ 10-try wipe    │
│                💻 Any OS, no software  |  ⏱ Auto-lock            │
├──────────────────────────────────────────────────────────────────┤
│ 🔍 [ Search drives (name, SKU, capacity)…           ]            │
│ Category: [All ▾]  Capacity: [Any ▾]  Price: [$0 ──●── $300]     │
│ Sort: [Featured ▾]   ☐ In stock only            12 results       │
├─────────────────┬─────────────────┬──────────────────────────────┤
│ [ image ]       │ [ image ]       │ [ image ]                    │
│ Pro 64 GB       │ Essentials 32GB │ Riverton Community 32 GB     │
│ Midnight Black  │ Slate Grey      │ River Blue                   │
│ $79.00          │ $59.00          │ $65.00                       │
│ ● In stock      │ ● Only 3 left   │ ● In stock                   │
│ ♥ $3 to Library │ ♥ $2 to Library │ ♥ $10 to Library             │
│ [View]          │ [View]          │ [View]                       │
└─────────────────┴─────────────────┴──────────────────────────────┘
```

- The grid has 3 columns on desktop. Streamlit stacks columns on narrow screens.
- Search updates as the user types (`st.text_input` plus a rerun). With no results, it shows "No drives match 'xyz'" and a **Clear filters** button.
- Sort options: Featured, Price low→high, Price high→low, Capacity, Newest.

### 4.3 Product detail

```
┌───────────────────────────────┬──────────────────────────────────┐
│                               │ KeyGuard Pro 64 GB               │
│         [ large image ]       │ SKU KG-PRO-64 · Pro              │
│                               │ $79.00                           │
│                               │ ● In stock (25)                  │
│                               │ ♥ $3.00 goes to Riverton Library │
│                               │ Qty [ 1 ▾ ]   [Add to cart]      │
│                               │ ← Back to shop                   │
├───────────────────────────────┴──────────────────────────────────┤
│ SECURITY HUD (glowing panel)          ● LOCKED                   │
│  Encryption        ■■■■■  AES-256 hardware                       │
│  Brute-force guard ■■■■■  Wipes after 10 wrong PINs              │
│  Compatibility     ■■■■■  Any OS · no software                   │
│  Auto-lock         ■■■■□  On unplug / idle timer                 │
├──────────────────────────────────────────────────────────────────┤
│ Tabs: [Overview] [Specs] [How the keypad works] [Community]      │
│  Specs table: capacity, encryption, connector, PIN length,       │
│  auto-wipe, warranty                                             │
├──────────────────────────────────────────────────────────────────┤
│ You may also like: 3 product cards from same category            │
└──────────────────────────────────────────────────────────────────┘
```

- The "How the keypad works" tab shows 3 numbered steps: 1. Type your PIN → 2. LED turns green → 3. Plug in. Each step has an icon, and the LED in the image changes from red to green.
- The quantity picker allows values from 1 up to min(10, stock).
- When stock is 0, the Add button is disabled and reads "Out of stock".

### 4.4 Cart

```
┌──────────────────────────────────────────────────────────────────┐
│ Your cart (3 items)                                              │
├──────────┬───────────────────────┬────────┬──────────┬───────────┤
│ [img]    │ Pro 64 GB             │ $79.00 │ [- 2 +]  │ $158.00 🗑│
│ [img]    │ Lanyard & Cap Set     │ $9.00  │ [- 1 +]  │   $9.00 🗑│
├──────────┴───────────────────────┴────────┴──────────┴───────────┤
│                                      Subtotal          $167.00   │
│                                      Shipping           FREE     │
│                                      Tax (8%)           $13.36   │
│                                      Total             $180.36   │
│                                      ♥ To Riverton       $6.50   │
│ [Continue shopping]                         [Proceed to checkout]│
└──────────────────────────────────────────────────────────────────┘
```

- When the subtotal is below $75, a hint reads "Add $X more for free shipping".
- If stock changed since an item was added, the line shows a warning and the quantity is capped.

### 4.5 Checkout

```
┌──────────────────────────────────┬───────────────────────────────┐
│ Checkout                          │ Order summary                 │
│ ⓘ Demo store — no payment is      │  2 × Pro 64 GB      $158.00   │
│   taken. Use a test email.        │  1 × Lanyard          $9.00   │
│ Signed in as sam@example.com      │  Subtotal           $167.00   │
│ Full name   [Sam Lee (prefilled)] │  Shipping              FREE   │
│ Address     [               ]     │  Tax                 $13.36   │
│ City [      ] ZIP [     ]         │  Total              $180.36   │
│ ☐ I understand this is a demo     │  ♥ To Riverton        $6.50   │
│           [ Place order ]         │                               │
└──────────────────────────────────┴───────────────────────────────┘
```

- **Sign-in gate:** a signed-out user who opens Checkout sees a locked panel instead of the form. It shows a `lock` icon, the text "Sign in to check out — your cart is saved", and **[SIGN IN]** and **[CREATE ACCOUNT]** buttons. After signing in, the user comes back to Checkout with the cart still there.
- The email is the account's email and cannot be edited here. The name is filled in from the profile and can be changed.
- The form is an `st.form`. Errors appear inline under each field.
- While the order is processing, the Place order button shows a spinner and is disabled so the order cannot be submitted twice.

### 4.6 Order confirmation

```
✅ Thank you, Alex! Your order KG-20261102-0007 is confirmed.
A confirmation email was saved for alex@example.com (demo outbox).
Items · totals · "You gave $6.50 to Riverton Library" · [Back to shop]
```

### 4.7 Sign in and Register

```
┌────────────────────────────────────────┐
│          🔒 ACCESS TERMINAL            │   ← glowing panel, centred
│  [ Sign in ]  [ Register ]   (tabs)    │
│                                        │
│  Email     [                      ]    │
│  Password  [••••••••          👁 ]     │
│            [   SIGN IN   ]             │
│  New here? Create an account →         │
│  ⓘ Demo: use an @example.com email     │
└────────────────────────────────────────┘

Register tab:
│  Full name [        ]                  │
│  Email     [        ]                  │
│  Password  [        ]  strength: ■■■□  │
│  Confirm   [        ]                  │
│  ☐ I understand this is a demo store   │
│            [ CREATE ACCOUNT ]          │
```

- There is one sign-in page for customers, staff and owners. After sign-in, customers return to the page they came from (or the Shop). Staff and owners land on the Dashboard.
- A failed sign-in always shows the same message, "Email or password is incorrect", so it never reveals whether an account exists.
- The password meter and a live checklist (8+ characters · a letter · a number) update as the user types.
- While locked out after too many failed attempts, the page shows a red `LOCKED` state with a countdown (see NFR-AUTH-05).

### 4.8 My Account (customer)

```
Tabs: [Profile] [My orders]
Profile:   Full name [     ]  Email (read-only)   [Save]
           [Change password]
My orders: table — Order # · Date · Items · Total · Status chip
           click row → order detail + "Download confirmation email"
```

### 4.9 Manage: dashboard (staff and owner)

```
┌───────────┬───────────┬───────────┬───────────────┐
│ Orders    │ Revenue   │ Units sold│ Community $   │   ← st.metric row
│ 27        │ $3,410.20 │ 61        │ $214.50       │
├───────────┴───────────┴───────────┴───────────────┤
│ ⚠ Low stock (≤ 5): Pro 256 GB (2), 5-Pack (4)      │
├───────────────────────────────────────────────────┤
│ Recent orders (last 10) — table                    │
└───────────────────────────────────────────────────┘
```

- **Staff** see Orders, Units sold and Low stock. The **Revenue** and **Community $** tiles are shown only to the owner.

### 4.10 Manage: products (staff and owner)

```
[ + Add product ]   Search [        ]   ☐ Show inactive
┌────────┬────────────────────┬────────┬───────┬────────┬─────────┐
│ SKU    │ Name               │ Price  │ Stock │ Active │ Actions │
│ KG-... │ ...                │ $79.00 │ 25    │ ✔      │ Edit    │
└────────┴────────────────────┴────────┴───────┴────────┴─────────┘
```

- Owners can edit inline with `st.data_editor` (price, stock, active), with a **Save changes** button.
- **Add / Edit** opens a form (in a dialog or expander) with every product field and an image upload.
- **Delete** asks for confirmation ("Type the SKU to confirm"). The recommended approach is to deactivate a product rather than delete it.
- **Role differences:** staff can edit stock, description, specs, image and the active flag. The **+ Add product**, **Delete**, **Price** and **Community gift** controls are hidden from staff, and price and gift cells are read-only for them. Owners see everything.

### 4.11 Manage: orders (staff and owner)

- A table of orders filtered by date and status. Clicking an order opens its line items, its totals and the path of its email file.
- Staff can change status through `Placed → Packed → Shipped`. Only the owner sees **Cancel order**, which puts the stock back.

### 4.12 Owner: Staff & Users

```
Search users [          ]
┌──────────────────┬────────────┬──────────┬────────────────────┐
│ Email            │ Name       │ Role     │ Actions            │
│ sam@example.com  │ Sam Lee    │ CUSTOMER │ [Make staff]       │
│ kim@example.com  │ Kim Ortiz  │ STAFF    │ [Remove staff]     │
│ owner@example.com│ Store Owner│ OWNER    │ —  (cannot change) │
└──────────────────┴────────────┴──────────┴────────────────────┘
```

- Every role change opens a confirmation dialog and is written to the audit log. The owner cannot change their own role.

## 5. Interaction and feedback rules

| Event | Feedback |
|---|---|
| Add to cart | Toast, and the cart badge count updates |
| Change quantity / remove | Totals update right away. Removing an item can be undone with a toast. |
| Validation error | Inline red text under the field, and focus stays in the form |
| Server/DB error | `st.error` with a plain explanation and a "Try again" button. Raw errors are never shown. |
| Long operation (> 300 ms) | `st.spinner` |
| Owner save | `st.success("Saved 3 changes")` |

## 6. Accessibility and motion safety

- **No flashing.** No effect flashes more than 3 times per second (WCAG 2.3.1). The RGB gradient moves slowly, taking 8 seconds or longer per cycle, and never strobes. This matters because audiences include minors and people with photosensitivity.
- **Reduced motion.** Under `@media (prefers-reduced-motion: reduce)`, all animations stop: the gradient becomes still and the lock-state loop shows a static "LOCKED → UNLOCKED" graphic.
- **Glow is decoration only.** Text must stay readable with glows and gradients turned off.
- Every image has alt text (the product name).
- Color is never the only signal. Badges always include text.
- Form fields have visible labels, not only placeholder text.
- All primary actions can be reached by keyboard (Streamlit default).
- Contrast is at least 4.5:1 for body text in both themes.

## 7. Content rules

- All copy is age-appropriate and friendly, written for training audiences that include minors.
- Every place that mentions money or email reminds the user that this is a demo.
- **Honest selling, with no pressure tactics:** no countdown timers, no fake "only 2 left" messages (the low-stock badge shows **real** stock only), no pre-ticked add-ons, and no guilt messages about the community gift.
- **No overclaiming:** security copy describes what the (fictional) drive does. It never claims to be "unhackable", "unbreachable" or officially certified.

## 8. Vision analysis

| Vision statement (from the owner) | What it means for the design | What it does **NOT** mean |
|---|---|---|
| "Gaming RGB / premium gaming-hardware aesthetic" | Dark-first theme, neon accents, RGB gradient edges, bevelled shapes and display fonts (§2) | **Not gamification:** no points, XP, levels, badges or rewards for shoppers. "Gaming" is the *look* only. Not strobing or flashing lights. Not copying any real gaming brand's logo, colors or name. |
| "Highlights my USB drives' security" | Security strip on every card, Security HUD, lock-state LED motif, and the keypad explainer placed above the fold (§2.3, §4.2, §4.3) | Not fear-based marketing, "hacker" imagery or skulls. Not claims of being unhackable or certified. |
| "Somewhat beneficial to a local city" | Community banner on every page, a gift chip on every card, and the gift total in the cart, confirmation and email | Not a real city partnership or real donation (Riverton is fictional). Not guilt-tripping shoppers. |
| "Customers register and sign in" | A shared "Access Terminal" sign-in and register page, a checkout gate, and My Account (§4.5, §4.7, §4.8) | Not social login. Not asking for age, phone or photos. Browsing never requires an account. |
| "Owner and staff manage products" | Manage section built from the user's role, with controls hidden by role (§3, §4.9–§4.12) | Not a separate admin website. Not exposing owner controls to staff. |
| "Learning and demo" | A demo notice on every page and at checkout. No payment fields anywhere. | Not a low-quality mock-up. It should look like a real, polished store while always being labeled as a demo. |

## 9. UI/UX requirements for the designer

Priority: **M** = Mandatory, **S** = Should, **C** = Could.

| ID | Pri | Requirement |
|---|---|---|
| UX-01 | M | Use the dark-first color tokens in §2.1. No other brand colors, and no real company's logo or trademark. |
| UX-02 | M | The RGB gradient appears only on borders, dividers, the hero headline and the primary CTA border. It never sits behind body text. |
| UX-03 | M | Every product card includes the security strip (PIN keypad · AES-256 · Auto-wipe), the stock badge and the community chip. |
| UX-04 | M | The home and product detail pages include the Security HUD panel and the red/green lock-state indicator. |
| UX-05 | M | The navigation and header show the user's state: signed out ([Sign in] [Register]) or signed in (name, role chip and [Sign out]). |
| UX-06 | M | Navigation and controls depend on role. Customers never see Manage links. Staff never see owner-only controls (§4.10–§4.12). |
| UX-07 | M | Checkout has a sign-in gate for signed-out users, and the cart is kept through sign-in (§4.5). |
| UX-08 | M | The sign-in and register page includes a password strength meter, a live rules checklist, a show/hide password toggle, generic error text and a lockout state (§4.7). |
| UX-09 | M | Every data view has empty, loading and error states (§2.3 and §5). |
| UX-10 | M | Destructive actions (delete product, cancel order, change role) need a confirmation dialog. |
| UX-11 | M | Meets WCAG 2.1 AA contrast. Nothing flashes more than 3 times a second. All animation respects `prefers-reduced-motion` (§6). |
| UX-12 | M | A demo notice is visible in the footer, at checkout and on the register tab. |
| UX-13 | S | Layout works from 360 px width up to desktop. Cards go from 3 columns to 1 on phones. |
| UX-14 | S | Hover and focus states for all interactive elements use the glow scale (§2.1). |
| UX-15 | C | Short (≤ 300 ms) micro-interactions: add-to-cart pulse on the cart badge, and a lock-to-unlock icon change after successful sign-in. |

## 10. Designer deliverables

1. A style tile or mini design system: color tokens, type scale, buttons, inputs, badges, card, HUD panel, lock indicator, glow and gradient specs.
2. High-fidelity wireframes for every page in §3 at desktop (1440) and phone (390) widths, including empty, loading, error and role variants.
3. Click-through prototype of the main flow: Catalog → Detail → Add to cart → Cart → Sign-in gate → Sign in → Checkout → Confirmation.
4. A motion spec for the gradient cycle, the lock loop and the hover glow, with the reduced-motion fallback for each.
5. A filled-in accessibility checklist for UX-11.
6. Designs for every screen S1–S16 in §12, including each system state in §13.
7. A note on each design confirming it can be built within the Streamlit limits in §14, or marking it "needs a simpler fallback".

## 11. Key user flows

Each flow lists the screens in order. Screen codes are defined in §12.

| Flow | Who | Steps | Stories |
|---|---|---|---|
| **A. Browse and buy** (main flow) | Guest → Customer | S1 Home → search or filter → S2 Detail → Add to cart → S3 Cart → Checkout → **sign-in gate** → S4 Sign in *or* S5 Register → back to S6 Checkout (cart kept) → Place order → S7 Confirmation → Download email | SRCH-01/02, PDP-01, CART-01/02/04, CHK-01…05, AUTH-01/02 |
| **B. Check a past order** | Customer | S4 Sign in → S9 My orders → open an order → Download confirmation email | AUTH-02, CHK-06 |
| **C. Restock a low-stock drive** | Staff | S4 Sign in → S10 Dashboard (low-stock list) → S11 Products → edit stock → Save → success toast | MGT-01/02/04/08 |
| **D. Add a new drive** | Owner | S11 Products → **+ Add product** → S12 Product form → upload image → Save → product appears in S1 | MGT-03, MGT-07 |
| **E. Retire a drive** | Staff or owner | S11 Products → toggle **Active** off → confirm → product disappears from S1 and its URL shows "Product not found" | MGT-05 |
| **F. Promote a staff member** | Owner | S14 Staff & Users → search → **Make staff** → confirm dialog → role chip updates | MGT-10 |
| **G. Cancel an order** | Owner | S13 Orders → open order → **Cancel order** → confirm → stock restored | MGT-09 |
| **H. Too many wrong passwords** | Anyone | S4 Sign in → 5 failed attempts → **Locked** state with countdown → try again later | AUTH-02 |

## 12. Screen index (S1–S16) linked to user stories

| Code | Screen | Wireframe | Who sees it | User stories |
|---|---|---|---|---|
| S1 | Home / Catalog (hero, Security HUD, search, filters, product grid) | §4.2 | Everyone | US-SRCH-01, 02, 03, 04 |
| S2 | Product detail (HUD, tabs, add to cart, "You may also like") | §4.3 | Everyone | US-PDP-01, 02 · US-CART-01 |
| S3 | Cart | §4.4 | Everyone | US-CART-02, 03 |
| S4 | Sign in | §4.7 | Signed out | US-AUTH-02, 03, 05 · US-CART-04 |
| S5 | Register | §4.7 | Signed out | US-AUTH-01 |
| S6 | Checkout (with sign-in gate) | §4.5 | Gate: signed out · Form: signed in | US-CHK-01, 02, 03 |
| S7 | Order confirmation | §4.6 | Customer | US-CHK-04, 05 |
| S8 | My Account: Profile | §4.8 | Signed in | US-AUTH-04 |
| S9 | My Account: My orders | §4.8 | Signed in | US-CHK-06 |
| S10 | Manage: Dashboard | §4.9 | Staff, Owner (revenue tiles owner only) | US-MGT-01, 08 |
| S11 | Manage: Product list and bulk edit | §4.10 | Staff, Owner | US-MGT-02, 04, 05, 06 |
| S12 | Manage: Add / edit product form | §4.10 | Owner (create) · Staff (edit allowed fields) | US-MGT-03, 07 |
| S13 | Manage: Orders | §4.11 | Staff, Owner (cancel owner only) | US-MGT-09 |
| S14 | Owner: Staff & Users | §4.12 | Owner | US-MGT-10 |
| S15 | Global layout: sidebar nav, header, community banner, footer, cart badge | §4.1 | Everyone (menu changes by role) | US-MGT-01 · US-AUTH-03 · US-CART-01 |
| S16 | System states (shown on any screen) | §13 | Everyone | All stories (UX-09) |

All 31 user stories appear at least once in this table.

## 13. System states (S16)

Every screen must have a design for each state that can happen on it.

| State | When it happens | What the user sees |
|---|---|---|
| **Loading** | Data is being fetched | `st.spinner` plus placeholder (skeleton) cards in the same layout. No layout jump when data arrives. |
| **Empty** | No search results, empty cart, no orders yet, no products in Manage | An icon, one sentence and one action (for example "No drives match 'xyz'" with **Clear filters**) |
| **Validation error** | A form field is wrong | Red text under the field. Typed values are kept. |
| **Action failed** | Saving or placing an order fails | A plain `st.error` with **Try again**. Nothing is shown as successful (NFR-REL-05). |
| **Store unavailable** | The database can't be reached | A full-page "Store temporarily unavailable" panel with the logo and a **Retry** button (NFR-REL-03) |
| **Not found** | Unknown or inactive product SKU, or an unknown order number | "Product not found" or "Order not found", with **Back to shop** |
| **Access denied** | Someone opens a page their role can't use | A lock icon, "Staff access only" (or "Owner only") and **Go to shop** |
| **Sign-in required** | A signed-out user opens Checkout or My Account | The sign-in gate panel (§4.5) |
| **Locked out** | 5 failed sign-ins | A red **LOCKED** indicator with a countdown (§4.7) |
| **Session expired** | 30 minutes without activity | "You were signed out for safety", then Sign in. The cart is kept. |
| **Out of stock / stock changed** | Stock is 0, or lower than the quantity in the cart | A red badge and a disabled button, or an amber warning in the cart with the quantity capped |
| **Success** | Saved, added or ordered | A toast or `st.success`, close to the action |

## 14. What Streamlit can and can't do (design within these limits)

The app is built with Streamlit, so designs must use what it supports. When unsure, design the simple version first and the fancy version as an optional extra.

| ✅ Easy in Streamlit | ⚠️ Possible with custom CSS (keep it simple) | ❌ Avoid (not practical) |
|---|---|---|
| Sidebar navigation that changes by role (`st.navigation`) | Neon glow, RGB gradient borders, bevelled corners on containers and buttons | Free positioning or overlapping elements (Streamlit stacks blocks top to bottom) |
| Columns, containers with borders, tabs, expanders | Display fonts from Google Fonts | Complex JavaScript animations or a 3D, rotating drive model. Use a still image or a slow CSS effect instead. |
| Forms, inputs, sliders, selectboxes, checkboxes | A slow-moving gradient, with a reduced-motion fallback | Drag and drop, swipe gestures and custom right-click menus |
| Dialogs (one at a time), toasts, spinners, success and error boxes | Hover effects on cards made from containers | Smooth page transitions. Every click re-runs the page, so design for instant swaps. |
| Editable tables (`st.data_editor`) and metric tiles (`st.metric`) | Styling Streamlit's built-in widgets. This works, but can break when Streamlit updates, so restyle only buttons, inputs and containers. | Real-time live updates pushed to every user |
| Images, file upload, download button | A sticky header (it may not stay fixed in every browser) | Pixel-perfect matching of a design tool mock-up |
| URL query parameters (`?sku=`) and Material icons | | Several stacked pop-ups at once |

**Tips for the designer:**
- Design in **vertical sections** made of rows of columns. That's how Streamlit lays pages out.
- Treat the RGB effects as **borders and shadows**, not backgrounds behind text.
- Make the hero "drive render" a **static image** (PNG or WebP), with the LED glow done in CSS.
- Use only **Material icons**, so they render without extra files.

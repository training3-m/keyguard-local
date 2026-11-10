# Functional Requirements

## 1. Product catalog and search

### FR-1.1 Catalog

The app shall display published products with name, summary, price, image or
placeholder, and stock availability.

### FR-1.2 Search

The shopper shall be able to search products by name, description, and tags.
Search shall be case-insensitive and show a useful empty state when there are
no matches. Search results shall include only published products.

### FR-1.3 Product detail

The shopper shall be able to open a product detail view showing its description,
price, available inventory, and configured verified specifications.
Unpublished products shall not be available to shoppers.

## 2. Cart

### FR-2.1 Add items

The shopper shall be able to add an in-stock product to the cart. The app shall
reject an add operation for an unpublished or out-of-stock product.

### FR-2.2 Change and remove items

The shopper shall be able to update item quantities and remove items. Quantity
must be a positive whole number and cannot exceed current available stock.

### FR-2.3 Totals

The app shall calculate line totals and subtotal from authoritative product
prices and cart quantities. The app shall not add tax, shipping, or payment
fees unless separately specified in a future requirement.

### FR-2.4 Stale cart

Before checkout, the app shall re-read or otherwise validate current product
status, prices, and stock. It shall explain any changes and require the shopper
to review the updated cart before submitting.

## 3. Demo checkout and order confirmation

### FR-3.1 Checkout fields

Checkout shall collect a syntactically valid test email address and no payment
information. Label the email as test/demo data and tell the shopper that no
email will be sent.

### FR-3.2 Submission

The shopper shall explicitly submit a “Place demo order” action. On submission,
the app shall validate the email, cart contents, current prices, and current
stock.

### FR-3.3 Order record

For a successful checkout, the app shall create a unique order identifier and
persist a JSON record under `data/orders/`. The record shall include:

- Order identifier and creation timestamp.
- Test email address.
- Product identifiers and order-time product names.
- Unit prices, quantities, line totals, and order subtotal.
- A status identifying it as a demo order, not a paid order.

Use a generated, filesystem-safe filename independent of the email address.
Do not write card data or other unnecessary personal information.

### FR-3.4 Inventory deduction

After a successful order, the app shall deduct each ordered quantity from
available inventory. It shall prevent stock from becoming negative and prevent
two orders from consuming the same remaining stock.

For a local file-backed demo, order persistence and inventory updates shall be
implemented with a recoverable, serialized operation appropriate to that
backend. For Supabase or another remote backend, use a server-side transaction
or equivalent atomic operation. Do not report success if either operation
fails or leaves the result uncertain; surface the error and preserve enough
state for safe retry/reconciliation.

### FR-3.5 Confirmation

Only after the order is persisted and inventory is updated successfully shall
the app show an order confirmation. The confirmation shall display the order
identifier, test email, items, quantities, total, and the message that no
payment was collected and no email was sent.

Clear the cart only after successful order completion. Repeated submission
must not create duplicate orders or deduct inventory twice for the same
checkout attempt.

### FR-3.6 Demo boundaries

The app shall not charge a payment method, send an email, or represent a demo
order as paid, shipped, or fulfilled.

## 4. Owner product management

### FR-4.1 Product creation and editing

An authorized owner shall be able to create and edit product name, summary,
description, price, stock, image reference, tags, and publish status.

### FR-4.2 Validation

The app shall reject missing required text, invalid or negative prices, and
negative or fractional inventory. Optional specifications may be omitted and
shall not be fabricated.

### FR-4.3 Publication and removal

An authorized owner shall be able to publish and unpublish a product. Products
referenced by order history should be unpublished or archived rather than
permanently deleted. Unpublished products shall not appear in shopper search
or catalog results.

### FR-4.4 Authorization

Owner pages and write operations shall be restricted to an authorized owner.
Hiding navigation alone is not authorization: the underlying write operation
must enforce the role. In local learning mode, clearly identify any
development-only access mechanism; never describe it as production security.

## 5. Owner order review

An authorized owner shall be able to review demo order ID, timestamp, test
email, order items, quantities, and total. Order records shall be visibly
identified as demos.

## 6. Data and error behavior

- Product identifiers shall be stable and unique.
- Order details shall preserve order-time product names and prices even if the
  current product is later edited.
- Inventory and price values used for checkout shall come from the data
  service, not solely from client/session state.
- Persistence and validation errors shall be visible and actionable; no error
  may be presented as successful checkout.
- Do not commit generated demo orders or real customer data.
- The demo order storage path is `data/orders/`; it must be isolated from
  source-controlled fixtures and must not be used as a production customer
  database.

## 7. Acceptance criteria

1. A shopper can search published products and open a matching product detail
   page; unpublished products do not appear in results.
2. A shopper can add an in-stock product, change its quantity, remove it, and
   see correct line and subtotal calculations.
3. The app rejects invalid email, zero/negative/non-integer quantities, and
   quantities exceeding current stock.
4. A valid demo checkout stores one order record under `data/orders/`, shows
   an order confirmation, and decreases inventory by exactly the ordered
   quantities.
5. The checkout requests no payment details and sends no email.
6. If order or inventory persistence fails, no success confirmation is shown,
   the shopper receives an error, and the app avoids duplicate deduction on
   retry.
7. An authorized owner can create, edit, publish/unpublish products, and
   manage inventory; an unauthorized shopper cannot perform those operations.
8. The owner can review recorded demo orders, and product changes do not alter
   the historical item names or prices on an order.

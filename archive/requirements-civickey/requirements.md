# CivicKey Store — Consolidated Requirements

## 1. Purpose

CivicKey Store is a learning and demonstration e-commerce app for a fictional
USB-drive product. It demonstrates product discovery, a shopping cart, a
payment-free checkout, inventory updates, and owner product management.

The app is not a real store. Checkout must not collect payment details, send
real email, or imply that an order is a real purchase.

## 2. Product summary

The featured product is a reusable USB flash drive with a physical keypad.
The keypad is intended to add a physical access-control step before the drive
can be unlocked. The app may present a community-minded product story—for
example, inviting a portion of proceeds to support a locally chosen city
project—but must label any such contribution as a proposal until an owner
provides a verified program and terms.

Do not claim that a keypad alone encrypts data or guarantees security. Product
claims about encryption, capacity, compatibility, durability, and contribution
amounts must be explicitly configured and verified before being displayed as
facts.

See [Product Requirements](./product.md) for product details.

## 3. Users and roles

- **Shopper:** browses and searches the catalog, views product details, adds
  products to a cart, and submits a demo order using a test email address.
- **Store owner:** creates, edits, publishes, unpublishes, and removes products;
  reviews inventory and demo orders.

Owner pages must not be presented as publicly accessible management tools in a
deployed app. Authentication and authorization are required before enabling
owner actions outside a local learning setup.

## 4. Experience and visual direction

The experience should feel trustworthy, practical, civic-minded, and easy to
understand. Use a clean catalog, clear product photography or placeholders,
readable typography, visible stock and pricing, and prominent cart and checkout
actions. The community story should be informative rather than imply an
unverified charitable commitment.

The app is implemented in Streamlit; designs should use its multipage
navigation and reusable components rather than assume a separate frontend.

See [UI/UX Requirements](./ui-ux.md) for page layouts and interaction details.

## 5. Required functionality

1. **Catalog and search:** list published products and search by product name,
   description, or relevant tags. Provide useful empty and error states.
2. **Product detail:** show images, description, configured specifications,
   price, availability, and quantity controls.
3. **Cart:** add items, change quantities, remove items, and see an accurate
   subtotal. Reject quantities greater than available stock.
4. **Demo checkout:** collect a test email address only; do not request or
   process payment information. On successful submission, create an order
   record in the local demo orders folder, display an order confirmation, and
   deduct the ordered quantities from inventory.
5. **Owner product management:** provide owner-only product create, edit,
   publish/unpublish, and delete or archive operations, including inventory
   management.
6. **Order visibility:** make submitted demo orders available to the owner for
   learning and verification.

See [Functional Requirements](./functional-requirements.md) for detailed
acceptance criteria and data behavior.

## 6. Demo checkout and persistence

- The demo checkout is not a payment system. It must not include card fields,
  payment-provider integrations, or claims that an order was paid.
- Use a clearly identified test email address. Do not send an email; render the
  confirmation in the app.
- Save each successful demo order as a JSON record under
  `data/orders/` (create the folder when needed). Include the test email, order
  identifier, item quantities and prices, total, and timestamp. Use a
  filesystem-safe generated filename; do not use the email address as a
  filename.
- The order record and inventory deduction must represent the same successful
  checkout. Validate stock again when submitting checkout so stale carts
  cannot oversell. If persistence fails, report the failure and do not show a
  success confirmation.
- Do not commit generated order records or real personal data. Add the local
  orders directory to ignore rules when implementation creates it.
- The repository describes Supabase as its intended database. Keep inventory
  writes behind the existing data/service boundary. A local demo persistence
  implementation must be clearly separated from any deployed/Supabase mode;
  do not imply that a file write and a remote database update are a single
  atomic transaction.

## 7. Quality and constraints

- Keep the app suitable for local learning and demonstration.
- Validate all shopper and owner input; show actionable validation errors.
- Keep prices and inventory authoritative in the data layer, not solely in
  browser/session state.
- Do not expose owner controls to shoppers.
- Do not store payment data, passwords, or real customer information in demo
  files.
- Support keyboard navigation and readable contrast.
- Automated tests should cover catalog search, cart quantity rules, checkout
  confirmation and persistence, inventory deduction, and owner product
  operations.

## 8. Out of scope

- Real payment processing or paid orders.
- Sending real email.
- Production identity verification, fulfillment, shipping, or returns.
- Claims of certified encryption or guaranteed protection unless verified
  product details and implementation support them.
- A guaranteed donation or city partnership without owner-supplied terms.

## 9. Document set

- [Product Requirements](./product.md)
- [UI/UX Requirements](./ui-ux.md)
- [Functional Requirements](./functional-requirements.md)

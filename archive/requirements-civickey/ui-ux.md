# UI/UX Requirements

## Design direction

Create a calm, modern storefront that balances practical product information
with a community-minded identity. Avoid security-alarm styling and avoid
visuals or copy that overstate device protection or charitable impact.

### Visual system

- **Palette:** deep navy or charcoal for headings and navigation; warm off-white
  backgrounds; teal or leaf-green accents for community cues; amber for stock
  warnings. Maintain readable text contrast.
- **Typography:** a clear sans-serif system font, with distinct heading,
  body, metadata, and price sizes.
- **Layout:** responsive single-column flow on narrow screens and a
  restrained grid on wider screens. Keep content aligned and avoid dense
  dashboards.
- **Imagery:** use a product image when supplied; otherwise show a consistent
  neutral placeholder. Do not use imagery suggesting encryption certification
  or a city endorsement.
- **Components:** reusable product cards, quantity controls, status messages,
  forms, and cart/order summaries, consistent with the Streamlit app structure.

## Navigation

Use clear Streamlit multipage navigation for:

- **Shop** — product catalog and search.
- **Cart** — selected products and quantities.
- **Owner: Products** — product and inventory management, visible only to an
  authorized owner.
- **Owner: Orders** — demo order review, visible only to an authorized owner.

Provide a visible cart item count where practical. The demo-store notice should
be easy to find, including on checkout and confirmation.

## Page requirements

### Shop / catalog

- Show a concise introduction to CivicKey USB and an explicit demo-store
  notice.
- Place search near the start of the catalog.
- Show products as consistent cards with image, name, short description, price,
  stock state, and a product-detail action.
- Offer an add-to-cart action when stock is available; disable it for
  unpublished or out-of-stock products.
- Explain when a search has no matches and provide a way to clear the search.

### Product detail

- Display the product name, image, price, description, and available stock.
- Show only verified specifications.
- Explain the keypad as an access-control step without making unsupported
  encryption or security promises.
- Provide quantity selection and add-to-cart action, bounded by available
  stock.
- Show a clear message if the item is out of stock.

### Cart

- List each selected product, unit price, quantity, and line total.
- Allow quantity changes and removal, with stock limits enforced.
- Show subtotal and a clear path back to the catalog or onward to checkout.
- Explain that no payment is taken in this learning demo.
- Provide a useful empty-cart state.

### Checkout

- Collect only a test email address, validated before order submission.
- Do not render payment fields or imply payment will be charged.
- Summarize items, quantities, and total before submission.
- Make the action explicit, for example “Place demo order.”
- Show validation, inventory-conflict, and save errors in context without
  clearing the cart or presenting a false success state.

### Order confirmation

- Confirm that a demo order was recorded, not paid.
- Show the order identifier, test email, ordered items, quantities, and total.
- State that no email was sent and no payment was collected.
- Clear the completed cart only after order persistence succeeds.

### Owner: Products

- Use a table or compact list with product name, price, stock, and publish
  status.
- Provide clearly labeled create/edit forms and publish/unpublish controls.
- Validate required fields, non-negative prices, and non-negative whole-number
  inventory.
- Ask for confirmation before destructive removal; prefer unpublishing or
  archiving when order history refers to a product.
- Keep all management controls owner-only.

### Owner: Orders

- Show demo order ID, timestamp, test email, total, and line items.
- Label records as demo orders.
- Do not provide controls that imply a payment or fulfillment has occurred.

## Interaction and accessibility

- Use descriptive labels, not placeholder text alone.
- Keep keyboard focus order predictable and controls keyboard-operable.
- Use text labels and icons together for stock and status; do not rely on color
  alone.
- Display success, warning, and error messages close to the relevant action.
- Preserve user-entered values after validation or persistence errors.
- Keep layouts readable on mobile screens and avoid horizontal scrolling.

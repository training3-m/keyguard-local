-- 01_products.sql
-- The KeyGuard Local catalog (01-product.md §A5): 10 products for sale + 1 hidden (discontinued).
-- Everything here is fictional demo data. Safe to run again: existing SKUs are skipped.
-- Images stay empty for now; the shop shows a placeholder until staff upload photos (US-MGT-07).

insert into public.products
  (sku, name, category, capacity_gb, color, description, specs,
   price_cents, community_gift_cents, stock_qty, is_active, featured_rank)
values
  ('KG-ESS-16', 'KeyGuard Essentials 16 GB', 'Essentials', 16, 'Slate Grey',
   'Type your PIN, plug it in, get to work. Unplug it and your files lock themselves. A great first secure drive for school.',
   '{"encryption": "AES-256 hardware (demo copy)", "pin_length": "7-15 digits", "auto_wipe": "after 10 wrong PINs", "connector": "USB-C + USB-A adapter", "warranty": "3 years"}',
   4900, 200, 40, true, 50),

  ('KG-ESS-32', 'KeyGuard Essentials 32 GB', 'Essentials', 32, 'Slate Grey',
   'Room for a whole year of assignments, locked behind your own PIN. Works on any computer, no software needed.',
   '{"encryption": "AES-256 hardware (demo copy)", "pin_length": "7-15 digits", "auto_wipe": "after 10 wrong PINs", "connector": "USB-C + USB-A adapter", "warranty": "3 years"}',
   5900, 200, 35, true, 40),

  ('KG-PRO-64', 'KeyGuard Pro 64 GB', 'Pro', 64, 'Midnight Black',
   'An aluminium drive for client files and business records. Read-only mode keeps files from being changed by accident.',
   '{"encryption": "AES-256 hardware (demo copy)", "pin_length": "7-15 digits", "auto_wipe": "after 10 wrong PINs", "read_only_mode": "yes", "connector": "USB-C + USB-A adapter", "warranty": "3 years"}',
   7900, 300, 25, true, 10),

  ('KG-PRO-128', 'KeyGuard Pro 128 GB', 'Pro', 128, 'Midnight Black',
   'Double the space of the Pro 64 with the same keypad lock, auto-lock and read-only mode.',
   '{"encryption": "AES-256 hardware (demo copy)", "pin_length": "7-15 digits", "auto_wipe": "after 10 wrong PINs", "read_only_mode": "yes", "connector": "USB-C + USB-A adapter", "warranty": "3 years"}',
   9900, 400, 20, true, 25),

  -- Starts with low stock so the low-stock warning can be shown in demos.
  ('KG-PRO-256', 'KeyGuard Pro 256 GB RGB Edition', 'Pro', 256, 'Midnight Black with RGB keypad glow',
   'Our biggest drive, with a softly glowing RGB keypad: red when locked, green when unlocked. The glow fades slowly and never flashes.',
   '{"encryption": "AES-256 hardware (demo copy)", "pin_length": "7-15 digits", "auto_wipe": "after 10 wrong PINs", "read_only_mode": "yes", "lighting": "RGB keypad glow (slow fade, no flashing)", "connector": "USB-C + USB-A adapter", "warranty": "3 years"}',
   13900, 500, 10, true, 30),

  ('KG-RCE-32', 'Rancho Community Edition 32 GB', 'Community', 32, 'River Blue (skyline engraving)',
   'Engraved with the Rancho skyline. $10 from every drive goes to the Rancho Public Library Digital Safety Fund.',
   '{"encryption": "AES-256 hardware (demo copy)", "pin_length": "7-15 digits", "auto_wipe": "after 10 wrong PINs", "connector": "USB-C + USB-A adapter", "warranty": "3 years"}',
   6500, 1000, 30, true, 20),

  ('KG-RCE-64', 'Rancho Community Edition 64 GB', 'Community', 64, 'River Blue (skyline engraving)',
   'More space, same Rancho skyline engraving. $12 from every drive supports free data-privacy classes at the library.',
   '{"encryption": "AES-256 hardware (demo copy)", "pin_length": "7-15 digits", "auto_wipe": "after 10 wrong PINs", "connector": "USB-C + USB-A adapter", "warranty": "3 years"}',
   8500, 1200, 15, true, 35),

  ('KG-BULK-5', 'Essentials 32 GB — 5-Pack', 'Bulk', 32, 'Slate Grey',
   'Five Essentials 32 GB drives for a team or classroom. Each drive has its own PIN.',
   '{"contents": "5 x Essentials 32 GB", "encryption": "AES-256 hardware (demo copy)", "auto_wipe": "after 10 wrong PINs", "warranty": "3 years"}',
   26900, 1200, 8, true, 60),

  ('KG-ACC-LAN', 'KeyGuard Lanyard & Cap Set', 'Accessories', null, 'Mixed',
   'A lanyard and two spare caps so your drive is always with you.',
   '{"contents": "1 lanyard, 2 spare caps"}',
   900, 50, 60, true, 80),

  ('KG-ACC-CASE', 'Hard-Shell Travel Case', 'Accessories', null, 'Black',
   'A zip case that holds up to three KeyGuard drives.',
   '{"holds": "up to 3 drives"}',
   1500, 50, 45, true, 90),

  -- Discontinued and hidden: shows how "deactivate" keeps a product without selling it (US-MGT-05).
  ('KG-ESS-8', 'KeyGuard Essentials 8 GB', 'Essentials', 8, 'Slate Grey',
   'Discontinued. Replaced by the Essentials 16 GB.',
   '{"encryption": "AES-256 hardware (demo copy)", "pin_length": "7-15 digits", "auto_wipe": "after 10 wrong PINs"}',
   3900, 100, 0, false, 999)
on conflict (sku) do nothing;

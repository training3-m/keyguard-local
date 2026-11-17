-- 0002_products.sql
-- The USB drives and accessories sold in the store.
-- Spec: docs/requirements/01-product.md §A5 (catalog) and 03 §4.1, NFR-INT-05/08.

create table public.products (
  id                    bigint generated always as identity primary key,
  -- Unique product code such as KG-PRO-64. It never changes after creation (see 0005).
  sku                   text not null unique check (sku ~ '^[A-Z0-9-]{3,20}$'),
  name                  text not null check (char_length(name) between 2 and 120),
  category              text not null
                        check (category in ('Essentials', 'Pro', 'Community', 'Bulk', 'Accessories')),
  -- Null for accessories, which have no storage.
  capacity_gb           integer check (capacity_gb is null or capacity_gb > 0),
  color                 text,
  description           text,
  specs                 jsonb not null default '{}'::jsonb,
  -- Money is whole cents so there are no rounding errors (NFR-INT-04).
  price_cents           integer not null check (price_cents > 0),
  -- The amount per unit given to the Riverton library fund. Never more than the price.
  community_gift_cents  integer not null default 0
                        check (community_gift_cents >= 0 and community_gift_cents <= price_cents),
  -- Stock can never go below zero: the final safety net against overselling (NFR-INT-01).
  stock_qty             integer not null default 0 check (stock_qty >= 0),
  image_url             text,
  -- Inactive products are hidden from the shop but kept for order history.
  is_active             boolean not null default true,
  featured_rank         integer not null default 100,
  created_at            timestamptz not null default now(),
  updated_at            timestamptz not null default now()
);

comment on table public.products is 'Keypad-locked USB drives and accessories. Prices in cents.';

-- The shop lists active products by category and in "featured" order.
create index products_active_category_idx on public.products (category) where is_active;
create index products_active_featured_idx on public.products (featured_rank) where is_active;

create trigger products_set_updated_at
  before update on public.products
  for each row execute function private.set_updated_at();

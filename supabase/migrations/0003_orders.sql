-- 0003_orders.sql
-- Demo orders and their lines. No payment data is ever stored (NFR-SEC-02).
-- Orders are only CREATED by the place_order function (Prompt C), never directly by the website.
-- Spec: 03 §4.1 and §12 (data integrity), 01-product.md US-CHK-03, US-MGT-09.

create table public.orders (
  id                    bigint generated always as identity primary key,
  -- Shown to customers, for example KG-20261102-0007 (01-product.md §A6).
  order_number          text not null unique check (order_number ~ '^KG-[0-9]{8}-[0-9]{4}$'),
  -- Keep orders even if staff look up an old customer: a profile with orders cannot be deleted.
  customer_id           uuid not null references public.profiles (id) on delete restrict,
  customer_name         text not null check (char_length(customer_name) between 2 and 80),
  customer_email        text not null check (char_length(customer_email) between 3 and 254),
  address               text not null check (char_length(address) between 1 and 200),
  city                  text not null check (char_length(city) between 1 and 100),
  zip                   text not null check (zip ~ '^[0-9]{5}$'),
  subtotal_cents        integer not null check (subtotal_cents >= 0),
  shipping_cents        integer not null check (shipping_cents >= 0),
  tax_cents             integer not null check (tax_cents >= 0),
  -- The total must always add up, so a bug can never store a wrong total.
  total_cents           integer not null check (total_cents = subtotal_cents + shipping_cents + tax_cents),
  community_gift_cents  integer not null default 0 check (community_gift_cents >= 0),
  status                text not null default 'Placed'
                        check (status in ('Placed', 'Packed', 'Shipped', 'Cancelled')),
  -- One checkout click = one order, even if the button is pressed twice (NFR-INT-02).
  idempotency_key       uuid not null unique,
  -- Path of the saved .eml confirmation file; null until it is written.
  email_file            text,
  created_at            timestamptz not null default now(),
  updated_at            timestamptz not null default now()
);

comment on table public.orders is 'Demo orders. Created only by place_order(); no payment data.';

-- Customers list their own orders; staff list the newest first.
create index orders_customer_id_idx on public.orders (customer_id);
create index orders_created_at_idx on public.orders (created_at desc);

create trigger orders_set_updated_at
  before update on public.orders
  for each row execute function private.set_updated_at();

create table public.order_items (
  id                    bigint generated always as identity primary key,
  -- Deleting an order (only in reset_demo.sql) removes its lines too.
  order_id              bigint not null references public.orders (id) on delete cascade,
  -- A product that has been ordered cannot be deleted; deactivate it instead (NFR-INT-05).
  product_id            bigint not null references public.products (id) on delete restrict,
  -- Name and prices are copied at purchase time, so later edits never change old orders (NFR-INT-03).
  sku                   text not null,
  product_name          text not null,
  unit_price_cents      integer not null check (unit_price_cents > 0),
  qty                   integer not null check (qty between 1 and 10),
  community_gift_cents  integer not null default 0 check (community_gift_cents >= 0),
  line_total_cents      integer not null check (line_total_cents = unit_price_cents * qty),
  -- Each product appears once per order (the quantity says how many).
  unique (order_id, product_id)
);

comment on table public.order_items is 'Lines of an order, with product name and prices frozen at purchase.';

-- order_id is already indexed by the unique (order_id, product_id) constraint.
create index order_items_product_id_idx on public.order_items (product_id);

-- Only allowed status changes (NFR-INT-07):
--   Placed -> Packed -> Shipped, and Placed/Packed -> Cancelled.
-- Cancelling must go through cancel_order() (Prompt C) so the stock is put back;
-- that function switches on the "app.allow_cancel" setting for its own transaction only.
create or replace function private.check_order_status_change()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  if new.status = old.status then
    return new;
  end if;

  if not (
       (old.status = 'Placed' and new.status in ('Packed', 'Cancelled'))
    or (old.status = 'Packed' and new.status in ('Shipped', 'Cancelled'))
  ) then
    raise exception 'Order % cannot change from % to %', old.order_number, old.status, new.status
      using errcode = 'check_violation';
  end if;

  if new.status = 'Cancelled' and coalesce(current_setting('app.allow_cancel', true), '') <> 'on' then
    raise exception 'Use cancel_order() to cancel an order, so its stock is restored'
      using errcode = 'insufficient_privilege';
  end if;

  return new;
end;
$$;

create trigger orders_check_status_change
  before update of status on public.orders
  for each row execute function private.check_order_status_change();

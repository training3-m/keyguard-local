-- 0004_logs.sql
-- Logs that explain every stock change and every sensitive owner action.
-- Both are written ONLY by database triggers and functions, never by the website directly,
-- so a log entry is always saved in the same transaction as the change it describes (NFR-INT-06).
-- Spec: 03 §7 (logging) and §12 (data integrity).

create table public.inventory_log (
  id          bigint generated always as identity primary key,
  -- If an (unordered) product is deleted, its stock history goes with it.
  product_id  bigint not null references public.products (id) on delete cascade,
  -- How much the stock changed: negative for sales, positive for restocks.
  delta       integer not null check (delta <> 0),
  reason      text not null check (reason in ('order', 'cancel', 'staff_edit', 'owner_edit', 'seed')),
  order_id    bigint references public.orders (id) on delete set null,
  -- Who made the change; null for seed data or a deleted account.
  actor       uuid references public.profiles (id) on delete set null,
  created_at  timestamptz not null default now()
);

comment on table public.inventory_log is 'Every stock change, written automatically by a trigger on products.';

create index inventory_log_product_id_idx on public.inventory_log (product_id);
create index inventory_log_order_id_idx on public.inventory_log (order_id);
create index inventory_log_actor_idx on public.inventory_log (actor);

create table public.audit_log (
  id          bigint generated always as identity primary key,
  actor       uuid references public.profiles (id) on delete set null,
  action      text not null,
  -- What was changed, for example a SKU, an order number or a user id.
  target      text not null,
  details     jsonb not null default '{}'::jsonb,
  created_at  timestamptz not null default now()
);

comment on table public.audit_log is 'Sensitive owner actions: product create/delete/price change, cancels, role changes.';

create index audit_log_actor_idx on public.audit_log (actor);
create index audit_log_created_at_idx on public.audit_log (created_at desc);

-- Writes an inventory_log row whenever a product's stock changes.
-- The reason comes from the "app.stock_reason" setting that place_order() and cancel_order()
-- set for their own transaction (Prompt C); a plain edit in the Manage pages counts as a
-- staff or owner edit. Never logs a password, token or address (NFR-LOG-03).
create or replace function private.log_stock_change()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  change_reason text := nullif(current_setting('app.stock_reason', true), '');
  change_order  bigint := nullif(current_setting('app.stock_order_id', true), '')::bigint;
  editor_role   text;
begin
  if change_reason is null then
    select p.role into editor_role from public.profiles p where p.id = (select auth.uid());
    change_reason := case when editor_role = 'owner' then 'owner_edit' else 'staff_edit' end;
  end if;

  insert into public.inventory_log (product_id, delta, reason, order_id, actor)
  values (new.id, new.stock_qty - old.stock_qty, change_reason, change_order, (select auth.uid()));
  return new;
end;
$$;

create trigger products_log_stock_change
  after update of stock_qty on public.products
  for each row
  when (new.stock_qty is distinct from old.stock_qty)
  execute function private.log_stock_change();

-- Records product creation, deletion and price or gift changes in the audit log (NFR-LOG-02).
create or replace function private.audit_product_change()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  if tg_op = 'INSERT' then
    insert into public.audit_log (actor, action, target, details)
    values ((select auth.uid()), 'product_created', new.sku,
            jsonb_build_object('price_cents', new.price_cents, 'community_gift_cents', new.community_gift_cents));
    return new;
  elsif tg_op = 'DELETE' then
    insert into public.audit_log (actor, action, target, details)
    values ((select auth.uid()), 'product_deleted', old.sku, jsonb_build_object('name', old.name));
    return old;
  elsif new.price_cents is distinct from old.price_cents
     or new.community_gift_cents is distinct from old.community_gift_cents then
    insert into public.audit_log (actor, action, target, details)
    values ((select auth.uid()), 'product_price_changed', new.sku,
            jsonb_build_object('old_price_cents', old.price_cents, 'new_price_cents', new.price_cents,
                               'old_gift_cents', old.community_gift_cents, 'new_gift_cents', new.community_gift_cents));
  end if;
  return new;
end;
$$;

create trigger products_audit_change
  after insert or delete or update of price_cents, community_gift_cents on public.products
  for each row execute function private.audit_product_change();

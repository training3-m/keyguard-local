-- 0005_row_level_security.sql
-- Who can see and change what, enforced by the database itself (Row Level Security).
-- Even if the website has a bug, these rules still protect the data (NFR-ROLE-02, layer 3).
-- Spec: docs/requirements/03-non-functional-requirements.md §3 and §4.2.
--
-- Roles (from public.profiles.role):
--   guest    = not signed in (Postgres role "anon")
--   customer = signed in, default role
--   staff    = signed in, role 'staff'
--   owner    = signed in, role 'owner'

-------------------------------------------------------------------------------
-- 1. Helper functions used by the policies
-------------------------------------------------------------------------------

-- Returns the signed-in person's role, or null for guests.
-- SECURITY DEFINER so it can read profiles without being blocked by the profiles policies
-- (otherwise the profiles policy would have to check itself, forever).
create or replace function private.current_app_role()
returns text
language sql
stable
security definer
set search_path = ''
as $$
  select p.role from public.profiles p where p.id = (select auth.uid());
$$;

create or replace function private.is_staff_or_owner()
returns boolean
language sql
stable
set search_path = ''
as $$
  select coalesce(private.current_app_role() in ('staff', 'owner'), false);
$$;

create or replace function private.is_owner()
returns boolean
language sql
stable
set search_path = ''
as $$
  select coalesce(private.current_app_role() = 'owner', false);
$$;

-- Nobody may call private functions by default; the policies below need these three.
-- The "private" schema is not exposed by the Supabase API, so the browser still cannot call them.
revoke all on all functions in schema private from public;
grant usage on schema private to anon, authenticated;
grant execute on function private.current_app_role() to anon, authenticated;
grant execute on function private.is_staff_or_owner() to anon, authenticated;
grant execute on function private.is_owner() to anon, authenticated;

-------------------------------------------------------------------------------
-- 2. Rules that a policy cannot express (they compare the old and new row)
-------------------------------------------------------------------------------

-- SKUs never change, and only the owner may change a price or community gift (US-MGT-04).
-- Changes made in the Supabase dashboard (no signed-in user) are allowed, for fixing seed data.
create or replace function private.guard_product_update()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  if new.sku is distinct from old.sku then
    raise exception 'A product SKU cannot be changed (%)', old.sku
      using errcode = 'check_violation';
  end if;

  if (new.price_cents is distinct from old.price_cents
      or new.community_gift_cents is distinct from old.community_gift_cents)
     and (select auth.uid()) is not null
     and not private.is_owner() then
    raise exception 'Only the owner can change prices or community gifts'
      using errcode = 'insufficient_privilege';
  end if;

  return new;
end;
$$;

create trigger products_guard_update
  before update on public.products
  for each row execute function private.guard_product_update();

-------------------------------------------------------------------------------
-- 3. Table privileges: start from nothing, then allow only what is needed
-------------------------------------------------------------------------------

revoke all on table public.profiles, public.products, public.orders,
                    public.order_items, public.inventory_log, public.audit_log
  from anon, authenticated;

-- Guests may only read products. Signed-in users may read products; staff/owner policies limit writes.
grant select on table public.products to anon, authenticated;
grant insert, update, delete on table public.products to authenticated;

-- Signed-in users may read profiles (policies limit which) and change only their own name.
grant select on table public.profiles to authenticated;
grant update (full_name) on table public.profiles to authenticated;

-- Orders are created only by place_order() (Prompt C); staff/owner may change only the status.
grant select on table public.orders to authenticated;
grant update (status) on table public.orders to authenticated;

-- Order lines and logs are read-only for everyone; triggers and functions write them.
grant select on table public.order_items, public.inventory_log, public.audit_log to authenticated;

-------------------------------------------------------------------------------
-- 4. Turn on Row Level Security for every table
-------------------------------------------------------------------------------

alter table public.profiles      enable row level security;
alter table public.products      enable row level security;
alter table public.orders        enable row level security;
alter table public.order_items   enable row level security;
alter table public.inventory_log enable row level security;
alter table public.audit_log     enable row level security;

-------------------------------------------------------------------------------
-- 5. Policies
-- (select ...) around function calls makes Postgres run them once per query, not once per row.
-------------------------------------------------------------------------------

-- products ---------------------------------------------------------------

-- Everyone, signed in or not, can browse products that are on sale.
create policy "Anyone can see active products"
  on public.products for select
  to anon, authenticated
  using (is_active);

-- Staff and the owner also see hidden (inactive) products so they can manage them.
create policy "Staff and owner can see all products"
  on public.products for select
  to authenticated
  using ((select private.is_staff_or_owner()));

-- Staff and the owner can edit products; the guard trigger stops staff changing prices.
create policy "Staff and owner can edit products"
  on public.products for update
  to authenticated
  using ((select private.is_staff_or_owner()))
  with check ((select private.is_staff_or_owner()));

-- Only the owner can add new products to the catalog.
create policy "Only the owner can add products"
  on public.products for insert
  to authenticated
  with check ((select private.is_owner()));

-- Only the owner can delete a product (and only if it was never ordered, thanks to the foreign key).
create policy "Only the owner can delete products"
  on public.products for delete
  to authenticated
  using ((select private.is_owner()));

-- profiles ---------------------------------------------------------------

-- People can see their own profile, for example to show their name and role in the menu.
create policy "People can see their own profile"
  on public.profiles for select
  to authenticated
  using (id = (select auth.uid()));

-- Staff and the owner can see all profiles, for order lookups and the Staff & Users page.
create policy "Staff and owner can see all profiles"
  on public.profiles for select
  to authenticated
  using ((select private.is_staff_or_owner()));

-- People can change their own name; the column grant above stops them changing their role.
create policy "People can edit their own name"
  on public.profiles for update
  to authenticated
  using (id = (select auth.uid()))
  with check (id = (select auth.uid()));

-- orders -----------------------------------------------------------------

-- Customers can only ever see their own orders, never anyone else's (NFR-PRIV-03).
create policy "Customers can see their own orders"
  on public.orders for select
  to authenticated
  using (customer_id = (select auth.uid()));

-- Staff and the owner can see every order so they can pack and ship them.
create policy "Staff and owner can see all orders"
  on public.orders for select
  to authenticated
  using ((select private.is_staff_or_owner()));

-- Staff and the owner can move an order to Packed or Shipped; cancelling needs cancel_order().
create policy "Staff and owner can update order status"
  on public.orders for update
  to authenticated
  using ((select private.is_staff_or_owner()))
  with check ((select private.is_staff_or_owner()));

-- order_items ------------------------------------------------------------

-- Customers can see the lines of their own orders only.
create policy "Customers can see lines of their own orders"
  on public.order_items for select
  to authenticated
  using (exists (
    select 1 from public.orders o
    where o.id = order_items.order_id
      and o.customer_id = (select auth.uid())
  ));

-- Staff and the owner can see every order line.
create policy "Staff and owner can see all order lines"
  on public.order_items for select
  to authenticated
  using ((select private.is_staff_or_owner()));

-- inventory_log ----------------------------------------------------------

-- Staff and the owner can read the stock history; nobody can edit it.
create policy "Staff and owner can read the stock log"
  on public.inventory_log for select
  to authenticated
  using ((select private.is_staff_or_owner()));

-- audit_log --------------------------------------------------------------

-- Only the owner can read the audit log of sensitive actions.
create policy "Only the owner can read the audit log"
  on public.audit_log for select
  to authenticated
  using ((select private.is_owner()));

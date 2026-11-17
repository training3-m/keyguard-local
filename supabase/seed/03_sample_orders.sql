-- 03_sample_orders.sql
-- Three past orders for the demo customer, so My Orders, the dashboard and Manage Orders have
-- something to show before checkout is built. Run after 01_products.sql and 02_demo_roles.sql.
-- These are history only: they do not change stock. Safe to run again (existing order numbers are skipped).
-- Totals follow 01-product.md §A6: free shipping from $75, otherwise $4.99; 8% tax.

do $$
declare
  v_customer uuid;
  v_order_id bigint;
  o record;
begin
  select id into v_customer from auth.users where email = 'customer@example.com';
  if v_customer is null then
    raise exception 'Create customer@example.com first (docs/deployment/demo-accounts.md)';
  end if;

  for o in
    select * from (values
      -- order number,     status,    placed,       sku,          qty
      ('KG-20261102-0001', 'Shipped', '2026-11-02', 'KG-PRO-64',  1),
      ('KG-20261105-0001', 'Packed',  '2026-11-05', 'KG-ESS-16',  2),
      ('KG-20261108-0001', 'Placed',  '2026-11-08', 'KG-RCE-32',  1)
    ) as v(order_number, status, placed, sku, qty)
  loop
    continue when exists (select 1 from public.orders where order_number = o.order_number);

    insert into public.orders (
      order_number, customer_id, customer_name, customer_email, address, city, zip,
      subtotal_cents, shipping_cents, tax_cents, total_cents, community_gift_cents,
      status, idempotency_key, created_at, updated_at)
    select o.order_number, v_customer, 'Demo Customer', 'customer@example.com',
           '123 Demo Street', 'Rancho', '12345',
           t.subtotal, t.shipping, t.tax, t.subtotal + t.shipping + t.tax, p.community_gift_cents * o.qty,
           o.status, gen_random_uuid(), o.placed::timestamptz, o.placed::timestamptz
    from public.products p
    cross join lateral (
      select p.price_cents * o.qty as subtotal,
             case when p.price_cents * o.qty >= 7500 then 0 else 499 end as shipping,
             round(p.price_cents * o.qty * 0.08)::integer as tax
    ) as t
    where p.sku = o.sku
    returning id into v_order_id;

    insert into public.order_items (
      order_id, product_id, sku, product_name, unit_price_cents, qty, community_gift_cents, line_total_cents)
    select v_order_id, p.id, p.sku, p.name, p.price_cents, o.qty,
           p.community_gift_cents * o.qty, p.price_cents * o.qty
    from public.products p
    where p.sku = o.sku;
  end loop;
end $$;

select order_number, status, total_cents, community_gift_cents
from public.orders
where customer_email = 'customer@example.com'
order by order_number;

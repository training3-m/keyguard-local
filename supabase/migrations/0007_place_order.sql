-- 0007_place_order.sql
-- The one "all or nothing" action in the store: placing an order (US-CHK-03).
-- In ONE transaction it checks stock, creates the order and its lines, lowers the stock and logs it.
-- If anything fails, nothing is saved. Calling it again with the same checkout key is safe.
-- Spec: 03 NFR-DB-01, NFR-INT-01..04; 01-product.md §A6 (shipping, tax, order number).

create or replace function public.place_order(
  p_items           jsonb,  -- [{"sku": "KG-PRO-64", "qty": 2}, ...] from the cart
  p_shipping        jsonb,  -- {"full_name": "...", "address": "...", "city": "...", "zip": "12345"}
  p_idempotency_key uuid    -- one random key per checkout attempt, kept in the browser session
)
returns jsonb
language plpgsql
security definer          -- needs to write orders and stock, which customers cannot do directly
set search_path = ''      -- every table is written with its schema, so nothing can be swapped in
as $$
declare
  v_customer      uuid := (select auth.uid());
  v_email         text;
  v_existing      public.orders;
  v_line          record;
  v_product       public.products;
  v_lines         jsonb := '[]'::jsonb;
  v_subtotal      integer := 0;
  v_gift          integer := 0;
  v_shipping      integer;
  v_tax           integer;
  v_today         text := to_char(current_date, 'YYYYMMDD');
  v_next          integer;
  v_order_number  text;
  v_order_id      bigint;
begin
  -- 1. Only signed-in people can order (US-CHK-01).
  if v_customer is null then
    raise exception 'Please sign in to place an order' using errcode = 'insufficient_privilege';
  end if;
  if p_idempotency_key is null then
    raise exception 'Missing checkout key' using errcode = 'invalid_parameter_value';
  end if;

  -- 2. Same checkout key again (double click, page refresh)? Return the first order, do nothing new.
  --    The lock makes two identical clicks wait for each other instead of racing (NFR-INT-02).
  perform pg_advisory_xact_lock(hashtextextended(p_idempotency_key::text, 0));
  select * into v_existing from public.orders where idempotency_key = p_idempotency_key;
  if found then
    if v_existing.customer_id <> v_customer then
      raise exception 'This checkout key belongs to another order' using errcode = 'insufficient_privilege';
    end if;
    return jsonb_build_object(
      'order_number', v_existing.order_number, 'order_id', v_existing.id,
      'subtotal_cents', v_existing.subtotal_cents, 'shipping_cents', v_existing.shipping_cents,
      'tax_cents', v_existing.tax_cents, 'total_cents', v_existing.total_cents,
      'community_gift_cents', v_existing.community_gift_cents, 'already_placed', true);
  end if;

  -- 3. Check the cart and the shipping details, with messages a shopper understands.
  if p_items is null or jsonb_typeof(p_items) <> 'array' or jsonb_array_length(p_items) = 0 then
    raise exception 'Your cart is empty' using errcode = 'invalid_parameter_value';
  end if;
  if jsonb_array_length(p_items) > 20 then
    raise exception 'Too many different items in one order (max 20)' using errcode = 'invalid_parameter_value';
  end if;
  if coalesce(char_length(trim(p_shipping ->> 'full_name')), 0) not between 2 and 80 then
    raise exception 'Please enter your full name (2 to 80 characters)' using errcode = 'invalid_parameter_value';
  end if;
  if coalesce(trim(p_shipping ->> 'address'), '') = '' or coalesce(trim(p_shipping ->> 'city'), '') = '' then
    raise exception 'Please enter your address and city' using errcode = 'invalid_parameter_value';
  end if;
  if coalesce(p_shipping ->> 'zip', '') !~ '^[0-9]{5}$' then
    raise exception 'ZIP code must be 5 digits' using errcode = 'invalid_parameter_value';
  end if;

  -- The confirmation goes to the account's own email, never one typed at checkout.
  select u.email into v_email from auth.users u where u.id = v_customer;

  -- 4. Lock each product and check its stock. Locking in SKU order means two shoppers
  --    can never block each other forever. Prices come from the database, never the browser.
  for v_line in
    select upper(trim(e ->> 'sku')) as sku, sum((e ->> 'qty')::integer) as qty
    from jsonb_array_elements(p_items) as e
    group by 1
    order by 1
  loop
    if v_line.qty is null or v_line.qty not between 1 and 10 then
      raise exception 'Quantity for % must be between 1 and 10', v_line.sku
        using errcode = 'invalid_parameter_value';
    end if;

    select * into v_product from public.products where sku = v_line.sku for update;
    if not found or not v_product.is_active then
      raise exception 'Product % is not available', v_line.sku using errcode = 'invalid_parameter_value';
    end if;
    if v_product.stock_qty < v_line.qty then
      raise exception 'Not enough stock for % (only % left)', v_product.name, v_product.stock_qty
        using errcode = 'check_violation';
    end if;

    v_subtotal := v_subtotal + v_product.price_cents * v_line.qty;
    v_gift     := v_gift + v_product.community_gift_cents * v_line.qty;
    v_lines    := v_lines || jsonb_build_object(
                    'product_id', v_product.id, 'sku', v_product.sku, 'name', v_product.name,
                    'price', v_product.price_cents, 'gift', v_product.community_gift_cents, 'qty', v_line.qty);
  end loop;

  -- 5. Totals (01-product.md §A6): free shipping from $75, otherwise $4.99; 8% tax on the subtotal,
  --    rounded once to the nearest cent (NFR-INT-04).
  v_shipping := case when v_subtotal >= 7500 then 0 else 499 end;
  v_tax      := round(v_subtotal * 0.08)::integer;

  -- 6. Order number KG-YYYYMMDD-NNNN, counting up each day. The lock stops two orders getting the same number.
  perform pg_advisory_xact_lock(hashtextextended('keyguard_order_number', 0));
  select coalesce(max(right(o.order_number, 4)::integer), 0) + 1 into v_next
  from public.orders o
  where o.order_number like 'KG-' || v_today || '-%';
  if v_next > 9999 then
    raise exception 'Too many orders today' using errcode = 'program_limit_exceeded';
  end if;
  v_order_number := 'KG-' || v_today || '-' || lpad(v_next::text, 4, '0');

  -- 7. Save the order and its lines (names and prices frozen, NFR-INT-03).
  insert into public.orders (
    order_number, customer_id, customer_name, customer_email, address, city, zip,
    subtotal_cents, shipping_cents, tax_cents, total_cents, community_gift_cents, idempotency_key)
  values (
    v_order_number, v_customer, trim(p_shipping ->> 'full_name'), v_email,
    trim(p_shipping ->> 'address'), trim(p_shipping ->> 'city'), p_shipping ->> 'zip',
    v_subtotal, v_shipping, v_tax, v_subtotal + v_shipping + v_tax, v_gift, p_idempotency_key)
  returning id into v_order_id;

  insert into public.order_items (
    order_id, product_id, sku, product_name, unit_price_cents, qty, community_gift_cents, line_total_cents)
  select v_order_id, (l ->> 'product_id')::bigint, l ->> 'sku', l ->> 'name',
         (l ->> 'price')::integer, (l ->> 'qty')::integer,
         (l ->> 'gift')::integer * (l ->> 'qty')::integer,
         (l ->> 'price')::integer * (l ->> 'qty')::integer
  from jsonb_array_elements(v_lines) as l;

  -- 8. Lower the stock. The trigger from 0004 logs each change with reason 'order' and this order's id.
  perform set_config('app.stock_reason', 'order', true);
  perform set_config('app.stock_order_id', v_order_id::text, true);
  update public.products p
  set stock_qty = p.stock_qty - (l ->> 'qty')::integer
  from jsonb_array_elements(v_lines) as l
  where p.id = (l ->> 'product_id')::bigint;
  perform set_config('app.stock_reason', '', true);
  perform set_config('app.stock_order_id', '', true);

  return jsonb_build_object(
    'order_number', v_order_number, 'order_id', v_order_id,
    'subtotal_cents', v_subtotal, 'shipping_cents', v_shipping, 'tax_cents', v_tax,
    'total_cents', v_subtotal + v_shipping + v_tax, 'community_gift_cents', v_gift,
    'already_placed', false);
end;
$$;

comment on function public.place_order(jsonb, jsonb, uuid) is
  'Places a demo order in one transaction: checks stock, saves order and lines, lowers stock. Safe to repeat with the same key.';

-- Only signed-in users may call it (NFR-DB-03). Guests and the public get nothing.
revoke all on function public.place_order(jsonb, jsonb, uuid) from public, anon;
grant execute on function public.place_order(jsonb, jsonb, uuid) to authenticated;

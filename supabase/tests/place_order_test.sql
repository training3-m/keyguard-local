-- place_order_test.sql
-- Proves that place_order() (0007) cannot over-book and cannot run twice for the same checkout key.
-- Run in the Supabase SQL Editor on the DEV project, after the demo accounts exist.
-- It runs as the demo customer, uses its own test product, and deletes everything it created.
-- PASS: one row "ALL PLACE_ORDER TESTS PASSED". FAIL: an error starting with "TEST n FAILED"
-- (and because the whole script is one transaction, a failure leaves nothing behind).

do $$
declare
  v_customer  uuid;
  v_key       uuid := gen_random_uuid();
  v_ship      jsonb := '{"full_name": "Test Customer", "address": "1 Test Way", "city": "Rancho", "zip": "12345"}';
  v_first     jsonb;
  v_second    jsonb;
  v_stock     integer;
  v_orders    integer;
  v_failed    boolean;
begin
  select id into v_customer from auth.users where email = 'customer@example.com';
  if v_customer is null then
    raise exception 'Create the demo accounts first (docs/deployment/demo-accounts.md)';
  end if;

  -- Setup (as the database admin): a test drive with exactly 1 in stock.
  insert into public.products (sku, name, category, price_cents, stock_qty)
  values ('KG-TEST-1', 'Test Drive (delete me)', 'Essentials', 1000, 1);

  -- From here on, act exactly like the signed-in demo customer using the website.
  perform set_config('request.jwt.claims',
                     json_build_object('sub', v_customer, 'role', 'authenticated')::text, true);
  perform set_config('role', 'authenticated', true);

  -- TEST 1: ordering 2 when only 1 is in stock must fail, and must not change the stock.
  v_failed := false;
  begin
    perform public.place_order('[{"sku": "KG-TEST-1", "qty": 2}]', v_ship, gen_random_uuid());
  exception when check_violation then
    v_failed := sqlerrm like 'Not enough stock%';
  end;
  if not v_failed then
    raise exception 'TEST 1 FAILED: ordering 2 with only 1 in stock was allowed';
  end if;

  -- TEST 2: the same checkout key twice (a double click) creates ONE order and lowers stock ONCE.
  v_first  := public.place_order('[{"sku": "KG-TEST-1", "qty": 1}]', v_ship, v_key);
  v_second := public.place_order('[{"sku": "KG-TEST-1", "qty": 1}]', v_ship, v_key);

  select count(*) into v_orders from public.orders where idempotency_key = v_key;
  if v_orders <> 1 or (v_second ->> 'order_number') <> (v_first ->> 'order_number')
     or (v_second ->> 'already_placed')::boolean is not true then
    raise exception 'TEST 2 FAILED: same key gave % orders (% and %)',
      v_orders, v_first ->> 'order_number', v_second ->> 'order_number';
  end if;

  -- Back to admin to read the stock (the test product is still active, but be explicit).
  perform set_config('role', 'none', true);
  select stock_qty into v_stock from public.products where sku = 'KG-TEST-1';
  if v_stock <> 0 then
    raise exception 'TEST 2 FAILED: stock should be 0 after one order, but is %', v_stock;
  end if;

  -- TEST 3: the order totals follow the rules: $10.00 + $4.99 shipping + $0.80 tax = $15.79.
  if (v_first ->> 'total_cents')::integer <> 1579 then
    raise exception 'TEST 3 FAILED: expected total 1579 cents, got %', v_first ->> 'total_cents';
  end if;

  -- Clean up everything this test created.
  delete from public.orders where idempotency_key = v_key;           -- its lines go with it
  delete from public.products where sku = 'KG-TEST-1';               -- its stock log goes with it
  delete from public.audit_log where target = 'KG-TEST-1';
end $$;

select 'ALL PLACE_ORDER TESTS PASSED' as result;

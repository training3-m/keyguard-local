-- 0008_order_and_role_functions.sql
-- Small functions for actions the website cannot do with a plain update, because of the security rules:
--   cancel_order          owner cancels an order and the stock goes back (US-MGT-09)
--   set_user_role         owner promotes a customer to staff, or back (US-MGT-10)
--   set_order_email_file  saves where the .eml confirmation was written (US-CHK-04)
-- Every function checks who is calling it before doing anything (NFR-DB-03).

-------------------------------------------------------------------------------
-- cancel_order
-------------------------------------------------------------------------------
create or replace function public.cancel_order(p_order_number text)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_order public.orders;
begin
  if not private.is_owner() then
    raise exception 'Only the owner can cancel orders' using errcode = 'insufficient_privilege';
  end if;

  -- Lock the order so two cancels at the same time cannot both restock it.
  select * into v_order from public.orders where order_number = p_order_number for update;
  if not found then
    raise exception 'Order % not found', p_order_number using errcode = 'no_data_found';
  end if;
  if v_order.status not in ('Placed', 'Packed') then
    raise exception 'Order % is % and cannot be cancelled', v_order.order_number, v_order.status
      using errcode = 'check_violation';
  end if;

  -- Put the stock back; the trigger from 0004 logs it with reason 'cancel'.
  perform set_config('app.stock_reason', 'cancel', true);
  perform set_config('app.stock_order_id', v_order.id::text, true);
  update public.products p
  set stock_qty = p.stock_qty + i.qty
  from public.order_items i
  where i.order_id = v_order.id and p.id = i.product_id;

  -- The status rule in 0003 only allows 'Cancelled' while this setting is on.
  perform set_config('app.allow_cancel', 'on', true);
  update public.orders set status = 'Cancelled' where id = v_order.id;

  perform set_config('app.allow_cancel', '', true);
  perform set_config('app.stock_reason', '', true);
  perform set_config('app.stock_order_id', '', true);

  insert into public.audit_log (actor, action, target, details)
  values ((select auth.uid()), 'order_cancelled', v_order.order_number,
          jsonb_build_object('previous_status', v_order.status, 'total_cents', v_order.total_cents));

  return jsonb_build_object('order_number', v_order.order_number, 'status', 'Cancelled');
end;
$$;

-------------------------------------------------------------------------------
-- set_user_role
-------------------------------------------------------------------------------
create or replace function public.set_user_role(p_user_id uuid, p_role text)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_old_role text;
begin
  if not private.is_owner() then
    raise exception 'Only the owner can change roles' using errcode = 'insufficient_privilege';
  end if;
  -- The owner role can never be given away from the website (NFR-ROLE-04).
  if p_role not in ('customer', 'staff') then
    raise exception 'Role must be customer or staff' using errcode = 'invalid_parameter_value';
  end if;
  if p_user_id = (select auth.uid()) then
    raise exception 'You cannot change your own role' using errcode = 'insufficient_privilege';
  end if;

  select role into v_old_role from public.profiles where id = p_user_id for update;
  if not found then
    raise exception 'User not found' using errcode = 'no_data_found';
  end if;
  if v_old_role = 'owner' then
    raise exception 'The owner role cannot be changed here' using errcode = 'insufficient_privilege';
  end if;

  update public.profiles set role = p_role where id = p_user_id;

  insert into public.audit_log (actor, action, target, details)
  values ((select auth.uid()), 'role_changed', p_user_id::text,
          jsonb_build_object('old_role', v_old_role, 'new_role', p_role));

  return jsonb_build_object('user_id', p_user_id, 'old_role', v_old_role, 'new_role', p_role);
end;
$$;

-------------------------------------------------------------------------------
-- set_order_email_file
-------------------------------------------------------------------------------
-- Customers cannot update orders directly, so the checkout page saves the email path through this.
create or replace function public.set_order_email_file(p_order_number text, p_path text)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  -- Only a safe file name inside outbox/ is accepted (NFR-SEC-07).
  if p_path is null or p_path !~ '^outbox/[A-Za-z0-9._@-]+\.eml$' then
    raise exception 'Invalid email file path' using errcode = 'invalid_parameter_value';
  end if;

  update public.orders
  set email_file = p_path
  where order_number = p_order_number
    and (customer_id = (select auth.uid()) or private.is_staff_or_owner());

  if not found then
    raise exception 'Order % not found', p_order_number using errcode = 'no_data_found';
  end if;
end;
$$;

-------------------------------------------------------------------------------
-- Who may call them: signed-in users only. Each function checks the role itself.
-------------------------------------------------------------------------------
revoke all on function public.cancel_order(text) from public, anon;
revoke all on function public.set_user_role(uuid, text) from public, anon;
revoke all on function public.set_order_email_file(text, text) from public, anon;
grant execute on function public.cancel_order(text) to authenticated;
grant execute on function public.set_user_role(uuid, text) to authenticated;
grant execute on function public.set_order_email_file(text, text) to authenticated;

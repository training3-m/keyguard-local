-- 0009_community_total.sql
-- The live "$X raised for Rancho Library" total on the banner (02-ui-ux.md §4.1, open question Q5).
-- Orders are private (0005), so guests can't add them up themselves. This function returns ONLY the
-- total, never any order details, so it is safe for everyone, signed in or not.

create or replace function public.community_total_cents()
returns bigint
language sql
stable
security definer
set search_path = ''
as $$
  -- Cancelled orders don't count: their money never "went" to the fund.
  select coalesce(sum(o.community_gift_cents), 0)::bigint
  from public.orders o
  where o.status <> 'Cancelled';
$$;

comment on function public.community_total_cents() is
  'Total community gift from all non-cancelled orders, in cents. Safe for guests: returns one number only.';

revoke all on function public.community_total_cents() from public;
grant execute on function public.community_total_cents() to anon, authenticated;

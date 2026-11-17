-- 02_demo_roles.sql
-- Gives the 3 demo accounts their names and roles. Run AFTER creating the accounts in the
-- Supabase dashboard (docs/deployment/demo-accounts.md). No passwords are stored in this repo.
-- This is also the one-time "create the first owner" step (NFR-ROLE-05). Safe to run again.

do $$
declare
  v_missing text;
begin
  select string_agg(e, ', ') into v_missing
  from unnest(array['owner@example.com', 'staff@example.com', 'customer@example.com']) as e
  where not exists (select 1 from auth.users u where u.email = e);

  if v_missing is not null then
    raise exception 'Create these accounts first (Authentication > Users > Add user): %', v_missing;
  end if;

  update public.profiles p
  set role = d.role, full_name = d.full_name
  from (values
          ('owner@example.com',    'owner',    'Demo Owner'),
          ('staff@example.com',    'staff',    'Demo Staff'),
          ('customer@example.com', 'customer', 'Demo Customer')
       ) as d(email, role, full_name)
  join auth.users u on u.email = d.email
  where p.id = u.id;
end $$;

select u.email, p.full_name, p.role
from public.profiles p
join auth.users u on u.id = p.id
where u.email like '%@example.com'
order by p.role;

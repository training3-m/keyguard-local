-- 0001_profiles.sql
-- One profile per sign-in account, holding the person's name and role.
-- Spec: docs/requirements/03-non-functional-requirements.md §3 (roles) and §4.1 (data model).

-- "private" holds helper functions that the website's API must never expose.
-- Supabase only exposes the "public" schema, so nothing here can be called from the browser.
create schema if not exists private;

-- Keeps "updated_at" correct on every change, so nobody has to remember to set it.
create or replace function private.set_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

create table public.profiles (
  -- Same id as the Supabase sign-in account; deleting the account deletes the profile.
  id          uuid primary key references auth.users (id) on delete cascade,
  full_name   text check (full_name is null or char_length(full_name) between 2 and 80),
  -- Everyone starts as a customer. Only the owner can change roles (set_user_role, Prompt C).
  role        text not null default 'customer' check (role in ('customer', 'staff', 'owner')),
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

comment on table public.profiles is 'One row per user account: display name and role (customer, staff, owner).';

create trigger profiles_set_updated_at
  before update on public.profiles
  for each row execute function private.set_updated_at();

-- Creates the profile automatically when someone registers.
-- SECURITY DEFINER because the new user has no right to insert profiles themselves.
-- The role is ALWAYS 'customer' here, whatever the sign-up form sends (NFR-ROLE-04).
create or replace function private.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  clean_name text := nullif(trim(new.raw_user_meta_data ->> 'full_name'), '');
begin
  -- Ignore a name that breaks the 2-80 character rule instead of blocking the sign-up.
  if clean_name is not null and char_length(clean_name) not between 2 and 80 then
    clean_name := null;
  end if;

  insert into public.profiles (id, full_name, role)
  values (new.id, clean_name, 'customer');
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function private.handle_new_user();

# Database Setup: Applying the Migrations

How to build the KeyGuard Local database in a Supabase project. Do this once for the **dev** project now, and later for the **demo** project. The **same files, in the same order**, go everywhere (NFR-ENV-03).

## Before you start

- You're signed in to [supabase.com](https://supabase.com) and the project exists (dev: `keyguard-dev`).
- **Authentication → Sign In / Providers → Email → Confirm email** is **off** (NFR-AUTH-04).
- The project is **new and empty**. These files create tables and fail with "already exists" if run twice. If that happens, see "Starting over" below.

## Apply the files (SQL Editor, about 5 minutes)

Run the files **one at a time, in number order**. Each one depends on the ones before it.

| Order | File | What it creates |
|---|---|---|
| 1 | `supabase/migrations/0001_profiles.sql` | `private` schema, `profiles` table, trigger that creates a profile on sign-up |
| 2 | `supabase/migrations/0002_products.sql` | `products` table |
| 3 | `supabase/migrations/0003_orders.sql` | `orders` and `order_items` tables, order status rule |
| 4 | `supabase/migrations/0004_logs.sql` | `inventory_log` and `audit_log` tables, automatic logging triggers |
| 5 | `supabase/migrations/0005_row_level_security.sql` | Who can see and change what (security rules) |
| 6 | `supabase/migrations/0006_storage_product_images.sql` | `product-images` storage bucket and its rules |
| 7 | `supabase/migrations/0007_place_order.sql` | `place_order`: the all-or-nothing checkout (US-CHK-03) |
| 8 | `supabase/migrations/0008_order_and_role_functions.sql` | `cancel_order`, `set_user_role`, `set_order_email_file` |

### Then the sample data and the test

| Order | File | What it does |
|---|---|---|
| 9 | `supabase/seed/01_products.sql` | Adds the 11 products (10 for sale, 1 hidden) |
| — | *(dashboard)* | Create the 3 demo accounts: see [demo-accounts.md](demo-accounts.md) |
| 10 | `supabase/seed/02_demo_roles.sql` | Gives the demo accounts their names and roles |
| 11 | `supabase/seed/03_sample_orders.sql` | Adds 3 past orders for the demo customer |
| 12 | `supabase/tests/place_order_test.sql` | Proves checkout can't oversell or run twice. Expect **ALL PLACE_ORDER TESTS PASSED**. |

**Tip:** if copy-pasting long files is awkward, files can be combined and run **once** in a new, empty query. The SQL Editor runs the whole text as one transaction, so it's all-or-nothing.

For **each** file:

1. In VS Code, open the file and copy everything (**Ctrl + A**, then **Ctrl + C**).
2. In Supabase, click **SQL Editor** in the left sidebar, then **+ New query**.
3. Paste (**Ctrl + V**) and click **Run** (or press **Ctrl + Enter**).
4. **Check:** the result says **"Success. No rows returned"**. If you see an error, **stop** and copy the error message into Claude. Don't run the next file.

Supabase may warn about a "destructive operation" for file 5, because it contains `revoke`. That's expected: it removes default permissions on purpose. Click **Run this query**.

## Check it worked

Run this in a new SQL Editor query:

```sql
select tablename, rowsecurity as rls_on
from pg_tables
where schemaname = 'public'
order by tablename;
```

**Expected:** 6 tables (`audit_log`, `inventory_log`, `order_items`, `orders`, `products`, `profiles`), all with `rls_on = true`.

Then check the rules exist:

```sql
select tablename, count(*) as policies
from pg_policies
where schemaname in ('public', 'storage')
group by tablename
order by tablename;
```

**Expected:** `audit_log 1`, `inventory_log 1`, `objects 4`, `order_items 2`, `orders 3`, `products 5`, `profiles 3`.

Also check in **Storage** (left sidebar) that a **public** bucket called `product-images` exists.

## One safety check

Go to **Project Settings → Data API** (or **API**) and look at **Exposed schemas**. It should list `public` (and maybe `graphql_public`) but **not** `private`. The helper functions in `private` must never be callable from the browser.

## Alternative: Supabase CLI (optional, for later)

If the team installs the [Supabase CLI](https://supabase.com/docs/guides/cli), the same files can be applied with `supabase link` and `supabase db push` instead of copy-paste. The SQL Editor is enough for this class.

## Starting over (dev project only)

If a file fails halfway and you want a clean start, the simplest way in a class is: **Project Settings → General → delete the project**, create a new empty one, update `.env` and `.streamlit/secrets.toml` with the new URL and key, and apply the files again from 0001.

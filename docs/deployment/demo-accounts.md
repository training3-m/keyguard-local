# Demo Accounts

Three made-up accounts, one per role, used for testing and the class demo (01-product.md §A5). **Passwords are never written in this repo.** Each Supabase project (dev, demo) gets its own accounts.

| Email | Role | Name |
|---|---|---|
| `owner@example.com` | owner | Demo Owner |
| `staff@example.com` | staff | Demo Staff |
| `customer@example.com` | customer | Demo Customer |

`@example.com` is a domain reserved for examples, so no real person gets these emails.

## 1. Create the accounts (Supabase dashboard)

Do this 3 times, once per email:

1. In Supabase, go to **Authentication** → **Users** → **Add user** → **Create new user**.
2. **Email:** the email from the table.
3. **Password:** choose one yourself (8+ characters, at least one letter and one number, NFR-AUTH-02).
4. Tick **Auto Confirm User**, so no confirmation email is needed.
5. Click **Create user**.

**Passwords:** store them in a password manager. Share them with teammates **privately**, for example in a direct message, never in GitHub, issues, code or prompts to Claude.

Each new account automatically gets the role `customer` (trigger in `0001_profiles.sql`).

## 2. Give them their roles

Run `supabase/seed/02_demo_roles.sql` in the **SQL Editor**. It sets the names and roles above and shows a small table to confirm. If an account is missing, it tells you which one to create.

This is also the one-time step that creates the **first owner** (NFR-ROLE-05). After this, the owner promotes staff from the website (US-MGT-10).

## 3. Add sample orders

Run `supabase/seed/03_sample_orders.sql`. It adds three past orders for the demo customer (Shipped, Packed, Placed), so the order pages have something to show.

## Using real teammates instead

When teammates register in the app, they become customers. The owner can then make one of them staff from the Staff & Users page (US-MGT-10), or by running `select public.set_user_role('<their user id>', 'staff');` while signed in as the owner.

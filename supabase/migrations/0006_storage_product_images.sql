-- 0006_storage_product_images.sql
-- A storage folder ("bucket") for product photos, uploaded from the Manage pages (US-MGT-07).
-- Spec: 03 NFR-SEC-06 and NFR-CHILD-05: PNG or JPG only, 2 MB max, only staff and owner upload.

-- Public bucket: anyone can VIEW an image by its link, which the shop needs.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('product-images', 'product-images', true, 2097152, array['image/png', 'image/jpeg'])
on conflict (id) do nothing;

-- Staff and the owner can list the bucket's files (needed to replace an existing image).
create policy "Staff and owner can list product images"
  on storage.objects for select
  to authenticated
  using (bucket_id = 'product-images' and (select private.is_staff_or_owner()));

-- Only staff and the owner can upload product images; customers and guests cannot.
create policy "Staff and owner can upload product images"
  on storage.objects for insert
  to authenticated
  with check (bucket_id = 'product-images' and (select private.is_staff_or_owner()));

-- Only staff and the owner can replace a product image.
create policy "Staff and owner can replace product images"
  on storage.objects for update
  to authenticated
  using (bucket_id = 'product-images' and (select private.is_staff_or_owner()))
  with check (bucket_id = 'product-images' and (select private.is_staff_or_owner()));

-- Only staff and the owner can delete a product image.
create policy "Staff and owner can delete product images"
  on storage.objects for delete
  to authenticated
  using (bucket_id = 'product-images' and (select private.is_staff_or_owner()));

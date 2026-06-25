-- Supabase Storage: políticas para bucket existente `restaurant-documents`.
-- Si el bucket ya existe en el dashboard, solo ejecuta las políticas (sección 2+).
-- Si no existe, descomenta la sección 1 o créalo en Storage → New bucket → Public.

-- 1) Crear bucket (opcional — omitir si ya existe como restaurant-documents)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'restaurant-documents',
  'restaurant-documents',
  true,
  52428800,
  ARRAY[
    'image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/svg+xml',
    'application/pdf'
  ]::text[]
)
ON CONFLICT (id) DO UPDATE SET
  public = EXCLUDED.public,
  file_size_limit = EXCLUDED.file_size_limit,
  allowed_mime_types = EXCLUDED.allowed_mime_types;

-- 2) Lectura pública (GET /object/public/restaurant-documents/...)
DROP POLICY IF EXISTS "restaurant_documents_public_read" ON storage.objects;
CREATE POLICY "restaurant_documents_public_read"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'restaurant-documents');

-- 3) Escritura vía service_role (uploads firmados desde el backend)
DROP POLICY IF EXISTS "restaurant_documents_service_write" ON storage.objects;
CREATE POLICY "restaurant_documents_service_write"
ON storage.objects FOR INSERT
TO service_role
WITH CHECK (bucket_id = 'restaurant-documents');

DROP POLICY IF EXISTS "restaurant_documents_service_update" ON storage.objects;
CREATE POLICY "restaurant_documents_service_update"
ON storage.objects FOR UPDATE
TO service_role
USING (bucket_id = 'restaurant-documents')
WITH CHECK (bucket_id = 'restaurant-documents');

-- Verificación
SELECT id, name, public FROM storage.buckets WHERE id = 'restaurant-documents';

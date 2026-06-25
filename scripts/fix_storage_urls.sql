-- Corrige URLs de media guardadas con bucket/ruta incorrectos.
-- Bucket real: restaurant-documents
-- Ruta del objeto en bucket: restaurants/{id}/logo|cover|business_doc/...

UPDATE public.restaurante
SET imagen_destacada = regexp_replace(
  imagen_destacada,
  '^https://([^.]+)\.supabase\.co/restaurants/([0-9]+)/(.+)$',
  'https://\1.supabase.co/storage/v1/object/public/restaurant-documents/restaurants/\2/\3'
)
WHERE imagen_destacada ~ '^https://[^/]+\.supabase\.co/restaurants/[0-9]+/';

UPDATE public.restaurante
SET imagen_destacada = regexp_replace(
  imagen_destacada,
  '/storage/v1/object/public/restaurants/([0-9]+)/',
  '/storage/v1/object/public/restaurant-documents/restaurants/\1/'
)
WHERE imagen_destacada LIKE '%/object/public/restaurants/%';

UPDATE public.restaurante_imagen ri
SET url = 'https://bakkcbqdcuktgmzztxcr.supabase.co/storage/v1/object/public/restaurant-documents/' || ri.storage_key
WHERE storage_key <> '' AND (
  url IS NULL OR url = '' OR url NOT LIKE '%/object/public/restaurant-documents/%'
);

UPDATE public.documento_restaurante dr
SET url = 'https://bakkcbqdcuktgmzztxcr.supabase.co/storage/v1/object/public/restaurant-documents/' || dr.storage_key
WHERE storage_key <> '' AND (
  url IS NULL OR url = '' OR url NOT LIKE '%/object/public/restaurant-documents/%'
);

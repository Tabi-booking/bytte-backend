-- =============================================================================
-- Validación esquema Tabi / onboarding (solo lectura)
-- Ejecutar en Supabase SQL Editor. Debe devolver filas OK para cada check.
-- =============================================================================

-- Columnas esperadas en restaurante
SELECT 'restaurante.razon_social' AS check_name,
       EXISTS (
         SELECT 1 FROM information_schema.columns
         WHERE table_schema = 'public' AND table_name = 'restaurante' AND column_name = 'razon_social'
       ) AS ok
UNION ALL
SELECT 'restaurante.descripcion',
       EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'restaurante' AND column_name = 'descripcion')
UNION ALL
SELECT 'restaurante.sitio_web',
       EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'restaurante' AND column_name = 'sitio_web')
UNION ALL
SELECT 'restaurante.redes_sociales',
       EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'restaurante' AND column_name = 'redes_sociales')
UNION ALL
SELECT 'restaurante.capacidad_asientos',
       EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'restaurante' AND column_name = 'capacidad_asientos')
UNION ALL
SELECT 'restaurante.numero_mesas',
       EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'restaurante' AND column_name = 'numero_mesas')
UNION ALL
SELECT 'restaurante.onboarding_paso',
       EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'restaurante' AND column_name = 'onboarding_paso')
UNION ALL
SELECT 'restaurante.onboarding_estado',
       EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'restaurante' AND column_name = 'onboarding_estado')
UNION ALL
SELECT 'restaurante.onboarding_pct',
       EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'restaurante' AND column_name = 'onboarding_pct')
UNION ALL
SELECT 'restaurante.onboarding_datos',
       EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'restaurante' AND column_name = 'onboarding_datos')
UNION ALL
SELECT 'restaurante.onboarding_enviado_en',
       EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'restaurante' AND column_name = 'onboarding_enviado_en')
UNION ALL
SELECT 'restaurante.activo',
       EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'restaurante' AND column_name = 'activo')
UNION ALL
SELECT 'table.restaurante_categoria',
       EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'restaurante_categoria')
UNION ALL
SELECT 'table.restaurante_etiqueta',
       EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'restaurante_etiqueta')
UNION ALL
SELECT 'table.restaurante_tipo_reserva',
       EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'restaurante_tipo_reserva')
UNION ALL
SELECT 'table.restaurante_imagen',
       EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'restaurante_imagen')
UNION ALL
SELECT 'table.documento_restaurante',
       EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documento_restaurante')
UNION ALL
SELECT 'table.suscripcion_restaurante',
       EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'suscripcion_restaurante')
ORDER BY check_name;

-- Query de referencia: perfil completo (reemplaza :restaurant_id)
-- SELECT r.id, r.nombre, r.razon_social FROM restaurante r WHERE r.id = 1;

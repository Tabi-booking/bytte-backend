-- =============================================================================
-- BYTTE - Datos de ejemplo (poblar BD)
-- Ejecutar en Supabase → SQL Editor (una vez, o tras vaciar tablas).
-- Orden respetando claves foráneas.
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- 1. Referencias
-- -----------------------------------------------------------------------------

INSERT INTO public.ubicacion (pais, departamento, ciudad, barrio)
SELECT 'Colombia', 'Antioquia', 'Medellín', 'El Poblado'
WHERE NOT EXISTS (SELECT 1 FROM public.ubicacion WHERE ciudad = 'Medellín' AND barrio = 'El Poblado');

INSERT INTO public.ubicacion (pais, departamento, ciudad, barrio)
SELECT 'Colombia', 'Cundinamarca', 'Bogotá', 'Chapinero'
WHERE NOT EXISTS (SELECT 1 FROM public.ubicacion WHERE ciudad = 'Bogotá' AND barrio = 'Chapinero');

INSERT INTO public.ubicacion (pais, departamento, ciudad, barrio)
SELECT 'Colombia', 'Valle del Cauca', 'Cali', 'Granada'
WHERE NOT EXISTS (SELECT 1 FROM public.ubicacion WHERE ciudad = 'Cali' AND barrio = 'Granada');

INSERT INTO public.categorias (nombre) VALUES
  ('Italiana'),
  ('Japonesa'),
  ('Colombiana'),
  ('Mexicana'),
  ('Vegetariana')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO public.etiquetas (nombre, svg) VALUES
  ('Romántico', NULL),
  ('Familiar', NULL),
  ('Negocios', NULL),
  ('Terraza', NULL),
  ('Pet friendly', NULL)
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO public.rol (nombre) VALUES
  ('Propietario'),
  ('Administrador'),
  ('Mesero'),
  ('Cocinero'),
  ('Cajero')
ON CONFLICT (nombre) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 2. Restaurantes (usa primeros IDs de ubicación / categoría / etiqueta)
-- -----------------------------------------------------------------------------

INSERT INTO public.restaurante (
  id_acceso, nombre, direccion, telefono, calificacion, horarios,
  imagen_destacada, google_maps, rango_precios,
  id_ubicacion, id_categoria, id_etiqueta, activo
)
SELECT
  'acc-bog-001',
  'La Mesa del Centro',
  'Carrera 7 #71-21',
  '6015550101',
  4.5,
  'Lun-Dom 12:00-23:00',
  'https://example.com/la-mesa.jpg',
  'https://maps.google.com/?q=Bogota',
  '$$'::rango_precios_enum,
  u.id, c.id, e.id, TRUE
FROM (SELECT id FROM public.ubicacion WHERE ciudad = 'Bogotá' ORDER BY id LIMIT 1) u
CROSS JOIN (SELECT id FROM public.categorias WHERE nombre = 'Colombiana' ORDER BY id LIMIT 1) c
CROSS JOIN (SELECT id FROM public.etiquetas WHERE nombre = 'Familiar' ORDER BY id LIMIT 1) e
WHERE NOT EXISTS (SELECT 1 FROM public.restaurante WHERE id_acceso = 'acc-bog-001');

INSERT INTO public.restaurante (
  id_acceso, nombre, direccion, telefono, calificacion, horarios,
  imagen_destacada, google_maps, rango_precios,
  id_ubicacion, id_categoria, id_etiqueta, activo
)
SELECT
  'acc-med-002',
  'Sakura Sushi',
  'Calle 10 #43-12',
  '6044448899',
  4.8,
  'Mar-Dom 13:00-22:00',
  'https://example.com/sakura.jpg',
  'https://maps.google.com/?q=Medellin',
  '$$$'::rango_precios_enum,
  u.id, c.id, e.id, TRUE
FROM (SELECT id FROM public.ubicacion WHERE ciudad = 'Medellín' ORDER BY id LIMIT 1) u
CROSS JOIN (SELECT id FROM public.categorias WHERE nombre = 'Japonesa' ORDER BY id LIMIT 1) c
CROSS JOIN (SELECT id FROM public.etiquetas WHERE nombre = 'Romántico' ORDER BY id LIMIT 1) e
WHERE NOT EXISTS (SELECT 1 FROM public.restaurante WHERE id_acceso = 'acc-med-002');

INSERT INTO public.restaurante (
  id_acceso, nombre, direccion, telefono, calificacion, horarios,
  imagen_destacada, google_maps, rango_precios,
  id_ubicacion, id_categoria, id_etiqueta, activo
)
SELECT
  'acc-cal-003',
  'Nonna Pasta',
  'Av. 6 Norte #15-40',
  '6023332211',
  4.2,
  'Mié-Lun 11:30-22:00',
  'https://example.com/nonna.jpg',
  'https://maps.google.com/?q=Cali',
  '$$'::rango_precios_enum,
  u.id, c.id, e.id, TRUE
FROM (SELECT id FROM public.ubicacion WHERE ciudad = 'Cali' ORDER BY id LIMIT 1) u
CROSS JOIN (SELECT id FROM public.categorias WHERE nombre = 'Italiana' ORDER BY id LIMIT 1) c
CROSS JOIN (SELECT id FROM public.etiquetas WHERE nombre = 'Terraza' ORDER BY id LIMIT 1) e
WHERE NOT EXISTS (SELECT 1 FROM public.restaurante WHERE id_acceso = 'acc-cal-003');

-- -----------------------------------------------------------------------------
-- 3. Clientes
-- -----------------------------------------------------------------------------

INSERT INTO public.cliente (
  nombre, apellido, telefono, correo, contrasena,
  tipo_documento, numero_documento, activo
) VALUES
  ('Ana', 'García', '3001112233', 'ana.garcia@example.com', 'hash_demo_1', 'CC', '1098123456', TRUE),
  ('Luis', 'Martínez', '3004445566', 'luis.martinez@example.com', 'hash_demo_2', 'CC', '8012345678', TRUE),
  ('María', 'López', '3007778899', 'maria.lopez@example.com', 'hash_demo_3', 'CE', 'CE123456', TRUE)
ON CONFLICT (correo) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 4. Usuarios (empleados) ligados a rol y restaurante
-- -----------------------------------------------------------------------------
-- Contraseñas: valores demo en texto plano; la API acepta login con estos strings
-- y puede migrar a bcrypt al crear/actualizar usuarios (ver README).
-- -----------------------------------------------------------------------------

INSERT INTO public.usuario (
  nombre, apellido, telefono, correo, contrasena,
  tipo_documento, numero_documento, id_rol, id_restaurante, activo
)
SELECT
  'Carlos', 'Ruiz', '6010001122', 'carlos.ruiz@bytte.demo', 'hash_demo_u1',
  'CC', '79461234', r.id, res.id, TRUE
FROM (SELECT id FROM public.rol WHERE nombre = 'Administrador' LIMIT 1) r
CROSS JOIN (SELECT id FROM public.restaurante WHERE id_acceso = 'acc-bog-001' LIMIT 1) res
WHERE NOT EXISTS (SELECT 1 FROM public.usuario WHERE correo = 'carlos.ruiz@bytte.demo');

INSERT INTO public.usuario (
  nombre, apellido, telefono, correo, contrasena,
  tipo_documento, numero_documento, id_rol, id_restaurante, activo
)
SELECT
  'Diana', 'Pérez', '6040003344', 'diana.perez@bytte.demo', 'hash_demo_u2',
  'CC', '52987412', r.id, res.id, TRUE
FROM (SELECT id FROM public.rol WHERE nombre = 'Mesero' LIMIT 1) r
CROSS JOIN (SELECT id FROM public.restaurante WHERE id_acceso = 'acc-med-002' LIMIT 1) res
WHERE NOT EXISTS (SELECT 1 FROM public.usuario WHERE correo = 'diana.perez@bytte.demo');

-- -----------------------------------------------------------------------------
-- 5. Super usuarios
-- -----------------------------------------------------------------------------

INSERT INTO public.super_usuario (
  nombre, apellido, telefono, correo, contrasena, tipo_documento, numero_documento
) VALUES
  ('Admin', 'Bytte', '6000000000', 'admin@bytte.os', 'hash_super_demo', 'CC', '900000001')
ON CONFLICT (correo) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 6. Reservas
-- -----------------------------------------------------------------------------

INSERT INTO public.reserva (
  cantidad_personas, fecha, hora, codigo_reserva, comentarios, precio, preorden,
  id_restaurante, id_cliente, estado
)
SELECT
  4, CURRENT_DATE + 3, '20:00'::time, 'RES-BYT-001', 'Mesa ventana si es posible', 120000.00,
  NULL, r.id, c.id, 'CONFIRMADA'::estado_reserva_enum
FROM (SELECT id FROM public.restaurante WHERE id_acceso = 'acc-bog-001' LIMIT 1) r
CROSS JOIN (SELECT id FROM public.cliente WHERE correo = 'ana.garcia@example.com' LIMIT 1) c
WHERE NOT EXISTS (SELECT 1 FROM public.reserva WHERE codigo_reserva = 'RES-BYT-001');

INSERT INTO public.reserva (
  cantidad_personas, fecha, hora, codigo_reserva, comentarios, precio, preorden,
  id_restaurante, id_cliente, estado
)
SELECT
  2, CURRENT_DATE + 5, '19:30'::time, 'RES-BYT-002', NULL, 85000.00,
  NULL, r.id, c.id, 'PENDIENTE'::estado_reserva_enum
FROM (SELECT id FROM public.restaurante WHERE id_acceso = 'acc-med-002' LIMIT 1) r
CROSS JOIN (SELECT id FROM public.cliente WHERE correo = 'luis.martinez@example.com' LIMIT 1) c
WHERE NOT EXISTS (SELECT 1 FROM public.reserva WHERE codigo_reserva = 'RES-BYT-002');

-- -----------------------------------------------------------------------------
-- 7. Pedidos (por reserva)
-- -----------------------------------------------------------------------------

INSERT INTO public.pedido (cantidad, descripcion, precio_unitario, importe, id_reserva)
SELECT
  2, 'Menú degustación', 45000.00, 90000.00, rv.id
FROM public.reserva rv
WHERE rv.codigo_reserva = 'RES-BYT-001'
  AND NOT EXISTS (SELECT 1 FROM public.pedido p WHERE p.id_reserva = rv.id AND p.descripcion = 'Menú degustación');

INSERT INTO public.pedido (cantidad, descripcion, precio_unitario, importe, id_reserva)
SELECT
  1, 'Postre del día', 15000.00, 15000.00, rv.id
FROM public.reserva rv
WHERE rv.codigo_reserva = 'RES-BYT-001'
  AND NOT EXISTS (SELECT 1 FROM public.pedido p WHERE p.id_reserva = rv.id AND p.descripcion = 'Postre del día');

-- -----------------------------------------------------------------------------
-- 8. Pagos
-- -----------------------------------------------------------------------------

INSERT INTO public.pago (
  nombre_cliente, subtotal, iva, total, metodo_pago, fecha_pago,
  fecha_vencimiento, tiempo, logo, id_pedido, estado
)
SELECT
  'Ana García', 90000.00, 17100.00, 107100.00, 'TARJETA'::metodo_pago_enum, CURRENT_DATE,
  NULL, NULL, NULL, p.id, 'PAGADO'::estado_pago_enum
FROM public.pedido p
JOIN public.reserva rv ON rv.id = p.id_reserva
WHERE rv.codigo_reserva = 'RES-BYT-001' AND p.descripcion = 'Menú degustación'
  AND NOT EXISTS (SELECT 1 FROM public.pago pg WHERE pg.id_pedido = p.id);

-- -----------------------------------------------------------------------------
-- 9. Pedido adicional (reserva Medellín) — para demos de menú en otro local
-- -----------------------------------------------------------------------------

INSERT INTO public.pedido (cantidad, descripcion, precio_unitario, importe, id_reserva)
SELECT
  1, 'Chef omakase', 120000.00, 120000.00, rv.id
FROM public.reserva rv
WHERE rv.codigo_reserva = 'RES-BYT-002'
  AND NOT EXISTS (SELECT 1 FROM public.pedido p WHERE p.id_reserva = rv.id);

-- -----------------------------------------------------------------------------
-- 10. Horarios (public.horarios) — franjas por restaurante
--    Convención dia_semana: 0=domingo … 6=sábado
-- -----------------------------------------------------------------------------

INSERT INTO public.horarios (id_restaurante, dia_semana, hora_apertura, hora_cierre, etiqueta_dia, activo)
SELECT r.id, v.dia, v.ap, v.cr, v.etq, TRUE
FROM public.restaurante r
CROSS JOIN (VALUES
  ('acc-bog-001', 1, '12:00'::time, '23:00'::time, 'Lunes'),
  ('acc-bog-001', 2, '12:00'::time, '23:00'::time, 'Martes'),
  ('acc-bog-001', 5, '12:00'::time, '23:30'::time, 'Viernes'),
  ('acc-bog-001', 6, '12:00'::time, '23:30'::time, 'Sábado'),
  ('acc-med-002', 3, '13:00'::time, '22:00'::time, 'Miércoles'),
  ('acc-med-002', 4, '13:00'::time, '22:30'::time, 'Jueves'),
  ('acc-med-002', 5, '13:00'::time, '23:00'::time, 'Viernes'),
  ('acc-med-002', 6, '13:00'::time, '23:00'::time, 'Sábado'),
  ('acc-cal-003', 1, '11:30'::time, '22:00'::time, 'Lunes'),
  ('acc-cal-003', 4, '11:30'::time, '22:00'::time, 'Jueves'),
  ('acc-cal-003', 0, '12:00'::time, '21:00'::time, 'Domingo')
) AS v(acceso, dia, ap, cr, etq)
WHERE r.id_acceso = v.acceso
ON CONFLICT (id_restaurante, dia_semana) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 11. Rango de precio en tabla (además de la columna restaurante; idempotente)
-- -----------------------------------------------------------------------------

INSERT INTO public.rango_precio_restaurante (id_restaurante, nivel, es_principal, notas)
SELECT r.id, '$'::rango_precios_enum, FALSE, 'Opción accesible (seed demo)'
FROM public.restaurante r
WHERE r.id_acceso = 'acc-bog-001'
ON CONFLICT (id_restaurante, nivel) DO NOTHING;

INSERT INTO public.rango_precio_restaurante (id_restaurante, nivel, es_principal, notas)
SELECT r.id, '$$$'::rango_precios_enum, FALSE, 'Experiencia premium (seed demo)'
FROM public.restaurante r
WHERE r.id_acceso = 'acc-med-002'
ON CONFLICT (id_restaurante, nivel) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 12. Calificaciones (public.calificacion) — historial demo
-- -----------------------------------------------------------------------------

INSERT INTO public.calificacion (id_restaurante, puntuacion, comentario, id_cliente, origen)
SELECT r.id, 4.5, 'Muy buena comida y ambiente familiar.', c.id, 'seed'
FROM public.restaurante r
CROSS JOIN public.cliente c
WHERE r.id_acceso = 'acc-bog-001' AND c.correo = 'ana.garcia@example.com'
  AND NOT EXISTS (
    SELECT 1 FROM public.calificacion x
    WHERE x.id_restaurante = r.id AND x.origen = 'seed'
      AND x.comentario = 'Muy buena comida y ambiente familiar.'
  );

INSERT INTO public.calificacion (id_restaurante, puntuacion, comentario, id_cliente, origen)
SELECT r.id, 5.0, 'El sushi impecable.', c.id, 'seed'
FROM public.restaurante r
CROSS JOIN public.cliente c
WHERE r.id_acceso = 'acc-med-002' AND c.correo = 'luis.martinez@example.com'
  AND NOT EXISTS (
    SELECT 1 FROM public.calificacion x
    WHERE x.id_restaurante = r.id AND x.origen = 'seed'
      AND x.comentario = 'El sushi impecable.'
  );

INSERT INTO public.calificacion (id_restaurante, puntuacion, comentario, id_cliente, origen)
SELECT r.id, 4.0, NULL, c.id, 'seed'
FROM public.restaurante r
CROSS JOIN public.cliente c
WHERE r.id_acceso = 'acc-cal-003' AND c.correo = 'maria.lopez@example.com'
  AND NOT EXISTS (
    SELECT 1 FROM public.calificacion x
    WHERE x.id_restaurante = r.id AND x.origen = 'seed'
      AND x.id_cliente = c.id AND x.puntuacion = 4.0
  );

-- -----------------------------------------------------------------------------
-- 13. Menú y categorías por pedido (public.menu / public.categoria_menu)
-- -----------------------------------------------------------------------------

INSERT INTO public.menu (id_pedido, nombre, descripcion, orden, activo)
SELECT p.id, 'Experiencia degustación', 'Platos del chef para la mesa Bogotá', 1, TRUE
FROM public.pedido p
JOIN public.reserva rv ON rv.id = p.id_reserva
WHERE rv.codigo_reserva = 'RES-BYT-001' AND p.descripcion = 'Menú degustación'
  AND NOT EXISTS (
    SELECT 1 FROM public.menu m WHERE m.id_pedido = p.id AND m.nombre = 'Experiencia degustación'
  );

INSERT INTO public.categoria_menu (id_menu, nombre, descripcion, orden)
SELECT m.id, 'Entradas', 'Para compartir', 1
FROM public.menu m
JOIN public.pedido p ON p.id = m.id_pedido
JOIN public.reserva rv ON rv.id = p.id_reserva
WHERE rv.codigo_reserva = 'RES-BYT-001' AND m.nombre = 'Experiencia degustación'
  AND NOT EXISTS (
    SELECT 1 FROM public.categoria_menu cm
    WHERE cm.id_menu = m.id AND cm.nombre = 'Entradas'
  );

INSERT INTO public.categoria_menu (id_menu, nombre, descripcion, orden)
SELECT m.id, 'Fuertes', 'Plato principal', 2
FROM public.menu m
JOIN public.pedido p ON p.id = m.id_pedido
JOIN public.reserva rv ON rv.id = p.id_reserva
WHERE rv.codigo_reserva = 'RES-BYT-001' AND m.nombre = 'Experiencia degustación'
  AND NOT EXISTS (
    SELECT 1 FROM public.categoria_menu cm
    WHERE cm.id_menu = m.id AND cm.nombre = 'Fuertes'
  );

INSERT INTO public.menu (id_pedido, nombre, descripcion, orden, activo)
SELECT p.id, 'Postres', 'Cierre dulce', 1, TRUE
FROM public.pedido p
JOIN public.reserva rv ON rv.id = p.id_reserva
WHERE rv.codigo_reserva = 'RES-BYT-001' AND p.descripcion = 'Postre del día'
  AND NOT EXISTS (
    SELECT 1 FROM public.menu m WHERE m.id_pedido = p.id AND m.nombre = 'Postres'
  );

INSERT INTO public.categoria_menu (id_menu, nombre, descripcion, orden)
SELECT m.id, 'Dulces', 'Postres de la casa', 1
FROM public.menu m
JOIN public.pedido p ON p.id = m.id_pedido
JOIN public.reserva rv ON rv.id = p.id_reserva
WHERE rv.codigo_reserva = 'RES-BYT-001' AND m.nombre = 'Postres'
  AND NOT EXISTS (
    SELECT 1 FROM public.categoria_menu cm
    WHERE cm.id_menu = m.id AND cm.nombre = 'Dulces'
  );

INSERT INTO public.menu (id_pedido, nombre, descripcion, orden, activo)
SELECT p.id, 'Menú omakase', 'Selección chef Medellín', 1, TRUE
FROM public.pedido p
JOIN public.reserva rv ON rv.id = p.id_reserva
WHERE rv.codigo_reserva = 'RES-BYT-002' AND p.descripcion = 'Chef omakase'
  AND NOT EXISTS (
    SELECT 1 FROM public.menu m WHERE m.id_pedido = p.id AND m.nombre = 'Menú omakase'
  );

INSERT INTO public.categoria_menu (id_menu, nombre, descripcion, orden)
SELECT m.id, 'Nigiri', 'Pescados del día', 1
FROM public.menu m
JOIN public.pedido p ON p.id = m.id_pedido
JOIN public.reserva rv ON rv.id = p.id_reserva
WHERE rv.codigo_reserva = 'RES-BYT-002' AND m.nombre = 'Menú omakase'
  AND NOT EXISTS (
    SELECT 1 FROM public.categoria_menu cm
    WHERE cm.id_menu = m.id AND cm.nombre = 'Nigiri'
  );

COMMIT;

-- =============================================================================
-- Notas
-- -----------------------------------------------------------------------------
-- - Ubicaciones: se evitan duplicados con WHERE NOT EXISTS por ciudad+barrio.
-- - Tras aplicar scripts/migration_geografia_horarios_menu.sql, esta semilla
--   también rellena horarios, rangos tabla, calificaciones, menú/categorías.
-- - Para vaciar todo y volver a sembrar (¡borra datos! orden FK):
--   TRUNCATE public.categoria_menu, public.menu, public.calificacion,
--     public.horarios, public.rango_precio_restaurante, public.pago,
--     public.pedido, public.reserva, public.usuario, public.cliente,
--     public.super_usuario, public.restaurante,
--     public.ubicacion, public.categorias, public.etiquetas, public.rol
--   RESTART IDENTITY CASCADE;
-- =============================================================================

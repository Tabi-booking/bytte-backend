-- =============================================================================
-- BYTTE – Migración PostgreSQL (Supabase compatible)
-- Objetivo:
--   1) horarios por restaurante
--   2) rango de precios por restaurante (tabla; no reemplaza aún la columna enum)
--   3) poblar categorías y etiquetas (ampliadas)
--   4) departamento → ciudad → vincula ubicacion.id_ciudad
--   5) calificaciones por restaurante (historial / filas individuales)
--   6) menu → pedido, categoria_menu → menu
--
-- Ejecutar en SQL Editor de Supabase o psql tras backup.
-- Requiere FKs válidas en public.restaurante(id), public.pedido(id).
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- 0) Extensions útiles (opcional; ignora si no tienes permisos)
-- ---------------------------------------------------------------------------
-- CREATE EXTENSION IF NOT EXISTS unaccent;

-- Enum de rango de precios (si ya existe, no hace nada).
-- Importante: el cuerpo NO puede usar delimitador $$ porque choca con valores '$$' del ENUM.
DO $migrate$
BEGIN
  CREATE TYPE public.rango_precios_enum AS ENUM ('$', '$$', '$$$', '$$$$');
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $migrate$;

-- ---------------------------------------------------------------------------
-- 1) Tabla horarios (ligada a restaurante)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.horarios (
  id               BIGSERIAL PRIMARY KEY,
  id_restaurante   BIGINT NOT NULL
    REFERENCES public.restaurante (id) ON UPDATE CASCADE ON DELETE CASCADE,
  dia_semana       SMALLINT NOT NULL CHECK (dia_semana BETWEEN 0 AND 6),
  hora_apertura    TIME NOT NULL,
  hora_cierre      TIME NOT NULL,
  etiqueta_dia     TEXT,
  activo           BOOLEAN NOT NULL DEFAULT TRUE,
  creado_en        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (id_restaurante, dia_semana)
);

COMMENT ON TABLE public.horarios IS 'Franjas por día para el restaurante. dia_semana: 0=domingo … 6=sábado (convención ISO simple).';
CREATE INDEX IF NOT EXISTS idx_horarios_restaurante ON public.horarios (id_restaurante);

-- ---------------------------------------------------------------------------
-- 2) Tabla rango de precios por restaurante
--    (coexiste con restaurante.rango_precios enum hasta que migres la app)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.rango_precio_restaurante (
  id               BIGSERIAL PRIMARY KEY,
  id_restaurante   BIGINT NOT NULL
    REFERENCES public.restaurante (id) ON UPDATE CASCADE ON DELETE CASCADE,
  nivel            public.rango_precios_enum NOT NULL,
  es_principal     BOOLEAN NOT NULL DEFAULT TRUE,
  notas            TEXT,
  creado_en        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (id_restaurante, nivel)
);

COMMENT ON TABLE public.rango_precio_restaurante IS 'Niveles de precio asociados al restaurante (puede haber varios; marca es_principal).';
CREATE INDEX IF NOT EXISTS idx_rango_precio_rest ON public.rango_precio_restaurante (id_restaurante);

-- Espejo del rango actual en columna restaurante.rango_precios (si existe)
INSERT INTO public.rango_precio_restaurante (id_restaurante, nivel, es_principal)
SELECT r.id, r.rango_precios, TRUE
FROM public.restaurante r
WHERE r.rango_precios IS NOT NULL
ON CONFLICT (id_restaurante, nivel) DO NOTHING;

-- ---------------------------------------------------------------------------
-- 3) Poblar categorías y etiquetas (ampliado)
-- ---------------------------------------------------------------------------
INSERT INTO public.categorias (nombre) VALUES
  ('Fusión'),
  ('Asiática'),
  ('Mediterránea'),
  ('Carnes / parrilla'),
  ('Mariscos'),
  ('Comida rápida'),
  ('Café / brunch'),
  ('Bar / coctelería'),
  ('Repostería'),
  ('Saludable / Bowl')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO public.etiquetas (nombre, svg) VALUES
  ('Vegano', NULL),
  ('Sin gluten', NULL),
  ('Barra libre', NULL),
  ('Música en vivo', NULL),
  ('Delivery', NULL),
  ('Para llevar', NULL),
  ('Estacionamiento', NULL),
  ('Acceso discapacidad', NULL),
  ('Wi‑Fi gratuito', NULL),
  ('Aire acondicionado', NULL),
  ('Vista panorámica', NULL),
  ('Zona infantil', NULL),
  ('Mascotas exterior', NULL)
ON CONFLICT (nombre) DO NOTHING;

-- ---------------------------------------------------------------------------
-- 4) Departamento, ciudad y vínculo con ubicacion
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.departamento (
  id          BIGSERIAL PRIMARY KEY,
  nombre      TEXT NOT NULL UNIQUE,
  codigo_iso  VARCHAR(16),
  activo      BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS public.ciudad (
  id               BIGSERIAL PRIMARY KEY,
  id_departamento  BIGINT NOT NULL
    REFERENCES public.departamento (id) ON UPDATE CASCADE ON DELETE RESTRICT,
  nombre           TEXT NOT NULL,
  UNIQUE (id_departamento, nombre)
);

CREATE INDEX IF NOT EXISTS idx_ciudad_depto ON public.ciudad (id_departamento);

-- Columna nueva en ubicacion (mantén dept/ciudad texto legacy para compat)
ALTER TABLE public.ubicacion
  ADD COLUMN IF NOT EXISTS id_ciudad BIGINT REFERENCES public.ciudad (id)
    ON UPDATE CASCADE ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_ubicacion_ciudad ON public.ubicacion (id_ciudad);

-- Poblar Colombia: departamentos (idempotente)
INSERT INTO public.departamento (nombre, codigo_iso)
SELECT v.nombre, v.codigo_iso
FROM (VALUES
  ('Amazonas', 'AM'),
  ('Antioquia', 'ANT'),
  ('Arauca', 'ARA'),
  ('Atlántico', 'ATL'),
  ('Bolívar', 'BOL'),
  ('Boyacá', 'BOY'),
  ('Caldas', 'CAL'),
  ('Caquetá', 'CAQ'),
  ('Casanare', 'CAS'),
  ('Cauca', 'CAU'),
  ('Cesar', 'CES'),
  ('Chocó', 'CHO'),
  ('Córdoba', 'COR'),
  ('Cundinamarca', 'CUN'),
  ('Guainía', 'GUA'),
  ('Guaviare', 'GUV'),
  ('Huila', 'HUI'),
  ('La Guajira', 'LAG'),
  ('Magdalena', 'MAG'),
  ('Meta', 'MET'),
  ('Nariño', 'NAR'),
  ('Norte de Santander', 'NSA'),
  ('Putumayo', 'PUT'),
  ('Quindío', 'QUI'),
  ('Risaralda', 'RIS'),
  ('San Andrés y Providencia', 'SAP'),
  ('Santander', 'SAN'),
  ('Sucre', 'SUC'),
  ('Tolima', 'TOL'),
  ('Valle del Cauca', 'VAC'),
  ('Vaupés', 'VAU'),
  ('Vichada', 'VID'),
  ('Bogotá D.C.', 'DC')
) AS v(nombre, codigo_iso)
ON CONFLICT (nombre) DO UPDATE SET codigo_iso = EXCLUDED.codigo_iso;

-- Ciudades (capitales y núcleos relevantes; ampliable con CSV DANE)
INSERT INTO public.ciudad (id_departamento, nombre)
SELECT d.id, v.ciudad
FROM (VALUES
  ('Amazonas', 'Leticia'),
  ('Amazonas', 'Puerto Alegría'),
  ('Antioquia', 'Medellín'),
  ('Antioquia', 'Bello'),
  ('Antioquia', 'Envigado'),
  ('Antioquia', 'Itagüí'),
  ('Antioquia', 'Rionegro'),
  ('Arauca', 'Arauca'),
  ('Arauca', 'Saravena'),
  ('Atlántico', 'Barranquilla'),
  ('Atlántico', 'Soledad'),
  ('Atlántico', 'Malambo'),
  ('Bolívar', 'Cartagena'),
  ('Bolívar', 'Magangué'),
  ('Bolívar', 'Turbaco'),
  ('Boyacá', 'Tunja'),
  ('Boyacá', 'Duitama'),
  ('Boyacá', 'Sogamoso'),
  ('Boyacá', 'Chiquinquirá'),
  ('Caldas', 'Manizales'),
  ('Caldas', 'La Dorada'),
  ('Caldas', 'Riosucio'),
  ('Caquetá', 'Florencia'),
  ('Caquetá', 'San Vicente del Caguán'),
  ('Casanare', 'Yopal'),
  ('Casanare', 'Aguazul'),
  ('Cauca', 'Popayán'),
  ('Cauca', 'Santander de Quilichao'),
  ('Cesar', 'Valledupar'),
  ('Cesar', 'Aguachica'),
  ('Chocó', 'Quibdó'),
  ('Chocó', 'Istmina'),
  ('Córdoba', 'Montería'),
  ('Córdoba', 'Lorica'),
  ('Cundinamarca', 'Soacha'),
  ('Cundinamarca', 'Facatativá'),
  ('Cundinamarca', 'Zipaquirá'),
  ('Cundinamarca', 'Girardot'),
  ('Cundinamarca', 'Chía'),
  ('Guainía', 'Inírida'),
  ('Guaviare', 'San José del Guaviare'),
  ('Huila', 'Neiva'),
  ('Huila', 'Pitalito'),
  ('Huila', 'Garzón'),
  ('La Guajira', 'Riohacha'),
  ('La Guajira', 'Maicao'),
  ('Magdalena', 'Santa Marta'),
  ('Magdalena', 'Ciénaga'),
  ('Magdalena', 'Fundación'),
  ('Meta', 'Villavicencio'),
  ('Meta', 'Acacías'),
  ('Nariño', 'Pasto'),
  ('Nariño', 'Tumaco'),
  ('Nariño', 'Ipiales'),
  ('Norte de Santander', 'Cúcuta'),
  ('Norte de Santander', 'Ocaña'),
  ('Norte de Santander', 'Pamplona'),
  ('Putumayo', 'Mocoa'),
  ('Putumayo', 'Puerto Asís'),
  ('Quindío', 'Armenia'),
  ('Quindío', 'Calarcá'),
  ('Risaralda', 'Pereira'),
  ('Risaralda', 'Dosquebradas'),
  ('Risaralda', 'Santa Rosa de Cabal'),
  ('San Andrés y Providencia', 'San Andrés'),
  ('Santander', 'Bucaramanga'),
  ('Santander', 'Floridablanca'),
  ('Santander', 'Barrancabermeja'),
  ('Santander', 'Piedecuesta'),
  ('Sucre', 'Sincelejo'),
  ('Sucre', 'Corozal'),
  ('Tolima', 'Ibagué'),
  ('Tolima', 'Espinal'),
  ('Tolima', 'Melgar'),
  ('Valle del Cauca', 'Cali'),
  ('Valle del Cauca', 'Palmira'),
  ('Valle del Cauca', 'Buenaventura'),
  ('Valle del Cauca', 'Tuluá'),
  ('Valle del Cauca', 'Buga'),
  ('Vaupés', 'Mitú'),
  ('Vichada', 'Puerto Carreño'),
  ('Bogotá D.C.', 'Bogotá'),
  ('Bogotá D.C.', 'Usme'),
  ('Bogotá D.C.', 'Bosa'),
  ('Bogotá D.C.', 'Suba'),
  ('Bogotá D.C.', 'Chapinero')
) AS v(depto, ciudad)
JOIN public.departamento d ON d.nombre = v.depto
ON CONFLICT (id_departamento, nombre) DO NOTHING;

-- Sincronizar ubicaciones existentes (texto) → id_ciudad
UPDATE public.ubicacion u
SET id_ciudad = c.id
FROM public.ciudad c
JOIN public.departamento dep ON dep.id = c.id_departamento
WHERE u.id_ciudad IS NULL
  AND lower(trim(u.departamento)) = lower(trim(dep.nombre))
  AND lower(trim(u.ciudad)) = lower(trim(c.nombre));

-- Variante común: en seed "Bogotá" con depto Cundinamarca — mapeo explícito
UPDATE public.ubicacion u
SET id_ciudad = c.id
FROM public.ciudad c
JOIN public.departamento dep ON dep.id = c.id_departamento
WHERE u.id_ciudad IS NULL
  AND lower(trim(u.ciudad)) = 'bogotá'
  AND dep.nombre = 'Bogotá D.C.'
  AND c.nombre = 'Bogotá';

-- ---------------------------------------------------------------------------
-- 5) Calificaciones (tabla aparte, ligada a restaurante)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.calificacion (
  id               BIGSERIAL PRIMARY KEY,
  id_restaurante   BIGINT NOT NULL
    REFERENCES public.restaurante (id) ON UPDATE CASCADE ON DELETE CASCADE,
  puntuacion       NUMERIC(2,1) NOT NULL CHECK (puntuacion >= 0 AND puntuacion <= 5),
  comentario       TEXT,
  id_cliente       BIGINT REFERENCES public.cliente (id) ON UPDATE CASCADE ON DELETE SET NULL,
  origen           TEXT,
  creado_en        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_calificacion_rest ON public.calificacion (id_restaurante);
CREATE INDEX IF NOT EXISTS idx_calificacion_cliente ON public.calificacion (id_cliente);

-- Copia un snapshot desde la columna actual de restaurante (opcional, una fila por restaurante)
INSERT INTO public.calificacion (id_restaurante, puntuacion, comentario, origen)
SELECT r.id, r.calificacion::NUMERIC(2,1), NULL, 'migración columna restaurante.calificacion'
FROM public.restaurante r
WHERE r.calificacion IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM public.calificacion c
    WHERE c.id_restaurante = r.id AND c.origen = 'migración columna restaurante.calificacion'
  );

-- ---------------------------------------------------------------------------
-- 6) Menú por pedido y categoría de menú
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.menu (
  id            BIGSERIAL PRIMARY KEY,
  id_pedido     BIGINT NOT NULL
    REFERENCES public.pedido (id) ON UPDATE CASCADE ON DELETE CASCADE,
  nombre        TEXT NOT NULL,
  descripcion   TEXT,
  orden         SMALLINT NOT NULL DEFAULT 0,
  activo        BOOLEAN NOT NULL DEFAULT TRUE,
  creado_en     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_menu_pedido ON public.menu (id_pedido);

CREATE TABLE IF NOT EXISTS public.categoria_menu (
  id            BIGSERIAL PRIMARY KEY,
  id_menu       BIGINT NOT NULL
    REFERENCES public.menu (id) ON UPDATE CASCADE ON DELETE CASCADE,
  nombre        TEXT NOT NULL,
  descripcion   TEXT,
  orden         SMALLINT NOT NULL DEFAULT 0,
  creado_en     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_categoria_menu ON public.categoria_menu (id_menu);

COMMIT;

-- =============================================================================
-- Notas posteriores (manual / siguiente iteración API)
-- =============================================================================
-- 1. Puedes poblar horarios desde el texto legacy restaurante.horarios en la app.
-- 2. Puedes espejar restaurante.rango_precios → rango_precio_restaurante tras migrar código.
-- 3. ciudad "Girardot" puede aparecer en Tolima/Cundinamarca según límites; ajustar si aplica.
-- 4. Para listado oficial completo DANE usar import CSV a public.ciudad.
-- =============================================================================

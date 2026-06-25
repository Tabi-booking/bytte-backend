"""Triggers: sincronizar restaurante.calificacion (promedio) y restaurante.rango_precios desde tablas hijas."""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

revision: str = "tr_sync_01"
down_revision: Union[str, None] = "baseline001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_UP_SQL = text(
    """
CREATE OR REPLACE FUNCTION public.sync_restaurante_calificacion_promedio()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $f$
DECLARE
  rid bigint := COALESCE(NEW.id_restaurante, OLD.id_restaurante);
  v_avg numeric;
BEGIN
  SELECT ROUND(AVG(puntuacion)::numeric, 1) INTO v_avg
  FROM public.calificacion
  WHERE id_restaurante = rid;

  UPDATE public.restaurante SET calificacion = v_avg WHERE id = rid;
  RETURN COALESCE(NEW, OLD);
END;
$f$;

DROP TRIGGER IF EXISTS trg_bytte_sync_rest_calificacion ON public.calificacion;
CREATE TRIGGER trg_bytte_sync_rest_calificacion
AFTER INSERT OR UPDATE OR DELETE ON public.calificacion
FOR EACH ROW EXECUTE PROCEDURE public.sync_restaurante_calificacion_promedio();

CREATE OR REPLACE FUNCTION public.sync_restaurante_rango_desde_tabla()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $f$
DECLARE
  rid bigint := COALESCE(NEW.id_restaurante, OLD.id_restaurante);
  v_nivel public.rango_precios_enum;
BEGIN
  SELECT rpr.nivel INTO v_nivel
  FROM public.rango_precio_restaurante rpr
  WHERE rpr.id_restaurante = rid AND rpr.es_principal = TRUE
  LIMIT 1;

  IF v_nivel IS NULL THEN
    SELECT rpr.nivel INTO v_nivel
    FROM public.rango_precio_restaurante rpr
    WHERE rpr.id_restaurante = rid
    ORDER BY rpr.nivel ASC
    LIMIT 1;
  END IF;

  IF v_nivel IS NOT NULL THEN
    UPDATE public.restaurante SET rango_precios = v_nivel WHERE id = rid;
  END IF;

  RETURN COALESCE(NEW, OLD);
END;
$f$;

DROP TRIGGER IF EXISTS trg_bytte_sync_rest_rango ON public.rango_precio_restaurante;
CREATE TRIGGER trg_bytte_sync_rest_rango
AFTER INSERT OR UPDATE OR DELETE ON public.rango_precio_restaurante
FOR EACH ROW EXECUTE PROCEDURE public.sync_restaurante_rango_desde_tabla();
"""
)

_BACKFILL_CAL = text(
    """
UPDATE public.restaurante r
SET calificacion = agg.v
FROM (
  SELECT id_restaurante AS rid, ROUND(AVG(puntuacion)::numeric, 1) AS v
  FROM public.calificacion
  GROUP BY id_restaurante
) agg
WHERE r.id = agg.rid AND agg.v IS NOT NULL;
"""
)

_BACKFILL_RANGO = text(
    """
UPDATE public.restaurante r
SET rango_precios = COALESCE(
  (SELECT nivel FROM public.rango_precio_restaurante x
   WHERE x.id_restaurante = r.id AND x.es_principal
   LIMIT 1),
  (SELECT nivel FROM public.rango_precio_restaurante x
   WHERE x.id_restaurante = r.id
   ORDER BY nivel ASC
   LIMIT 1)
)
WHERE EXISTS (
  SELECT 1 FROM public.rango_precio_restaurante x WHERE x.id_restaurante = r.id
);
"""
)

_DOWN_SQL = text(
    """
DROP TRIGGER IF EXISTS trg_bytte_sync_rest_calificacion ON public.calificacion;
DROP TRIGGER IF EXISTS trg_bytte_sync_rest_rango ON public.rango_precio_restaurante;

DROP FUNCTION IF EXISTS public.sync_restaurante_calificacion_promedio();
DROP FUNCTION IF EXISTS public.sync_restaurante_rango_desde_tabla();
"""
)


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(_UP_SQL)
    conn.execute(_BACKFILL_CAL)
    conn.execute(_BACKFILL_RANGO)


def downgrade() -> None:
    op.execute(_DOWN_SQL)

"""Perfil agregado restaurante (lectura SQL directa + PATCH por secciones)."""

from __future__ import annotations

import json
from typing import Any, List, Optional, Tuple

from Application.onboarding_mapping import (
    estado_bd_a_api,
    get_paso,
    merge_paso,
    onboarding_datos_to_json,
    parse_onboarding_datos,
)
from Application.storage_config import get_storage_settings
from Application.storage_urls import normalize_media_url
from Application.schemas_restaurant_profile import (
    ContactSection,
    CoverImage,
    DocumentItem,
    FeaturesSection,
    LocationSection,
    MediaSection,
    MetaSection,
    OnboardingSection,
    OperationsSection,
    OwnerContact,
    ProfileSection,
    RestaurantMePatch,
    RestaurantMeResponse,
    SubscriptionSection,
)
from Domain.ModeloHorario import Modelo_Horario
from Infraestructure.Database import get_db_connection
from Infraestructure.InfraestructuraCalificacion import Infraestructura_Calificacion
from Infraestructure.InfraestructuraHorarios import Infraestructura_Horarios
from Infraestructure.InfraestructuraRangoPrecioRestaurante import (
    Infraestructura_RangoPrecioRestaurante,
)
from Infraestructure.errors import NotFoundError


def _cell_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _cell_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class Infraestructura_RestaurantePerfil:
    def obtener_perfil_completo(self, id_restaurante: int) -> RestaurantMeResponse:
        db = get_db_connection()
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT
                  r.id,
                  r.id_acceso,
                  r.nombre,
                  r.razon_social,
                  r.descripcion,
                  r.sitio_web,
                  r.redes_sociales,
                  r.direccion,
                  r.telefono,
                  r.google_maps,
                  r.imagen_destacada,
                  r.horarios,
                  r.capacidad_asientos,
                  r.numero_mesas,
                  r.id_ubicacion,
                  r.onboarding_paso,
                  r.onboarding_estado,
                  r.onboarding_pct,
                  r.onboarding_datos,
                  r.onboarding_enviado_en,
                  COALESCE(r.activo, TRUE),
                  u.pais,
                  u.departamento,
                  u.ciudad,
                  u.barrio
                FROM public.restaurante r
                LEFT JOIN public.ubicacion u ON u.id = r.id_ubicacion
                WHERE r.id = %s
                """,
                (id_restaurante,),
            )
            row = cursor.fetchone()
            if not row:
                raise NotFoundError("Restaurante no encontrado")

            datos = parse_onboarding_datos(row[18])
            paso_1 = get_paso(datos, 1)
            paso_3 = get_paso(datos, 3)
            paso_5 = get_paso(datos, 5)

            profile = ProfileSection(
                nombre=_cell_str(row[2]),
                razon_social=_cell_str(row[3]),
                descripcion=_cell_str(row[4]),
                sitio_web=_cell_str(row[5]),
                redes_sociales=row[6] if isinstance(row[6], dict) else {},
                restaurant_type=paso_1.get("restaurant_type"),
            )

            location = LocationSection(
                id_ubicacion=_cell_str(row[14]) or None,
                pais=_cell_str(row[21]),
                departamento=_cell_str(row[22]),
                ciudad=_cell_str(row[23]),
                barrio=_cell_str(row[24]),
                direccion=_cell_str(row[7]),
                google_maps=_cell_str(row[9]),
            )

            owner = self._obtener_owner(cursor, id_restaurante, paso_3)
            contact = ContactSection(
                telefono=_cell_str(row[8]),
                owner=owner,
            )

            horarios = Infraestructura_Horarios().listar_por_restaurante(id_restaurante)
            operations = OperationsSection(
                horarios_resumen=_cell_str(row[11]),
                capacidad_asientos=_cell_int(row[12]),
                numero_mesas=_cell_int(row[13]),
                horarios=horarios,
            )

            cuisine, services, reservations = self._listar_features(
                cursor, id_restaurante, paso_5
            )
            features = FeaturesSection(
                cuisine_types=cuisine,
                services_offered=services,
                reservation_types=reservations,
            )

            storage = get_storage_settings()
            logo_raw = _cell_str(row[10])
            paso_6 = get_paso(datos, 6)
            logo_key = _cell_str(paso_6.get("logo_key") or "")
            media = MediaSection(
                logo_url=normalize_media_url(logo_raw, logo_key, storage),
                covers=self._listar_covers(cursor, id_restaurante, storage),
                documents=self._listar_documentos(cursor, id_restaurante, storage),
            )

            subscription = self._obtener_suscripcion(cursor, id_restaurante)
            onboarding = OnboardingSection(
                paso=_cell_int(row[15]),
                estado=estado_bd_a_api(_cell_str(row[16]) or None),
                pct=_cell_int(row[17]),
                enviado_en=row[19],
            )

            promo, cnt = Infraestructura_Calificacion().promedio_y_cantidad(id_restaurante)
            rangos = Infraestructura_RangoPrecioRestaurante().listar_por_restaurante(
                id_restaurante
            )
            meta = MetaSection(
                calificacion_promedio=promo,
                calificacion_cantidad=cnt,
                rangos_precio=rangos,
                activo=bool(row[20]),
                id_acceso=_cell_str(row[1]),
            )

            cursor.close()
            return RestaurantMeResponse(
                id=_cell_str(row[0]),
                profile=profile,
                location=location,
                contact=contact,
                operations=operations,
                features=features,
                media=media,
                subscription=subscription,
                onboarding=onboarding,
                meta=meta,
            )
        finally:
            db.close()

    def actualizar_perfil_parcial(
        self, id_restaurante: int, patch: RestaurantMePatch
    ) -> RestaurantMeResponse:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                "SELECT onboarding_datos FROM public.restaurante WHERE id = %s",
                (id_restaurante,),
            )
            row = cursor.fetchone()
            if not row:
                raise NotFoundError("Restaurante no encontrado")
            datos = parse_onboarding_datos(row[0])

            if patch.profile is not None:
                datos = self._patch_profile(cursor, id_restaurante, datos, patch.profile)
            if patch.location is not None:
                datos = self._patch_location(cursor, id_restaurante, datos, patch.location)
            if patch.contact is not None:
                self._patch_contact(cursor, id_restaurante, patch.contact)
            if patch.operations is not None:
                self._patch_operations(cursor, id_restaurante, patch.operations)
            if patch.features is not None:
                datos = self._patch_features(cursor, id_restaurante, datos, patch.features)

            db.commit()
            cursor.close()
        except NotFoundError:
            if db is not None:
                db.rollback()
            raise
        except Exception:
            if db is not None:
                db.rollback()
            raise
        finally:
            if db is not None and not db.closed:
                db.close()

        return self.obtener_perfil_completo(id_restaurante)

    def _obtener_owner(
        self, cursor: Any, id_restaurante: int, paso_3: dict
    ) -> Optional[OwnerContact]:
        cursor.execute(
            """
            SELECT us.nombre, us.apellido, us.correo, us.telefono
            FROM public.usuario us
            JOIN public.rol ON rol.id = us.id_rol
            WHERE us.id_restaurante = %s
              AND COALESCE(us.activo, TRUE)
            ORDER BY CASE
              WHEN LOWER(rol.nombre) IN ('propietario', 'administrador', 'owner') THEN 0
              ELSE 1
            END, us.id
            LIMIT 1
            """,
            (id_restaurante,),
        )
        urow = cursor.fetchone()
        if urow:
            return OwnerContact(
                nombre=_cell_str(urow[0]),
                apellido=_cell_str(urow[1]),
                correo=_cell_str(urow[2]),
                telefono=_cell_str(urow[3]),
            )
        if paso_3:
            return OwnerContact(
                nombre=_cell_str(paso_3.get("owner_name", "")),
                apellido="",
                correo=_cell_str(paso_3.get("email", "")),
                telefono=_cell_str(paso_3.get("phone", "")),
            )
        return None

    def _listar_features(
        self, cursor: Any, id_restaurante: int, paso_5: dict
    ) -> Tuple[List[str], List[str], List[str]]:
        cuisine: List[str] = []
        services: List[str] = []
        reservations: List[str] = []

        try:
            cursor.execute(
                """
                SELECT c.nombre FROM public.restaurante_categoria rc
                JOIN public.categorias c ON c.id = rc.id_categoria
                WHERE rc.id_restaurante = %s
                ORDER BY c.nombre
                """,
                (id_restaurante,),
            )
            cuisine = [_cell_str(r[0]) for r in cursor.fetchall()]
        except Exception:
            pass

        try:
            cursor.execute(
                """
                SELECT e.nombre FROM public.restaurante_etiqueta re
                JOIN public.etiquetas e ON e.id = re.id_etiqueta
                WHERE re.id_restaurante = %s
                ORDER BY e.nombre
                """,
                (id_restaurante,),
            )
            services = [_cell_str(r[0]) for r in cursor.fetchall()]
        except Exception:
            pass

        try:
            cursor.execute(
                """
                SELECT tipo FROM public.restaurante_tipo_reserva
                WHERE id_restaurante = %s
                ORDER BY tipo
                """,
                (id_restaurante,),
            )
            reservations = [_cell_str(r[0]) for r in cursor.fetchall()]
        except Exception:
            pass

        if not cuisine and paso_5.get("cuisine_types"):
            cuisine = list(paso_5.get("cuisine_types") or [])
        if not services and paso_5.get("services_offered"):
            services = list(paso_5.get("services_offered") or [])
        if not reservations and paso_5.get("reservation_types"):
            reservations = list(paso_5.get("reservation_types") or [])

        return cuisine, services, reservations

    def _listar_covers(
        self, cursor: Any, id_restaurante: int, storage: Any = None
    ) -> List[CoverImage]:
        try:
            cursor.execute(
                """
                SELECT id, COALESCE(url, ''), COALESCE(storage_key, ''), COALESCE(orden, 0)
                FROM public.restaurante_imagen
                WHERE id_restaurante = %s
                ORDER BY orden, id
                """,
                (id_restaurante,),
            )
            return [
                CoverImage(
                    id=_cell_str(r[0]),
                    url=normalize_media_url(_cell_str(r[1]), _cell_str(r[2]), storage),
                    storage_key=_cell_str(r[2]),
                    orden=int(r[3] or 0),
                )
                for r in cursor.fetchall()
            ]
        except Exception:
            return []

    def _listar_documentos(
        self, cursor: Any, id_restaurante: int, storage: Any = None
    ) -> List[DocumentItem]:
        try:
            cursor.execute(
                """
                SELECT id, COALESCE(tipo, ''), COALESCE(url, ''),
                       COALESCE(nombre_archivo, ''), COALESCE(storage_key, ''),
                       COALESCE(mime_type, ''), tamano_bytes, creado_en
                FROM public.documento_restaurante
                WHERE id_restaurante = %s
                ORDER BY creado_en DESC NULLS LAST, id
                """,
                (id_restaurante,),
            )
            return [
                DocumentItem(
                    id=_cell_str(r[0]),
                    tipo=_cell_str(r[1]),
                    url=normalize_media_url(_cell_str(r[2]), _cell_str(r[4]), storage),
                    nombre_archivo=_cell_str(r[3]),
                    storage_key=_cell_str(r[4]),
                    mime_type=_cell_str(r[5]),
                    tamano_bytes=r[6],
                    creado_en=r[7],
                )
                for r in cursor.fetchall()
            ]
        except Exception:
            return []

    def _obtener_suscripcion(
        self, cursor: Any, id_restaurante: int
    ) -> Optional[SubscriptionSection]:
        try:
            cursor.execute(
                """
                SELECT plan, ciclo_facturacion, estado, inicio_en, expira_en
                FROM public.suscripcion_restaurante
                WHERE id_restaurante = %s
                ORDER BY inicio_en DESC NULLS LAST, id DESC
                LIMIT 1
                """,
                (id_restaurante,),
            )
            srow = cursor.fetchone()
            if not srow:
                return None
            return SubscriptionSection(
                plan=_cell_str(srow[0]) or None,
                ciclo_facturacion=_cell_str(srow[1]) or None,
                estado=_cell_str(srow[2]) or None,
                inicio_en=srow[3],
                expira_en=srow[4],
            )
        except Exception:
            return None

    def _patch_profile(self, cursor: Any, rid: int, datos: dict, p: Any) -> dict:
        paso_1_patch: dict = {}
        if p.restaurant_type is not None:
            paso_1_patch["restaurant_type"] = p.restaurant_type
        if p.nombre is not None:
            paso_1_patch["restaurant_name"] = p.nombre
        if p.razon_social is not None:
            paso_1_patch["legal_name"] = p.razon_social
        if p.descripcion is not None:
            paso_1_patch["description"] = p.descripcion
        if p.sitio_web is not None:
            paso_1_patch["website"] = p.sitio_web
        if p.redes_sociales is not None:
            paso_1_patch["social_links"] = p.redes_sociales
        if paso_1_patch:
            datos = merge_paso(datos, 1, paso_1_patch)

        sets: List[str] = []
        args: List[Any] = []
        if p.nombre is not None:
            sets.append("nombre = %s")
            args.append(p.nombre.strip())
        if p.razon_social is not None:
            sets.append("razon_social = %s")
            args.append(p.razon_social.strip())
        if p.descripcion is not None:
            sets.append("descripcion = %s")
            args.append(p.descripcion.strip())
        if p.sitio_web is not None:
            sets.append("sitio_web = %s")
            args.append(p.sitio_web.strip())
        if p.redes_sociales is not None:
            sets.append("redes_sociales = %s::jsonb")
            args.append(json.dumps(p.redes_sociales, ensure_ascii=False))
        sets.append("onboarding_datos = %s::jsonb")
        args.append(onboarding_datos_to_json(datos))
        args.append(rid)
        cursor.execute(
            f"UPDATE public.restaurante SET {', '.join(sets)} WHERE id = %s",
            tuple(args),
        )
        return datos

    def _patch_location(self, cursor: Any, rid: int, datos: dict, loc: Any) -> dict:
        paso_2_patch: dict = {}
        for api_key, val in (
            ("country", loc.pais),
            ("department", loc.departamento),
            ("city", loc.ciudad),
            ("address", loc.barrio),
        ):
            if val is not None:
                paso_2_patch[api_key] = val
        if loc.direccion is not None:
            paso_2_patch["address"] = loc.direccion
        if loc.google_maps is not None:
            paso_2_patch["google_maps"] = loc.google_maps
        if paso_2_patch:
            datos = merge_paso(datos, 2, paso_2_patch)

        cursor.execute(
            "SELECT id_ubicacion FROM public.restaurante WHERE id = %s",
            (rid,),
        )
        urow = cursor.fetchone()
        ubic_id = urow[0] if urow else None

        pais = loc.pais if loc.pais is not None else ""
        depto = loc.departamento if loc.departamento is not None else ""
        ciudad = loc.ciudad if loc.ciudad is not None else ""
        barrio = loc.barrio if loc.barrio is not None else ""

        if ubic_id:
            cursor.execute(
                """
                UPDATE public.ubicacion
                SET pais = COALESCE(NULLIF(%s, ''), pais),
                    departamento = COALESCE(NULLIF(%s, ''), departamento),
                    ciudad = COALESCE(NULLIF(%s, ''), ciudad),
                    barrio = COALESCE(NULLIF(%s, ''), barrio)
                WHERE id = %s
                """,
                (pais, depto, ciudad, barrio, ubic_id),
            )
        elif any([pais, depto, ciudad, barrio]):
            cursor.execute(
                """
                INSERT INTO public.ubicacion (pais, departamento, ciudad, barrio)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (pais or "", depto or "", ciudad or "", barrio or ""),
            )
            new_u = cursor.fetchone()
            if new_u:
                ubic_id = new_u[0]
                cursor.execute(
                    "UPDATE public.restaurante SET id_ubicacion = %s WHERE id = %s",
                    (ubic_id, rid),
                )

        rest_sets: List[str] = ["onboarding_datos = %s::jsonb"]
        rest_args: List[Any] = [onboarding_datos_to_json(datos)]
        if loc.direccion is not None:
            rest_sets.append("direccion = %s")
            rest_args.append(loc.direccion.strip())
        if loc.google_maps is not None:
            rest_sets.append("google_maps = %s")
            rest_args.append(loc.google_maps.strip())
        rest_args.append(rid)
        cursor.execute(
            f"UPDATE public.restaurante SET {', '.join(rest_sets)} WHERE id = %s",
            tuple(rest_args),
        )
        return datos

    def _patch_contact(self, cursor: Any, rid: int, c: Any) -> None:
        if c.telefono is None:
            return
        cursor.execute(
            "UPDATE public.restaurante SET telefono = %s WHERE id = %s",
            (c.telefono.strip(), rid),
        )

    def _patch_operations(self, cursor: Any, rid: int, op: Any) -> None:
        sets: List[str] = []
        args: List[Any] = []
        if op.capacidad_asientos is not None:
            sets.append("capacidad_asientos = %s")
            args.append(op.capacidad_asientos)
        if op.numero_mesas is not None:
            sets.append("numero_mesas = %s")
            args.append(op.numero_mesas)
        if op.horarios_resumen is not None:
            sets.append("horarios = %s")
            args.append(op.horarios_resumen.strip())

        if op.horarios is not None:
            infra_h = Infraestructura_Horarios()
            for h in op.horarios:
                h = h.model_copy(update={"ID_Restaurante": str(rid)})
                infra_h.upsert_horario(h)
        elif op.opening_hours is not None and op.closing_hours is not None:
            cursor.execute(
                "DELETE FROM public.horarios WHERE id_restaurante = %s",
                (rid,),
            )
            resumen = (
                f"{op.opening_hours.strftime('%H:%M')}-{op.closing_hours.strftime('%H:%M')}"
            )
            sets.append("horarios = %s")
            args.append(
                op.horarios_resumen.strip()
                if op.horarios_resumen
                else resumen
            )
            for dia in range(7):
                cursor.execute(
                    """
                    INSERT INTO public.horarios (
                        id_restaurante, dia_semana, hora_apertura, hora_cierre, activo
                    ) VALUES (%s, %s, %s, %s, TRUE)
                    """,
                    (rid, dia, op.opening_hours, op.closing_hours),
                )

        if sets:
            args.append(rid)
            cursor.execute(
                f"UPDATE public.restaurante SET {', '.join(sets)} WHERE id = %s",
                tuple(args),
            )

    def _patch_features(self, cursor: Any, rid: int, datos: dict, f: Any) -> dict:
        paso_5_patch: dict = {}
        if f.cuisine_types is not None:
            paso_5_patch["cuisine_types"] = f.cuisine_types
        if f.services_offered is not None:
            paso_5_patch["services_offered"] = f.services_offered
        if f.reservation_types is not None:
            paso_5_patch["reservation_types"] = f.reservation_types
        if paso_5_patch:
            datos = merge_paso(datos, 5, paso_5_patch)

        if f.cuisine_types is not None:
            self._replace_m2m_categorias(cursor, rid, f.cuisine_types)
        if f.services_offered is not None:
            self._replace_m2m_etiquetas(cursor, rid, f.services_offered)
        if f.reservation_types is not None:
            self._replace_tipos_reserva(cursor, rid, f.reservation_types)

        cursor.execute(
            "UPDATE public.restaurante SET onboarding_datos = %s::jsonb WHERE id = %s",
            (onboarding_datos_to_json(datos), rid),
        )
        return datos

    def _get_or_create_categoria(self, cursor: Any, nombre: str) -> int:
        n = nombre.strip()
        cursor.execute(
            "SELECT id FROM public.categorias WHERE LOWER(nombre) = LOWER(%s) LIMIT 1",
            (n,),
        )
        row = cursor.fetchone()
        if row:
            return int(row[0])
        cursor.execute(
            "INSERT INTO public.categorias (nombre) VALUES (%s) RETURNING id",
            (n,),
        )
        ins = cursor.fetchone()
        return int(ins[0])

    def _get_or_create_etiqueta(self, cursor: Any, nombre: str) -> int:
        n = nombre.strip()
        cursor.execute(
            "SELECT id FROM public.etiquetas WHERE LOWER(nombre) = LOWER(%s) LIMIT 1",
            (n,),
        )
        row = cursor.fetchone()
        if row:
            return int(row[0])
        cursor.execute(
            "INSERT INTO public.etiquetas (nombre, svg) VALUES (%s, NULL) RETURNING id",
            (n,),
        )
        ins = cursor.fetchone()
        return int(ins[0])

    def _replace_m2m_categorias(
        self, cursor: Any, rid: int, nombres: List[str]
    ) -> None:
        try:
            cursor.execute(
                "DELETE FROM public.restaurante_categoria WHERE id_restaurante = %s",
                (rid,),
            )
            for nombre in nombres:
                if not str(nombre).strip():
                    continue
                cid = self._get_or_create_categoria(cursor, str(nombre))
                cursor.execute(
                    """
                    INSERT INTO public.restaurante_categoria (id_restaurante, id_categoria)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (rid, cid),
                )
            if nombres:
                first = self._get_or_create_categoria(cursor, str(nombres[0]))
                cursor.execute(
                    "UPDATE public.restaurante SET id_categoria = %s WHERE id = %s",
                    (first, rid),
                )
        except Exception:
            pass

    def _replace_m2m_etiquetas(self, cursor: Any, rid: int, nombres: List[str]) -> None:
        try:
            cursor.execute(
                "DELETE FROM public.restaurante_etiqueta WHERE id_restaurante = %s",
                (rid,),
            )
            for nombre in nombres:
                if not str(nombre).strip():
                    continue
                eid = self._get_or_create_etiqueta(cursor, str(nombre))
                cursor.execute(
                    """
                    INSERT INTO public.restaurante_etiqueta (id_restaurante, id_etiqueta)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (rid, eid),
                )
            if nombres:
                first = self._get_or_create_etiqueta(cursor, str(nombres[0]))
                cursor.execute(
                    "UPDATE public.restaurante SET id_etiqueta = %s WHERE id = %s",
                    (first, rid),
                )
        except Exception:
            pass

    def _replace_tipos_reserva(
        self, cursor: Any, rid: int, tipos: List[str]
    ) -> None:
        try:
            cursor.execute(
                "DELETE FROM public.restaurante_tipo_reserva WHERE id_restaurante = %s",
                (rid,),
            )
            for tipo in tipos:
                t = str(tipo).strip().lower()
                if not t:
                    continue
                cursor.execute(
                    """
                    INSERT INTO public.restaurante_tipo_reserva (id_restaurante, tipo)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (rid, t),
                )
        except Exception:
            pass

    # --- Onboarding / pasos públicos ---

    def crear_restaurante_stub(self) -> int:
        import uuid

        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            id_acceso = f"onboarding-{uuid.uuid4().hex[:12]}"
            cursor.execute(
                """
                INSERT INTO public.restaurante (
                    id_acceso, nombre, activo,
                    onboarding_estado, onboarding_paso, onboarding_pct, onboarding_datos
                ) VALUES (%s, '', FALSE, 'borrador', 1, 0, '{}'::jsonb)
                RETURNING id
                """,
                (id_acceso,),
            )
            row = cursor.fetchone()
            db.commit()
            cursor.close()
            if not row:
                raise NotFoundError("No se pudo crear el restaurante")
            return int(row[0])
        except Exception:
            if db is not None:
                db.rollback()
            raise
        finally:
            if db is not None and not db.closed:
                db.close()

    def _load_datos(self, cursor: Any, rid: int) -> dict:
        cursor.execute(
            "SELECT onboarding_datos FROM public.restaurante WHERE id = %s",
            (rid,),
        )
        row = cursor.fetchone()
        if not row:
            raise NotFoundError("Restaurante no encontrado")
        return parse_onboarding_datos(row[0])

    def _update_onboarding_progress(self, cursor: Any, rid: int, step: int) -> None:
        pct = min(100, int(round((step / 7) * 100)))
        cursor.execute(
            """
            UPDATE public.restaurante
            SET onboarding_paso = GREATEST(COALESCE(onboarding_paso, 1), %s),
                onboarding_pct = %s
            WHERE id = %s
            """,
            (step, pct, rid),
        )

    def aplicar_paso_en_transaccion(self, rid: int, step: int, fn) -> None:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            fn(cursor, rid)
            self._update_onboarding_progress(cursor, rid, step)
            db.commit()
            cursor.close()
        except NotFoundError:
            if db is not None:
                db.rollback()
            raise
        except Exception:
            if db is not None:
                db.rollback()
            raise
        finally:
            if db is not None and not db.closed:
                db.close()

    def aplicar_paso_1(self, rid: int, body: Any) -> None:
        from Application.schemas_restaurant_profile import ProfilePatch

        patch = ProfilePatch(
            nombre=body.restaurant_name,
            razon_social=body.legal_name,
            descripcion=body.description,
            sitio_web=body.website,
            redes_sociales=body.social_links,
            restaurant_type=body.restaurant_type,
        )

        def _run(cursor: Any, restaurant_id: int) -> None:
            datos = self._load_datos(cursor, restaurant_id)
            datos = self._patch_profile(cursor, restaurant_id, datos, patch)
            if body.restaurant_type:
                cid = self._get_or_create_categoria(cursor, body.restaurant_type.strip())
                cursor.execute(
                    "UPDATE public.restaurante SET id_categoria = %s WHERE id = %s",
                    (cid, restaurant_id),
                )
            datos = merge_paso(
                datos,
                1,
                body.model_dump(exclude_none=True),
            )
            cursor.execute(
                "UPDATE public.restaurante SET onboarding_datos = %s::jsonb WHERE id = %s",
                (onboarding_datos_to_json(datos), restaurant_id),
            )

        self.aplicar_paso_en_transaccion(rid, 1, _run)

    def aplicar_paso_2(self, rid: int, body: Any) -> None:
        from Application.schemas_restaurant_profile import LocationPatch

        google_maps = body.google_maps
        if not google_maps and body.lat is not None and body.lng is not None:
            google_maps = f"https://maps.google.com/?q={body.lat},{body.lng}"

        patch = LocationPatch(
            pais=body.country,
            departamento=body.department,
            ciudad=body.city,
            barrio=body.address,
            direccion=body.address,
            google_maps=google_maps,
        )

        def _run(cursor: Any, restaurant_id: int) -> None:
            datos = self._load_datos(cursor, restaurant_id)
            paso_2 = body.model_dump(exclude_none=True)
            if google_maps and "google_maps" not in paso_2:
                paso_2["google_maps"] = google_maps
            datos = merge_paso(datos, 2, paso_2)
            self._patch_location(cursor, restaurant_id, datos, patch)

        self.aplicar_paso_en_transaccion(rid, 2, _run)

    def aplicar_paso_3(self, rid: int, body: Any) -> None:
        from Application.schemas_restaurant_profile import ContactPatch

        patch = ContactPatch(telefono=body.phone)

        def _run(cursor: Any, restaurant_id: int) -> None:
            datos = self._load_datos(cursor, restaurant_id)
            datos = merge_paso(datos, 3, body.model_dump(exclude_none=True))
            self._patch_contact(cursor, restaurant_id, patch)
            cursor.execute(
                "UPDATE public.restaurante SET onboarding_datos = %s::jsonb WHERE id = %s",
                (onboarding_datos_to_json(datos), restaurant_id),
            )

        self.aplicar_paso_en_transaccion(rid, 3, _run)

    def aplicar_paso_4(self, rid: int, body: Any) -> None:
        from Application.schemas_restaurant_profile import OperationsPatch

        patch = OperationsPatch(
            opening_hours=body.opening_hours,
            closing_hours=body.closing_hours,
            capacidad_asientos=body.seating_capacity,
            numero_mesas=body.number_tables,
        )

        def _run(cursor: Any, restaurant_id: int) -> None:
            datos = self._load_datos(cursor, restaurant_id)
            datos = merge_paso(datos, 4, body.model_dump(exclude_none=True))
            self._patch_operations(cursor, restaurant_id, patch)
            cursor.execute(
                "UPDATE public.restaurante SET onboarding_datos = %s::jsonb WHERE id = %s",
                (onboarding_datos_to_json(datos), restaurant_id),
            )

        self.aplicar_paso_en_transaccion(rid, 4, _run)

    def aplicar_paso_5(self, rid: int, body: Any) -> None:
        from Application.schemas_restaurant_profile import FeaturesPatch

        patch = FeaturesPatch(
            cuisine_types=body.cuisine_types,
            services_offered=body.services_offered,
            reservation_types=body.reservation_types,
        )

        def _run(cursor: Any, restaurant_id: int) -> None:
            datos = self._load_datos(cursor, restaurant_id)
            self._patch_features(cursor, restaurant_id, datos, patch)
            datos = merge_paso(datos, 5, body.model_dump(exclude_none=True))
            cursor.execute(
                "UPDATE public.restaurante SET onboarding_datos = %s::jsonb WHERE id = %s",
                (onboarding_datos_to_json(datos), restaurant_id),
            )

        self.aplicar_paso_en_transaccion(rid, 5, _run)

    def aplicar_paso_6(self, rid: int, body: Any) -> None:
        def _run(cursor: Any, restaurant_id: int) -> None:
            datos = self._load_datos(cursor, restaurant_id)
            datos = merge_paso(datos, 6, body.model_dump(exclude_none=True))
            cursor.execute(
                "UPDATE public.restaurante SET onboarding_datos = %s::jsonb WHERE id = %s",
                (onboarding_datos_to_json(datos), restaurant_id),
            )

        self.aplicar_paso_en_transaccion(rid, 6, _run)

    def aplicar_paso_7(self, rid: int, body: Any) -> None:
        def _run(cursor: Any, restaurant_id: int) -> None:
            datos = self._load_datos(cursor, restaurant_id)
            datos = merge_paso(datos, 7, body.model_dump(exclude_none=True))
            cursor.execute(
                "UPDATE public.restaurante SET onboarding_datos = %s::jsonb WHERE id = %s",
                (onboarding_datos_to_json(datos), restaurant_id),
            )
            try:
                cursor.execute(
                    """
                    INSERT INTO public.suscripcion_restaurante (
                        id_restaurante, plan, ciclo_facturacion, estado, inicio_en
                    ) VALUES (%s, %s, %s, 'trial', NOW())
                    ON CONFLICT (id_restaurante) DO UPDATE SET
                        plan = EXCLUDED.plan,
                        ciclo_facturacion = EXCLUDED.ciclo_facturacion,
                        estado = EXCLUDED.estado
                    """,
                    (restaurant_id, body.plan, body.billing_cycle),
                )
            except Exception:
                cursor.execute(
                    """
                    UPDATE public.suscripcion_restaurante
                    SET plan = %s, ciclo_facturacion = %s, estado = 'trial',
                        inicio_en = COALESCE(inicio_en, NOW())
                    WHERE id_restaurante = %s
                    """,
                    (body.plan, body.billing_cycle, restaurant_id),
                )
                if cursor.rowcount == 0:
                    cursor.execute(
                        """
                        INSERT INTO public.suscripcion_restaurante (
                            id_restaurante, plan, ciclo_facturacion, estado, inicio_en
                        ) VALUES (%s, %s, %s, 'trial', NOW())
                        """,
                        (restaurant_id, body.plan, body.billing_cycle),
                    )

        self.aplicar_paso_en_transaccion(rid, 7, _run)

    def obtener_estado_onboarding(self, rid: int) -> dict:
        db = get_db_connection()
        try:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT onboarding_paso, onboarding_estado, onboarding_pct, onboarding_enviado_en
                FROM public.restaurante WHERE id = %s
                """,
                (rid,),
            )
            row = cursor.fetchone()
            cursor.close()
            if not row:
                raise NotFoundError("Restaurante no encontrado")
            return {
                "restaurant_id": str(rid),
                "step": _cell_int(row[0]) or 1,
                "status": estado_bd_a_api(_cell_str(row[1]) or "borrador") or "draft",
                "pct": _cell_int(row[2]) or 0,
                "submitted_at": row[3],
            }
        finally:
            db.close()

    def submit_onboarding(self, rid: int) -> None:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                """
                UPDATE public.restaurante
                SET onboarding_estado = 'enviado',
                    activo = TRUE,
                    onboarding_enviado_en = NOW(),
                    onboarding_pct = 100,
                    onboarding_paso = 7
                WHERE id = %s
                RETURNING id
                """,
                (rid,),
            )
            if cursor.fetchone() is None:
                raise NotFoundError("Restaurante no encontrado")
            db.commit()
            cursor.close()
        except NotFoundError:
            if db is not None:
                db.rollback()
            raise
        except Exception:
            if db is not None:
                db.rollback()
            raise
        finally:
            if db is not None and not db.closed:
                db.close()

    def confirm_logo_upload(self, rid: int, public_url: str, storage_key: str) -> None:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                "UPDATE public.restaurante SET imagen_destacada = %s WHERE id = %s",
                (public_url, rid),
            )
            datos = self._load_datos(cursor, rid)
            datos = merge_paso(datos, 6, {"logo_key": storage_key})
            cursor.execute(
                "UPDATE public.restaurante SET onboarding_datos = %s::jsonb WHERE id = %s",
                (onboarding_datos_to_json(datos), rid),
            )
            db.commit()
            cursor.close()
        except Exception:
            if db is not None:
                db.rollback()
            raise
        finally:
            if db is not None and not db.closed:
                db.close()

    def confirm_cover_upload(
        self, rid: int, public_url: str, storage_key: str, orden: int = 0
    ) -> None:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                """
                INSERT INTO public.restaurante_imagen (id_restaurante, url, storage_key, orden)
                VALUES (%s, %s, %s, %s)
                """,
                (rid, public_url, storage_key, orden),
            )
            db.commit()
            cursor.close()
        except Exception:
            if db is not None:
                db.rollback()
            raise
        finally:
            if db is not None and not db.closed:
                db.close()

    def confirm_document_upload(
        self,
        rid: int,
        public_url: str,
        storage_key: str,
        filename: str,
        mime_type: str,
        size_bytes: Optional[int],
    ) -> None:
        db = None
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                """
                INSERT INTO public.documento_restaurante (
                    id_restaurante, tipo, url, nombre_archivo, storage_key,
                    mime_type, tamano_bytes
                ) VALUES (%s, 'business_doc', %s, %s, %s, %s, %s)
                """,
                (rid, public_url, filename, storage_key, mime_type, size_bytes),
            )
            db.commit()
            cursor.close()
        except Exception:
            if db is not None:
                db.rollback()
            raise
        finally:
            if db is not None and not db.closed:
                db.close()

    def restaurante_en_borrador(self, rid: int) -> bool:
        db = get_db_connection()
        try:
            cursor = db.cursor()
            cursor.execute(
                "SELECT onboarding_estado FROM public.restaurante WHERE id = %s",
                (rid,),
            )
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return False
            return str(row[0] or "").lower() == "borrador"
        finally:
            db.close()

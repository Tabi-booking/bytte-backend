# Guía front — geografía, horarios, rangos, calificaciones y menú por pedido

Complementa [`FRONTEND_AUTH.md`](FRONTEND_AUTH.md): autenticación, CORS y Bearer son los mismos. Estas rutas exigen **JWT** salvo que se indique lo contrario.

**Requisito de base de datos:** el proyecto debe tener aplicada la migración [`scripts/migration_geografia_horarios_menu.sql`](../scripts/migration_geografia_horarios_menu.sql) (tablas `departamento`, `ciudad`, `horarios`, `rango_precio_restaurante`, `calificacion`, `menu`, `categoria_menu` y columna `ubicacion.id_ciudad`). Los triggers que mantienen coherentes `restaurante.calificacion` y `restaurante.rango_precios` respecto a las tablas hijas están en la revisión Alembic `tr_sync_01` (véase [`README.md`](../README.md)).

---

## Convenciones

- **Prefijo API:** las rutas de negocio están bajo **`/api/v1`** (ej. `GET /api/v1/ConsultarHorarios`). **`GET /health`** vive en la raíz (sin prefijo) para balanceadores y monitoreo.
- **Cabecera:** `Authorization: Bearer <access_token>`.
- **Content-Type:** `application/json` en `POST` / `PUT`.
- **`kind: "user"` (empleado):** el backend toma `restaurant_id` del JWT; no hace falta enviar `id_restaurante` en query para lecturas propias del restaurante asignado.
- **`kind: "super"`:** en lecturas por restaurante debes pasar **`id_restaurante` como query string** donde se indica. En escrituras donde el modelo lleva `ID_Restaurante`, envía ese campo en el cuerpo.
- **`/docs`:** contratos y esquemas exactos (`http://localhost:8000/docs` en local).

### Panel empleado — restaurante agregado

| Método | Ruta | Notas |
|--------|------|--------|
| `GET` | `/api/v1/restaurantes/mi` | Solo `kind: user`. Devuelve restaurante, horarios, rangos de la tabla, promedio y conteo de calificaciones. |

### Listados paginados

Estos `GET` devuelven `{"items": [...], "total": n, "limit": L, "offset": O}` con query opcionales **`limit`** (máx. 100) y **`offset`**:

- `/api/v1/ConsultarReserva`
- `/api/v1/ConsultarPedido`
- `/api/v1/ConsultarCalificacionRestaurante`

---

## Ubicación: campo `ID_Ciudad`

`GET /api/v1/ConsultarUbicacion` y `GET /api/v1/ConsultarUbicacionId` devuelven, además de `Pais`, `Departamento`, `Ciudad`, `Barrio`, el campo opcional **`ID_Ciudad`** (string vacío si no está enlazado).

**Modificar ubicación:** en `PUT /api/v1/ModificarUbicacion` puedes incluir **`ID_Ciudad`** con el id del catálogo de ciudad (`ConsultarCiudadPorDepartamento`) para persistir la FK después de ejecutar la lógica SQL existente del restaurante.

---

## Geografía (catálogos lectura)

| Método | Ruta | Parámetros |
|--------|------|-------------|
| `GET` | `/api/v1/ConsultarDepartamentos` | Ninguno |
| `GET` | `/api/v1/ConsultarCiudadPorDepartamento` | Query **`ID_Departamento`** (string numérico) |

**Uso típico en formularios:** cargar departamentos → al elegir uno, cargar ciudades con ese `ID_Departamento` → opcionalmente enviar ciudad elegida como `ID_Ciudad` al guardar ubicación/restaurante.

---

## Horarios (`public.horarios`)

| Método | Ruta | Notas |
|--------|------|--------|
| `GET` | `/api/v1/ConsultarHorarios` | `user`: lista del restaurante del token. **`super`:** query `id_restaurante` obligatorio. |
| `POST` | `/api/v1/IngresarHorario` | Upsert por par `(id_restaurante, dia_semana)`. `user`: no necesita `ID_Restaurante` en body (lo fuerza el token). **`super`:** enviar `ID_Restaurante` en body. |
| `PUT` | `/api/v1/ModificarHorario/{ID_Key}` | `ID_Key` = id numérico de la fila. `user`: `ID_Restaurante` se toma del token. **`super`:** incluir `ID_Restaurante` en body. |
| `DELETE` | `/api/v1/EliminarHorario/{ID_Key}` | `user`: basta `{ID_Key}`. **`super`:** query **`id_restaurante`** obligatorio. |

### Cuerpo `Modelo_Horario` (POST / PUT)

| Campo | Tipo | Obligatoriedad |
|-------|------|----------------|
| `ID_Restaurante` | string | Obligatorio para **super** en POST / PUT según rutas descritas. |
| `Dia_semana` | número entero | **0** = domingo … **6** = sábado. |
| `Hora_apertura`, `Hora_cierre` | hora ISO (`"09:30:00"`) | Sí |
| `Etiqueta_dia` | string | Opcional |
| `Activo` | boolean | Default `true` |

Ejemplo POST:

```json
{
  "ID_Restaurante": "",
  "Dia_semana": 1,
  "Hora_apertura": "12:00:00",
  "Hora_cierre": "22:00:00",
  "Etiqueta_dia": "Almuerzo",
  "Activo": true
}
```

(En `user` puedes omitir `ID_Restaurante` o dejar vacío; el servidor lo sobrescribe.)

---

## Rango de precio por restaurante (`public.rango_precio_restaurante`)

Convive con la columna `restaurante.rango_precios`; esta API usa la **tabla** nueva. Tras aplicar triggers de migración, la columna del restaurante se actualiza al insertar/actualizar/borrar filas en `rango_precio_restaurante` (prioriza `es_principal`, si no hay, el menor nivel del enum).

| Método | Ruta | Notas |
|--------|------|--------|
| `GET` | `/api/v1/ConsultarRangoPrecioRestaurante` | `super`: query `id_restaurante`. |
| `POST` | `/api/v1/IngresarRangoPrecioRestaurante` | Upsert por `(id_restaurante, nivel)`. |
| `DELETE` | `/api/v1/EliminarRangoPrecioRestaurante/{ID_Key}` | `super`: query `id_restaurante`. |

### Cuerpo `Modelo_RangoPrecioRestaurante` (POST)

| Campo | Descripción |
|-------|--------------|
| `Nivel` | Uno de: `"$"`, `"$$"`, `"$$$"`, `"$$$$"` (texto igual al enum Postgres). |
| `Es_principal` | boolean |
| `Notas` | string opcional |

---

## Calificaciones (`public.calificacion`)

Tras los triggers de migración, `restaurante.calificacion` refleja el **promedio** de las filas de esta tabla por restaurante.

| Método | Ruta | Notas |
|--------|------|--------|
| `GET` | `/api/v1/ConsultarCalificacionRestaurante` | Respuesta paginada; `super`: query `id_restaurante`. |
| `POST` | `/api/v1/IngresarCalificacion` | `user`: solo puede publicar para **su** `restaurant_id` (si manda otro → 403). `super`: enviar `ID_Restaurante`. |

### Cuerpo `Modelo_Calificacion` (POST)

| Campo | Descripción |
|-------|--------------|
| `Puntuacion` | Número 0–5 (decimales permitidos). |
| `Comentario` | Opcional |
| `ID_Cliente` | Opcional (string numérico o vacío si no hay cliente). |
| `Origen` | Opcional |

---

## Menú y categoría de menú (ligados al pedido)

Validación tenant: solo el restaurante propietario de la **reserva** asociada al **pedido** puede listar/modificar estos recursos (`pedido → reserva → id_restaurante`).

### Menú

| Método | Ruta | Notas |
|--------|------|--------|
| `GET` | `/api/v1/ConsultarMenuPorPedido` | Query **`ID_Pedido`** |
| `POST` | `/api/v1/IngresarMenu` | Body con `ID_Pedido`, `Nombre`, etc. |
| `PUT` | `/api/v1/ModificarMenu/{ID_Key}` | |
| `DELETE` | `/api/v1/EliminarMenu/{ID_Key}` | |

### Categoría de menú

| Método | Ruta | Notas |
|--------|------|--------|
| `GET` | `/api/v1/ConsultarCategoriaMenuPorMenu` | Query **`ID_Menu`** |
| `POST` | `/api/v1/IngresarCategoriaMenu` | Body con `ID_Menu`, `Nombre`, etc. |
| `PUT` | `/api/v1/ModificarCategoriaMenu/{ID_Key}` | |
| `DELETE` | `/api/v1/EliminarCategoriaMenu/{ID_Key}` | |

### Cuerpo `Modelo_Menu` (referencia rápida)

- `ID_Pedido` (string)
- `Nombre`
- `Descripcion`, `Orden`, `Activo`

### Cuerpo `Modelo_CategoriaMenu` (referencia rápida)

- `ID_Menu` (string)
- `Nombre`
- `Descripcion`, `Orden`

---

## Errores habituales

| Código | Causa |
|--------|--------|
| **400** | Falta query `id_restaurante` siendo super en consultas tenant-scoped; validación Pydantic (`error_type: validation`); o fallo de persistencia traducido desde `resultado` en rutas nuevas de esta guía. |
| **403** | Recurso (pedido, menú, reserva) no pertenece al restaurante del JWT |
| **401** | Token ausente/expirado (ver [`FRONTEND_AUTH.md`](FRONTEND_AUTH.md)) |

Muchas infraestructuras antiguas devuelven **`200`** con `resultado` en el JSON que empieza por `"… Fallido:"` ante errores de BD; revisa ese campo donde aplique rutas legacy.

---

## Reserva de estado

Para cambiar solo el estado de una reserva sin enviar todo el recurso existe:

| Método | Ruta | Cuerpo |
|--------|------|--------|
| `PUT` | `/api/v1/Reserva/{ID_Key}/estado` | `{ "Estado": "CONFIRMADA" }` |

Valores reales según tu enum Postgres `estado_reserva_enum` (ej. `PENDIENTE`, `CONFIRMADA`, `CANCELADA` tras migraciones).

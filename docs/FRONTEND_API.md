# Referencia completa API — integración frontend

Documento único para consumir el backend Bytte desde el cliente web. Complementa [`FRONTEND_AUTH.md`](FRONTEND_AUTH.md) y [`FRONTEND_GEO_HORARIOS_MENU.md`](FRONTEND_GEO_HORARIOS_MENU.md).

---

## Convenciones generales

| Concepto | Valor |
|----------|--------|
| **Base URL (dev)** | `http://localhost:8000` |
| **Prefijo REST** | `/api/v1` |
| **Health check** | `GET /health` (sin prefijo, sin JWT) |
| **Swagger** | `{baseUrl}/docs` |
| **Content-Type** | `application/json` en `POST` / `PUT` |
| **Autenticación** | `Authorization: Bearer <access_token>` |

### Rutas públicas (sin JWT)

- `GET /health`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/registro/restaurante`
- `POST /api/v1/onboarding/start`

Rutas de onboarding/uploads **antes del login** aceptan el header **`X-Restaurant-Id`** (devuelto por `/onboarding/start`) en lugar de JWT.

### Roles (`kind` del login)

| Rol | Descripción |
|-----|-------------|
| **`user`** | Empleado de restaurante. Datos filtrados por `restaurant_id` del token. |
| **`super`** | Administrador de plataforma. Acceso global; en recursos tenant-scoped debe enviar `id_restaurante` (query) o `ID_Restaurante` (body). |

### Patrón legacy de IDs

Muchos `PUT` / `DELETE` antiguos reciben **`ID_Key` como query string** (no en la ruta), además del cuerpo JSON completo del recurso.

Ejemplo:

```http
PUT /api/v1/ModificarCliente?ID_Key=42
Content-Type: application/json

{ "ID_Key": "42", "Nombre": "...", ... }
```

Rutas **nuevas** usan path param: `/ModificarHorario/{ID_Key}`, `/EliminarMenu/{ID_Key}`, etc.

### Campo `resultado` en respuestas

Muchos modelos incluyen `resultado: string`. Valor `"Exitoso"` (o similar) indica éxito. Si contiene `"Fallido:"`, hubo error de persistencia aunque el HTTP sea 200 (patrón legacy).

### Formato de errores

```json
{ "detail": "...", "error_type": "http" | "validation" | "database" | ... }
```

Validación Pydantic → **400** con `error_type: "validation"` y `detail` como array de errores.

### Paginación

Query opcionales en listados paginados:

| Query | Default | Máximo |
|-------|---------|--------|
| `limit` | 50 | 100 |
| `offset` | 0 | — |

Respuesta:

```json
{
  "items": [ ... ],
  "total": 120,
  "limit": 50,
  "offset": 0
}
```

---

## Autenticación

### `POST /api/v1/auth/login` — Público

**Rate limit:** 30/min por IP.

**Body:**

```json
{
  "correo": "carlos.ruiz@bytte.demo",
  "contrasena": "hash_demo_u1"
}
```

**Respuesta 200:**

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "kind": "user",
  "restaurant_id": "1"
}
```

| Campo | Tipo | Notas |
|-------|------|-------|
| `access_token` | string | JWT HS256 |
| `token_type` | string | Siempre `"bearer"` |
| `kind` | `"user"` \| `"super"` | Rol de sesión |
| `restaurant_id` | string \| null | Solo para `user`; `null` para `super` |

**Errores:** `401` credenciales inválidas. **No hay refresh token** — al expirar (default 480 min) repetir login.

---

### `POST /api/v1/auth/register` — Público (dueño tras onboarding)

**Rate limit:** 15/min por IP.

Crea el usuario **Propietario** (fallback **Administrador**) enlazado a un restaurante en estado `draft` (`onboarding_estado=borrador`). Devuelve el mismo cuerpo que login (**auto-login**).

**Body:**

```json
{
  "email": "owner@restaurant.test",
  "password": "secret123",
  "owner_name": "Ana García",
  "phone": "+573001234567",
  "restaurant_id": "42"
}
```

Alternativa: omitir `restaurant_id` en el body y enviar header **`X-Restaurant-Id: 42`**.

**Errores:** `400` (restaurante no en borrador), `409` (correo duplicado).

---

## Onboarding (wizard 7 pasos)

Flujo recomendado: **`start`** → pasos **1–7** (con uploads en paso 6) → **`register`** → **`submit`**.

| Método | Ruta | Auth |
|--------|------|------|
| `POST` | `/api/v1/onboarding/start` | Público |
| `POST` / `PATCH` | `/api/v1/onboarding/step/{1-7}` | JWT o `X-Restaurant-Id` |
| `GET` | `/api/v1/onboarding/status` | JWT o `X-Restaurant-Id` |
| `POST` | `/api/v1/onboarding/submit` | JWT dueño (`require_tenant`) |
| `GET` | `/api/v1/onboarding/{restaurant_id}` | Super |

### `POST /onboarding/start`

**Respuesta 200:**

```json
{ "restaurant_id": "123", "status": "draft" }
```

Guardar `restaurant_id` y enviarlo como **`X-Restaurant-Id`** hasta completar registro/login.

### Pasos 1–7 (body por paso)

| Paso | Campos clave |
|------|----------------|
| 1 | `restaurant_name`, `legal_name`, `description`, `website`, `social_links`, `restaurant_type` |
| 2 | `country`, `department`, `city`, `address`, `google_maps`, `lat`, `lng` |
| 3 | `owner_name`, `email`, `phone` |
| 4 | `opening_hours`, `closing_hours`, `seating_capacity`, `number_tables` |
| 5 | `reservation_types[]`, `cuisine_types[]`, `services_offered[]` |
| 6 | `logo_key`, `cover_image_keys[]`, `document_keys[]` (referencias tras confirm upload) |
| 7 | `plan` (`starter`\|`pro`\|`elite`), `billing_cycle` (`monthly`\|`annual`) |

**Respuesta paso:** `{ "restaurant_id", "step", "status", "pct" }`

### `GET /onboarding/status`

```json
{
  "restaurant_id": "123",
  "step": 3,
  "status": "draft",
  "pct": 43,
  "submitted_at": null
}
```

### `POST /onboarding/submit`

Requiere JWT con `restaurant_id`. Activa el restaurante (`status: submitted`, `activo=true`).

---

## Uploads (Supabase Storage)

| Método | Ruta | Auth |
|--------|------|------|
| `POST` | `/api/v1/uploads/presigned` | JWT o `X-Restaurant-Id` |
| `POST` | `/api/v1/uploads/confirm` | JWT o `X-Restaurant-Id` |

**Flujo:** `presigned` → **PUT** archivo a `upload_url` → `confirm` → opcionalmente guardar keys en **paso 6**.

### `POST /uploads/presigned`

```json
{
  "document_type": "logo",
  "filename": "logo.png",
  "mime_type": "image/png"
}
```

`document_type`: `logo` | `cover` | `business_doc`

**Respuesta:** `{ "storage_key", "upload_url", "expires_in" }`

### `POST /uploads/confirm`

```json
{
  "document_type": "logo",
  "storage_key": "123/logo/uuid_logo.png",
  "filename": "logo.png",
  "mime_type": "image/png",
  "size_bytes": 1024
}
```

**Respuesta:** `{ "storage_key", "public_url", "document_type" }`

---

### `POST /api/v1/auth/registro/restaurante` — Público (legacy)

**Rate limit:** 15/min por IP.

**Body — restaurante solo:**

```json
{
  "id_acceso": "",
  "Nombre": "Mi Restaurante",
  "Direccion": "Calle 123",
  "Telefono": "3001234567",
  "Calificacion": 0,
  "Horarios": "",
  "Imagen_destacada": "",
  "Google_maps": "",
  "Rango_de_precios": 2,
  "ID_Ubicacion": "1",
  "ID_categorias": "1",
  "ID_Etiqueta": "1"
}
```

**Body — restaurante + primer empleado:**

```json
{
  "id_acceso": "slug-unico-local",
  "Nombre": "Mi Restaurante",
  "Direccion": "Calle 123",
  "Telefono": "3001234567",
  "Calificacion": 0,
  "Horarios": "",
  "Imagen_destacada": "",
  "Google_maps": "",
  "Rango_de_precios": 2,
  "ID_Ubicacion": "1",
  "ID_categorias": "1",
  "ID_Etiqueta": "1",
  "empleado": {
    "Nombre": "Ana",
    "Apellido": "García",
    "Telefono": "3009876543",
    "Correo": "ana@restaurante.com",
    "Contrasena": "miPassword123",
    "Tipo_Documento": "CC",
    "Numero_Documento": "1234567890",
    "ID_Rol": ""
  }
}
```

| Campo | Obligatorio | Notas |
|-------|-------------|-------|
| `Nombre` | Sí | Nombre del restaurante |
| `Rango_de_precios` | No | Entero 1–4 (1=$ … 4=$$$$), default 1 |
| `id_acceso` | Condicional | **Obligatorio** si envías `empleado` (debe ser único) |
| `empleado` | No | Si se omite, solo se crea el restaurante |
| `empleado.ID_Rol` | No | Vacío → rol "Administrador" en BD |

**Respuesta 200:**

```json
{
  "restaurante": { "...Modelo_Restaurante..." },
  "empleado": { "...Modelo_Usuario..." }
}
```

`empleado` es `null` si no se envió.

**Errores:** `400`, `409` (correo duplicado), `422` (falta `id_acceso` con empleado).

---

### `GET /api/v1/auth/me` — Bearer

Devuelve la sesión actual: `user_id`, `email`, `kind`, `restaurant_id`, `nombre`, `apellido`, `rol`.

---

## Perfil restaurante (esquema Tabi — panel)

Endpoints REST para el panel post-onboarding. Lectura agregada desde SQL directo (onboarding, M2M, archivos, suscripción).

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| `GET` | `/api/v1/restaurants/me` | `user` | Perfil completo del restaurante del token |
| `PATCH` | `/api/v1/restaurants/me` | `user` | Actualización parcial por secciones |
| `GET` | `/api/v1/restaurants/{id}` | `super` | Perfil de cualquier restaurante |

> **Recomendado** para el panel. `GET /api/v1/restaurantes/mi` queda como agregado legacy reducido.

### Body `PATCH /restaurants/me`

```json
{
  "profile": { "nombre": "...", "descripcion": "...", "restaurant_type": "casual" },
  "location": { "pais": "Colombia", "ciudad": "Bogotá", "direccion": "...", "google_maps": "..." },
  "contact": { "telefono": "+57300..." },
  "operations": {
    "opening_hours": "08:00:00",
    "closing_hours": "22:00:00",
    "capacidad_asientos": 50,
    "numero_mesas": 12
  },
  "features": {
    "cuisine_types": ["Italiana"],
    "services_offered": ["WiFi"],
    "reservation_types": ["online"]
  }
}
```

`onboarding.estado` en GET: `draft` | `submitted` (traducido desde BD).

---

## Sistema

### `GET /health` — Público

**Respuesta:**

```json
{ "status": "ok", "database": "ok" }
```

`database` puede ser `"error"` si PostgreSQL no responde.

---

## Restaurante

**Modelo `Modelo_Restaurante`:**

| Campo | Tipo | Notas |
|-------|------|-------|
| `ID_Key` | string | Vacío en altas |
| `id_acceso` | string | Slug/código único del local |
| `Nombre` | string | |
| `Direccion` | string | |
| `Telefono` | string | |
| `Calificacion` | int | Promedio (también sincronizado por triggers) |
| `Horarios` | string | Texto libre legacy |
| `Imagen_destacada` | string | URL o path |
| `Google_maps` | string | |
| `Rango_de_precios` | int | 1–4 |
| `ID_Ubicacion` | string | FK ubicación |
| `ID_categorias` | string | FK categoría global |
| `ID_Etiqueta` | string | FK etiqueta |
| `resultado` | string | Lo rellena el servidor |

| Método | Ruta | Auth | Query / Body | Descripción |
|--------|------|------|--------------|-------------|
| `POST` | `/IngresarRestaurante` | **super** | Body: `Modelo_Restaurante` | Alta de restaurante |
| `PUT` | `/ModificarRestaurante` | **super** | Query: `ID_Key`. Body: `Modelo_Restaurante` | Modificar |
| `DELETE` | `/EliminarRestaurante` | **super** | Query: `ID_Key`. Body: `Modelo_Restaurante` | Eliminar |
| `GET` | `/ConsultarRestaurante` | Bearer | — | **super:** todos. **user:** solo el suyo |
| `GET` | `/ConsultarRestauranteId` | Bearer | Query: `ID_Key` | Por ID. **user:** solo su `restaurant_id` |
| `GET` | `/restaurantes/mi` | Bearer (**user** only) | — | Agregado: restaurante + horarios + rangos + stats calificaciones |

**Respuesta `GET /restaurantes/mi`:**

```json
{
  "restaurante": { "...Modelo_Restaurante..." },
  "horarios": [ "...Modelo_Horario..." ],
  "rangos_precio": [ "...Modelo_RangoPrecioRestaurante..." ],
  "calificacion_promedio": 4.5,
  "calificacion_cantidad": 12
}
```

---

## Reserva

**Modelo `Modelo_Reserva`:**

| Campo | Tipo | Notas |
|-------|------|-------|
| `ID_Key` | string | Vacío en altas |
| `Cantidad_personas` | int | |
| `Fecha` | date | `"2026-06-15"` |
| `Hora` | time | `"19:30:00"` |
| `Codigo_reserva` | string | |
| `Comentarios` | string | |
| `Precio` | int | Default 0 |
| `Preorden` | bool | Default false |
| `ID_Restaurante` | string | **user:** lo fuerza el token |
| `ID_Cliente` | string | FK cliente |
| `Estado` | string \| null | Enum BD (ej. PENDIENTE, CONFIRMADA, CANCELADA) |
| `resultado` | string | |

| Método | Ruta | Auth | Parámetros | Descripción |
|--------|------|------|------------|-------------|
| `POST` | `/IngresarReserva` | Bearer | Body: `Modelo_Reserva` | Alta. **user:** fuerza `ID_Restaurante` del token |
| `PUT` | `/ModificarReserva` | Bearer | Query: `ID_Key`. Body: `Modelo_Reserva` | Modificar completo |
| `PUT` | `/ModificarReserva/{ID_Key}` | Bearer | Path: `ID_Key`. Body: `Modelo_Reserva` | Igual, con ID en path |
| `PUT` | `/Reserva/{ID_Key}/estado` | Bearer | Path: `ID_Key`. Body: `{ "Estado": "CONFIRMADA" }` | Solo cambio de estado |
| `DELETE` | `/EliminarReserva` | Bearer | Query: `ID_Key`. Body: `Modelo_Reserva` | Eliminar |
| `GET` | `/ConsultarReserva` | Bearer | Query: `limit`, `offset` | Listado paginado. **user:** solo su restaurante |
| `GET` | `/ConsultarReservaId` | Bearer | Query: `ID_Key` | Detalle por ID |

**Body cambio de estado:**

```json
{ "Estado": "CONFIRMADA" }
```

Estado se normaliza a mayúsculas en servidor.

---

## Cliente

**Modelo `Modelo_Cliente`:**

| Campo | Tipo |
|-------|------|
| `ID_Key` | string (vacío en altas) |
| `Nombre` | string |
| `Apellido` | string |
| `Telefono` | string |
| `Correo` | string |
| `Contrasena` | string |
| `Tipo_Documento` | string |
| `Numero_Documento` | string |
| `resultado` | string |

> **Nota:** Clientes **no** están aislados por tenant en la API; cualquier usuario autenticado ve/gestiona el catálogo global.

| Método | Ruta | Auth | Parámetros | Descripción |
|--------|------|------|------------|-------------|
| `POST` | `/IngresarCliente` | Bearer | Body: `Modelo_Cliente` | Alta |
| `PUT` | `/ModificarCliente` | Bearer | Query: `ID_Key`. Body: `Modelo_Cliente` | Modificar |
| `DELETE` | `/EliminarCliente` | Bearer | Query: `ID_Key`. Body: `Modelo_Cliente` | Eliminar |
| `GET` | `/ConsultarCliente` | Bearer | — | Listar todos |
| `GET` | `/ConsultarClienteId` | Bearer | Query: `ID_Key` | Por ID |
| `GET` | `/ConsultarClientePorNumeroDocumento` | Bearer | Query: `Numero_Documento` o `numero_documento` | Buscar por documento |

---

## Usuario (empleado)

**Modelo `Modelo_UsuarioAlta` (solo POST `/IngresarUsuario`):**

| Campo | Tipo | Obligatorio | Alias snake_case |
|-------|------|-------------|------------------|
| `Nombre` | string | Sí | `nombre` |
| `Apellido` | string | No | `apellido` |
| `Telefono` | string | No | `telefono` |
| `Correo` | string | Sí | `correo` |
| `Contrasena` | string | Sí | `contrasena` |
| `Tipo_Documento` | string | No | `tipo_documento` |
| `Numero_Documento` | string | No | `numero_documento` |
| `ID_Rol` | string | Sí | `id_rol` |
| `ID_Restaurante` | string | No | `id_restaurante` — **user:** lo fuerza el token |

No envíes `ID_Key` ni `resultado` en el alta.

**Modelo `Modelo_Usuario` (PUT/respuesta):**

| Campo | Tipo | Notas |
|-------|------|-------|
| `ID_Key` | string | |
| `Nombre` | string | |
| `Apellido` | string | |
| `Telefono` | string | |
| `Correo` | string | |
| `Contrasena` | string | Se hashea si no es bcrypt `$2…` |
| `Tipo_Documento` | string | |
| `Numero_Documento` | string | |
| `ID_Rol` | string | FK rol |
| `ID_Restaurante` | string | **user:** lo fuerza el token |
| `resultado` | string | |

| Método | Ruta | Auth | Parámetros | Descripción |
|--------|------|------|------------|-------------|
| `POST` | `/IngresarUsuario` | Bearer | Body: `Modelo_UsuarioAlta` | Alta empleado |
| `PUT` | `/ModificarUsuario` | Bearer | Query: `ID_Key`. Body: `Modelo_Usuario` | Modificar |
| `DELETE` | `/EliminarUsuario` | Bearer | Query: `ID_Key` (obligatorio). Body opcional | Eliminar empleado |
| `DELETE` | `/EliminarUsuario/{ID_Key}` | Bearer | Path: `ID_Key`. Body opcional | Eliminar empleado (recomendado) |
| `GET` | `/ConsultarUsuario` | Bearer | — | **super:** todos. **user:** empleados de su restaurante |
| `GET` | `/ConsultarUsuarioId` | Bearer | Query: `ID_Key` | Por ID |

---

## Pedido

**Modelo `Modelo_PedidoAlta` (solo POST):**

| Campo | Tipo | Obligatorio |
|-------|------|-------------|
| `Cantidad` | int ≥ 1 | Sí |
| `Descripcion` | string | No |
| `Precio_Unitario` | int ≥ 0 | Sí |
| `Importe` | int ≥ 0 | Sí |
| `ID_Reserva` | string | Sí |

**Modelo `Modelo_Pedido` (PUT/DELETE/respuesta):**

| Campo | Tipo |
|-------|------|
| `ID_Key` | string |
| `Cantidad` | int |
| `Descripcion` | string |
| `Precio_Unitario` | int |
| `Importe` | int |
| `ID_Reserva` | string |
| `resultado` | string |

| Método | Ruta | Auth | Parámetros | Descripción |
|--------|------|------|------------|-------------|
| `POST` | `/IngresarPedido` | Bearer | Body: `Modelo_PedidoAlta` | Alta (sin `ID_Key`) |
| `PUT` | `/ModificarPedido` | Bearer | Query: `ID_Key`. Body: `Modelo_Pedido` | Modificar |
| `DELETE` | `/EliminarPedido` | Bearer | Query: `ID_Key`. Body: `Modelo_Pedido` | Eliminar |
| `GET` | `/ConsultarPedido` | Bearer | Query: `limit`, `offset` | Paginado. **user:** solo su restaurante |
| `GET` | `/ConsultarPedidoId` | Bearer | Query: `ID_Key` | Por ID |

---

## Pagos

**Modelo `Modelo_Pagos`:**

| Campo | Tipo | Notas |
|-------|------|-------|
| `ID_Key` | string | |
| `Nombre_Cliente` | string | |
| `Subtotal` | int | |
| `Iva` | int | |
| `Total` | int | |
| `Metodo_de_pago` | string | |
| `Fecha` | date | |
| `Fecha_Vencimiento` | date | |
| `Tiempo` | time | |
| `Logo` | string | |
| `ID_Pedido` | string | FK pedido |
| `resultado` | string | |

| Método | Ruta | Auth | Parámetros | Descripción |
|--------|------|------|------------|-------------|
| `POST` | `/IngresarPagos` | Bearer | Body: `Modelo_Pagos` | Alta |
| `PUT` | `/ModificarPagos` | Bearer | Query: `ID_Key`. Body: `Modelo_Pagos` | Modificar |
| `DELETE` | `/EliminarPagos` | Bearer | Query: `ID_Key`. Body: `Modelo_Pagos` | Eliminar |
| `GET` | `/ConsultarPagos` | Bearer | — | **super:** todos. **user:** pagos de su restaurante |
| `GET` | `/ConsultarPagosId` | Bearer | Query: `ID_Key` | Por ID |

---

## Rol — catálogo global

**Modelo `Modelo_Rol`:** `ID_Key`, `Nombre`, `resultado`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| `POST` | `/IngresarRol` | **super** | Alta |
| `PUT` | `/ModificarRol` | **super** | Query: `ID_Key` + body |
| `DELETE` | `/EliminarRol` | **super** | Query: `ID_Key` + body |
| `GET` | `/ConsultarRol` | Bearer | Listar (lectura para todos autenticados) |
| `GET` | `/ConsultarRolId` | Bearer | Query: `ID_Key` |

---

## Ubicación — catálogo global

**Modelo `Modelo_Ubicacion`:**

| Campo | Tipo |
|-------|------|
| `ID_Key` | string |
| `Pais` | string |
| `Departamento` | string |
| `Ciudad` | string |
| `Barrio` | string |
| `ID_Ciudad` | string (FK catálogo, opcional) |
| `resultado` | string |

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| `POST` | `/IngresarUbicacion` | **super** | Alta |
| `PUT` | `/ModificarUbicacion` | **super** | Query: `ID_Key` + body |
| `DELETE` | `/EliminarUbicacion` | **super** | Query: `ID_Key` + body |
| `GET` | `/ConsultarUbicacion` | Bearer | Listar |
| `GET` | `/ConsultarUbicacionId` | Bearer | Query: `ID_Key` |

---

## Categorías globales (tipo de restaurante)

**Modelo `Modelo_Categorias`:** `ID_Key`, `Nombre`, `resultado`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| `POST` | `/IngresarCategorias` | **super** | Alta |
| `PUT` | `/ModificarCategorias` | **super** | Query: `ID_Key` + body |
| `DELETE` | `/EliminarCategorias` | **super** | Query: `ID_Key` + body |
| `GET` | `/ConsultarCategorias` | Bearer | Listar |
| `GET` | `/ConsultarCategoriasId` | Bearer | Query: `ID_Key` |

---

## Etiquetas globales

**Modelo `Modelo_Etiquetas`:** `ID_Key`, `Nombre`, `svg`, `resultado`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| `POST` | `/IngresarEtiquetas` | **super** | Alta |
| `PUT` | `/ModificarEtiquetas` | **super** | Query: `ID_Key` + body |
| `DELETE` | `/EliminarEtiquetas` | **super** | Query: `ID_Key` + body |
| `GET` | `/ConsultarEtiquetas` | Bearer | Listar |
| `GET` | `/ConsultarEtiquetasId` | Bearer | Query: `ID_Key` |

---

## Super usuario

**Modelo `Modelo_Super_Usuario`:**

| Campo | Tipo |
|-------|------|
| `ID_Key` | string |
| `Nombre` | string |
| `Apellido` | string |
| `Telefono` | string |
| `Correo` | string |
| `Contrasena` | string |
| `Tipo_Documento` | string |
| `Numero_Documento` | string |
| `resultado` | string |

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| `POST` | `/IngresarSuperUsuario` | **super** | Alta |
| `PUT` | `/ModificarSuperUsuario` | **super** | Query: `ID_Key` + body |
| `DELETE` | `/EliminarSuperUsuario` | **super** | Query: `ID_Key` + body |
| `GET` | `/ConsultarSuperUsuario` | **super** | Listar |
| `GET` | `/ConsultarSuperUsuarioId` | **super** | Query: `ID_Key` |

---

## Geografía (lectura)

**Modelo `Modelo_Departamento`:** `ID_Key`, `Nombre`, `Codigo_iso`, `Activo`, `resultado`

**Modelo `Modelo_Ciudad`:** `ID_Key`, `ID_Departamento`, `Nombre`, `resultado`

| Método | Ruta | Auth | Query | Descripción |
|--------|------|------|-------|-------------|
| `GET` | `/ConsultarDepartamentos` | Bearer | — | Departamentos Colombia |
| `GET` | `/ConsultarCiudadPorDepartamento` | Bearer | `ID_Departamento` | Ciudades del departamento |

**Flujo UI:** departamentos → ciudades → guardar `ID_Ciudad` en ubicación.

---

## Horarios por restaurante

**Modelo `Modelo_Horario`:**

| Campo | Tipo | Notas |
|-------|------|-------|
| `ID_Key` | string | Vacío en altas |
| `ID_Restaurante` | string | **user:** lo fuerza el token |
| `Dia_semana` | int 0–6 | 0=domingo … 6=sábado |
| `Hora_apertura` | time | `"09:00:00"` |
| `Hora_cierre` | time | `"22:00:00"` |
| `Etiqueta_dia` | string | Opcional |
| `Activo` | bool | Default true |
| `resultado` | string | |

| Método | Ruta | Auth | Parámetros | Descripción |
|--------|------|------|------------|-------------|
| `GET` | `/ConsultarHorarios` | Bearer | **super:** query `id_restaurante` | Listar horarios |
| `POST` | `/IngresarHorario` | Bearer | Body: `Modelo_Horario` | Upsert por `(restaurante, dia_semana)` |
| `PUT` | `/ModificarHorario/{ID_Key}` | Bearer | Path + body | Actualizar fila |
| `DELETE` | `/EliminarHorario/{ID_Key}` | Bearer | **super:** query `id_restaurante` | Eliminar |

---

## Rango de precio por restaurante

**Modelo `Modelo_RangoPrecioRestaurante`:**

| Campo | Tipo | Notas |
|-------|------|-------|
| `ID_Key` | string | |
| `ID_Restaurante` | string | **user:** lo fuerza el token |
| `Nivel` | string | `"$"`, `"$$"`, `"$$$"`, `"$$$$"` |
| `Es_principal` | bool | |
| `Notas` | string | |
| `resultado` | string | |

| Método | Ruta | Auth | Parámetros | Descripción |
|--------|------|------|------------|-------------|
| `GET` | `/ConsultarRangoPrecioRestaurante` | Bearer | **super:** `id_restaurante` | Listar |
| `POST` | `/IngresarRangoPrecioRestaurante` | Bearer | Body | Upsert por `(restaurante, nivel)` |
| `DELETE` | `/EliminarRangoPrecioRestaurante/{ID_Key}` | Bearer | **super:** `id_restaurante` | Eliminar |

---

## Calificaciones

**Modelo `Modelo_Calificacion`:**

| Campo | Tipo | Notas |
|-------|------|-------|
| `ID_Key` | string | |
| `ID_Restaurante` | string | **user:** solo su restaurante |
| `Puntuacion` | decimal 0–5 | |
| `Comentario` | string | |
| `ID_Cliente` | string | Opcional |
| `Origen` | string | Opcional |
| `resultado` | string | |

| Método | Ruta | Auth | Parámetros | Descripción |
|--------|------|------|------------|-------------|
| `GET` | `/ConsultarCalificacionRestaurante` | Bearer | `limit`, `offset`. **super:** `id_restaurante` | Paginado |
| `POST` | `/IngresarCalificacion` | Bearer | Body | Nueva calificación |

---

## Menú por pedido

Validación tenant: `pedido → reserva → id_restaurante`.

**Modelo `Modelo_Menu`:**

| Campo | Tipo |
|-------|------|
| `ID_Key` | string |
| `ID_Pedido` | string |
| `Nombre` | string |
| `Descripcion` | string |
| `Orden` | int |
| `Activo` | bool |
| `resultado` | string |

| Método | Ruta | Auth | Parámetros | Descripción |
|--------|------|------|------------|-------------|
| `GET` | `/ConsultarMenuPorPedido` | Bearer | Query: `ID_Pedido` | Menús del pedido |
| `POST` | `/IngresarMenu` | Bearer | Body: `Modelo_Menu` | Alta |
| `PUT` | `/ModificarMenu/{ID_Key}` | Bearer | Path + body | Modificar |
| `DELETE` | `/EliminarMenu/{ID_Key}` | Bearer | Path | Eliminar |

---

## Categoría de menú

**Modelo `Modelo_CategoriaMenu`:**

| Campo | Tipo |
|-------|------|
| `ID_Key` | string |
| `ID_Menu` | string |
| `Nombre` | string |
| `Descripcion` | string |
| `Orden` | int |
| `resultado` | string |

| Método | Ruta | Auth | Parámetros | Descripción |
|--------|------|------|------------|-------------|
| `GET` | `/ConsultarCategoriaMenuPorMenu` | Bearer | Query: `ID_Menu` | Categorías del menú |
| `POST` | `/IngresarCategoriaMenu` | Bearer | Body | Alta |
| `PUT` | `/ModificarCategoriaMenu/{ID_Key}` | Bearer | Path + body | Modificar |
| `DELETE` | `/EliminarCategoriaMenu/{ID_Key}` | Bearer | Path | Eliminar |

---

## Matriz de permisos (resumen UI)

| Recurso | Lectura `user` | Escritura `user` | Lectura `super` | Escritura `super` |
|---------|----------------|------------------|-----------------|-------------------|
| Restaurante | Solo el suyo | No | Todos | Sí |
| `/restaurantes/mi` | Sí | — | No (403) | — |
| Reserva, Pedido, Pago, Usuario | Filtrado por tenant | Sí (su restaurante) | Global | Sí |
| Cliente | Global | Sí | Global | Sí |
| Rol, Ubicación, Categorías, Etiquetas | Sí | No | Sí | Sí |
| Super usuario | No | No | Sí | Sí |
| Horarios, Rangos, Calificaciones, Menú | Su restaurante | Sí | Global (+ `id_restaurante`) | Sí |
| Geografía | Sí | No | Sí | No |

---

## Cuentas demo (tras `scripts/seed_database.sql`)

| Rol | Correo | Contraseña |
|-----|--------|------------|
| Empleado Bogotá | `carlos.ruiz@bytte.demo` | `hash_demo_u1` |
| Empleado Medellín | `diana.perez@bytte.demo` | `hash_demo_u2` |
| Superusuario | `admin@bytte.os` | `hash_super_demo` |

---

## Checklist cliente HTTP (TypeScript / fetch)

```typescript
const API = import.meta.env.VITE_API_URL; // ej. http://localhost:8000

async function api(path: string, options: RequestInit = {}) {
  const token = sessionStorage.getItem("access_token");
  const res = await fetch(`${API}/api/v1${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  if (res.status === 401) { /* logout + redirect login */ }
  return res;
}

// Login
await fetch(`${API}/api/v1/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ correo, contrasena }),
});

// Listado paginado
await api("/ConsultarReserva?limit=20&offset=0");

// Modificar legacy (ID en query)
await api("/ModificarCliente?ID_Key=42", {
  method: "PUT",
  body: JSON.stringify({ ID_Key: "42", Nombre: "...", /* resto campos */ }),
});
```

---

## Índice rápido de rutas

| # | Método | Ruta completa |
|---|--------|---------------|
| — | GET | `/health` |
| 1 | POST | `/api/v1/auth/login` |
| 2 | POST | `/api/v1/auth/registro/restaurante` |
| 3 | GET | `/api/v1/auth/me` |
| 4 | GET | `/api/v1/restaurants/me` |
| 5 | PATCH | `/api/v1/restaurants/me` |
| 6 | GET | `/api/v1/restaurants/{id}` |
| 7 | GET | `/api/v1/restaurantes/mi` |
| 4 | POST | `/api/v1/IngresarRestaurante` |
| 5 | PUT | `/api/v1/ModificarRestaurante` |
| 6 | DELETE | `/api/v1/EliminarRestaurante` |
| 7 | GET | `/api/v1/ConsultarRestaurante` |
| 8 | GET | `/api/v1/ConsultarRestauranteId` |
| 9 | POST | `/api/v1/IngresarReserva` |
| 10 | PUT | `/api/v1/ModificarReserva` |
| 11 | PUT | `/api/v1/ModificarReserva/{ID_Key}` |
| 12 | PUT | `/api/v1/Reserva/{ID_Key}/estado` |
| 13 | DELETE | `/api/v1/EliminarReserva` |
| 14 | GET | `/api/v1/ConsultarReserva` |
| 15 | GET | `/api/v1/ConsultarReservaId` |
| 16 | POST | `/api/v1/IngresarCliente` |
| 17 | PUT | `/api/v1/ModificarCliente` |
| 18 | DELETE | `/api/v1/EliminarCliente` |
| 19 | GET | `/api/v1/ConsultarCliente` |
| 20 | GET | `/api/v1/ConsultarClienteId` |
| 21 | GET | `/api/v1/ConsultarClientePorNumeroDocumento` |
| 22 | POST | `/api/v1/IngresarUsuario` |
| 23 | PUT | `/api/v1/ModificarUsuario` |
| 24 | DELETE | `/api/v1/EliminarUsuario` |
| 25 | GET | `/api/v1/ConsultarUsuario` |
| 26 | GET | `/api/v1/ConsultarUsuarioId` |
| 27 | POST | `/api/v1/IngresarPedido` |
| 28 | PUT | `/api/v1/ModificarPedido` |
| 29 | DELETE | `/api/v1/EliminarPedido` |
| 30 | GET | `/api/v1/ConsultarPedido` |
| 31 | GET | `/api/v1/ConsultarPedidoId` |
| 32 | POST | `/api/v1/IngresarPagos` |
| 33 | PUT | `/api/v1/ModificarPagos` |
| 34 | DELETE | `/api/v1/EliminarPagos` |
| 35 | GET | `/api/v1/ConsultarPagos` |
| 36 | GET | `/api/v1/ConsultarPagosId` |
| 37 | POST | `/api/v1/IngresarRol` |
| 38 | PUT | `/api/v1/ModificarRol` |
| 39 | DELETE | `/api/v1/EliminarRol` |
| 40 | GET | `/api/v1/ConsultarRol` |
| 41 | GET | `/api/v1/ConsultarRolId` |
| 42 | POST | `/api/v1/IngresarUbicacion` |
| 43 | PUT | `/api/v1/ModificarUbicacion` |
| 44 | DELETE | `/api/v1/EliminarUbicacion` |
| 45 | GET | `/api/v1/ConsultarUbicacion` |
| 46 | GET | `/api/v1/ConsultarUbicacionId` |
| 47 | POST | `/api/v1/IngresarCategorias` |
| 48 | PUT | `/api/v1/ModificarCategorias` |
| 49 | DELETE | `/api/v1/EliminarCategorias` |
| 50 | GET | `/api/v1/ConsultarCategorias` |
| 51 | GET | `/api/v1/ConsultarCategoriasId` |
| 52 | POST | `/api/v1/IngresarEtiquetas` |
| 53 | PUT | `/api/v1/ModificarEtiquetas` |
| 54 | DELETE | `/api/v1/EliminarEtiquetas` |
| 55 | GET | `/api/v1/ConsultarEtiquetas` |
| 56 | GET | `/api/v1/ConsultarEtiquetasId` |
| 57 | POST | `/api/v1/IngresarSuperUsuario` |
| 58 | PUT | `/api/v1/ModificarSuperUsuario` |
| 59 | DELETE | `/api/v1/EliminarSuperUsuario` |
| 60 | GET | `/api/v1/ConsultarSuperUsuario` |
| 61 | GET | `/api/v1/ConsultarSuperUsuarioId` |
| 62 | GET | `/api/v1/ConsultarDepartamentos` |
| 63 | GET | `/api/v1/ConsultarCiudadPorDepartamento` |
| 64 | GET | `/api/v1/ConsultarHorarios` |
| 65 | POST | `/api/v1/IngresarHorario` |
| 66 | PUT | `/api/v1/ModificarHorario/{ID_Key}` |
| 67 | DELETE | `/api/v1/EliminarHorario/{ID_Key}` |
| 68 | GET | `/api/v1/ConsultarRangoPrecioRestaurante` |
| 69 | POST | `/api/v1/IngresarRangoPrecioRestaurante` |
| 70 | DELETE | `/api/v1/EliminarRangoPrecioRestaurante/{ID_Key}` |
| 71 | GET | `/api/v1/ConsultarCalificacionRestaurante` |
| 72 | POST | `/api/v1/IngresarCalificacion` |
| 73 | GET | `/api/v1/ConsultarMenuPorPedido` |
| 74 | POST | `/api/v1/IngresarMenu` |
| 75 | PUT | `/api/v1/ModificarMenu/{ID_Key}` |
| 76 | DELETE | `/api/v1/EliminarMenu/{ID_Key}` |
| 77 | GET | `/api/v1/ConsultarCategoriaMenuPorMenu` |
| 78 | POST | `/api/v1/IngresarCategoriaMenu` |
| 79 | PUT | `/api/v1/ModificarCategoriaMenu/{ID_Key}` |
| 80 | DELETE | `/api/v1/EliminarCategoriaMenu/{ID_Key}` |

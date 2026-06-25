# Guía de integración front — autenticación y permisos

Este documento describe qué debe implementar el cliente web contra el backend Bytte (JWT, tenant, roles).

## URL base y CORS

- **Base URL:** configurable por entorno (ej. `http://localhost:8000` en desarrollo). La documentación interactiva está en `{baseUrl}/docs`.
- **`GET /health`:** comprueba vida del proceso y opcionalmente la BD (`database: "ok"|"error"`); útil para load balancers; **no** requiere JWT.
- **Prefijo REST:** todas las rutas de negocio están bajo **`/api/v1`** (los ejemplos de esta guía usan ese prefijo para auth).
- **CORS:** el servidor solo permite el origen configurado en la variable de entorno **`FRONT_URL`** del backend. El front en desarrollo debe coincidir exactamente (ej. `http://localhost:3000`). Si no coincide, el navegador bloqueará las peticiones.

## Login (ruta pública)

| Método | Ruta | Cuerpo |
|--------|------|--------|
| `POST` | `/api/v1/auth/login` | JSON: `correo`, `contrasena` |

**Ejemplo:**

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
  "restaurant_id": "123"
}
```

- **`kind`:** `"user"` (empleado de restaurante) o `"super"` (administración de plataforma).
- **`restaurant_id`:** presente y en string cuando `kind === "user"` (identificador del restaurante asignado). Es `null` para `super`.

**Error:** `401` con mensaje de credenciales inválidas (`error_type: http`).

**Rate limiting:** en producción, `login` tiene límite por IP (**30/min** por defecto con SlowAPI). Respuestas **429** ⇒ esperar y reintentar sin spamear el endpoint.

## Sesión actual (`GET /auth/me`)

| Método | Ruta | Auth |
|--------|------|------|
| `GET` | `/api/v1/auth/me` | Bearer |

**Respuesta 200 (empleado):**

```json
{
  "user_id": "12",
  "email": "carlos.ruiz@bytte.demo",
  "kind": "user",
  "restaurant_id": "1",
  "nombre": "Carlos",
  "apellido": "Ruiz",
  "rol": "Administrador"
}
```

**Respuesta 200 (super):** `kind: "super"`, `restaurant_id: null`, `rol: "super"`.

Útil tras el login para hidratar el layout del panel sin decodificar el JWT en el cliente.

**Permisos por rol:** la respuesta incluye `permissions` (array de strings) e `is_admin`. Ver [`FRONTEND_ROLES.md`](FRONTEND_ROLES.md).

## Matriz de permisos (pública)

| Método | Ruta |
|--------|------|
| `GET` | `/api/v1/auth/roles/permissions` |

Devuelve `{ "roles": { "Mesero": ["orders.read", ...], ... } }` para documentación en UI o settings.

## Registro dueño tras onboarding (`POST /auth/register`)

| Método | Ruta | Cuerpo |
|--------|------|--------|
| `POST` | `/api/v1/auth/register` | JSON: `email`, `password`, `owner_name`, `phone`, `restaurant_id` (opcional si hay header) |

**Header alternativo:** `X-Restaurant-Id` (mismo valor devuelto por `POST /api/v1/onboarding/start`).

**Respuesta 200:** igual que login — `{ "access_token", "token_type", "kind": "user", "restaurant_id" }`.

**Errores:** `400` (restaurante no en borrador), `409` (correo ya registrado).

**Diferencia con `/auth/registro/restaurante`:** el flujo Tabi crea el restaurante con `/onboarding/start` y los pasos del wizard; `/auth/register` solo crea el usuario dueño enlazado a ese `restaurant_id`. El endpoint legacy crea restaurante + empleado en una sola llamada.

## Registro público de restaurante (legacy, sin token)

| Método | Ruta | Cuerpo |
|--------|------|--------|
| `POST` | `/api/v1/auth/registro/restaurante` | JSON: datos del restaurante + opcional objeto `empleado` |

**Solo restaurante:** mismos campos que `IngresarRestaurante` (sin `ID_Key`). `id_acceso` puede ir vacío si no registras empleado.

**Restaurante + empleado:** incluye `empleado` con `Nombre`, `Apellido`, `Telefono`, `Correo`, `Contrasena`, `Tipo_Documento`, `Numero_Documento`, `ID_Rol` (opcional; si va vacío se usa el rol **Administrador** en BD). En este caso **`id_acceso` es obligatorio** (debe ser único; sirve para enlazar el restaurante creado con el usuario).

**Respuesta 200:**

```json
{
  "restaurante": { "...Modelo_Restaurante..." },
  "empleado": { "...Modelo_Usuario..." }
}
```

Si no envías `empleado`, `empleado` será `null`.

**Errores:** `400` (fallo en BD o validación), `409` si el correo del empleado ya existe, `422` si falta `id_acceso` teniendo `empleado`.

**Seguridad:** endpoint público con **rate limiting** en servidor; en producción conviene además captcha o revisión manual.

## Sesión larga y **JWT_SECRET**

**Refresh token:** no hay endpoint de refresh. Cuando el JWT expire (por defecto **480** minutos, configurable con `JWT_EXPIRE_MINUTES` en el servidor), el cliente debe pedir login de nuevo y sustituir el `access_token`.

**Rotación de `JWT_SECRET` (operación):**

- Guarde la clave sólo en un gestor de secretos (no en el repositorio). Longitud recomendada: **32+ caracteres aleatorios** (HS256).
- Al rotar la clave, todos los tokens firmados con la clave anterior dejan de ser válidos (**401**) en cuanto el servidor arranca sólo con la clave nueva. Para **cero downtime**, despliegue un paso intermedio que acepte la clave antigua y la nueva (no implementado por defecto en este repo): por ejemplo dos secretos en env y validación “intenta segunda clave si falla la primera”, o cortar sesiones en una ventana de mantenimiento.
- Tras la rotación, los usuarios deberán volver a autenticarse.

## Todas las demás rutas: Bearer obligatorio

Salvo las rutas públicas de **`/api/v1/auth/...`** y **`GET /health`**, cada petición debe incluir:

```http
Authorization: Bearer <access_token>
```

### Implementación recomendada

1. Tras login exitoso, persistir `access_token` (y opcionalmente `kind`, `restaurant_id`) según la política del equipo (`sessionStorage` vs `localStorage` vs memoria).
2. Configurar un cliente HTTP (Axios, fetch wrapper, etc.) que inyecte automáticamente la cabecera `Authorization` y el prefijo base **`/api/v1`** para recursos REST.
3. Ante respuesta **401**, limpiar sesión y redirigir a la pantalla de login.

## Modelo de permisos en UI

Usar `kind` (y `restaurant_id` para contexto visual) para decidir menús y rutas.

| Área | `user` (empleado) | `super` |
|------|-------------------|--------|
| Restaurantes: alta / edición / baja | No (403 si se intenta) | Sí |
| Consulta de restaurantes | Solo el propio (`restaurant_id`) | Lista completa |
| Reservas, pedidos, pagos, usuarios (empleados) | Datos filtrados al restaurante del token | Sin filtro de tenant |
| Superusuarios (CRUD) | No | Sí |
| Rol, ubicación, categorías, etiquetas: **lectura** | Sí (autenticado) | Sí |
| Rol, ubicación, categorías, etiquetas: **escritura** | No (403) | Sí |
| Clientes (CRUD) | Sí (autenticado; sin aislamiento por tenant en API) | Sí |

El backend fuerza en varios casos el `id_restaurante` del token; el front no debe confiar en que enviar otro ID en el body permita actuar sobre otro restaurante.

## Errores HTTP frecuentes

| Código | Acción sugerida en front |
|--------|---------------------------|
| 401 | Token ausente, inválido o expirado → cerrar sesión y login |
| 403 | Autenticado pero sin permiso para la operación → mensaje claro |
| 400 | Validación (`error_type: validation`) u otros; revisar `detail` |

## Cuentas de demostración

Tras ejecutar el seed de base de datos (`scripts/seed_database.sql`):

| Rol | Correo | Contraseña |
|-----|--------|--------------|
| Empleado (ej. Bogotá) | `carlos.ruiz@bytte.demo` | `hash_demo_u1` |
| Empleado (ej. Medellín) | `diana.perez@bytte.demo` | `hash_demo_u2` |
| Superusuario | `admin@bytte.os` | `hash_super_demo` |

## Checklist de implementación

- [ ] Variable de entorno para la URL del API (ej. `VITE_API_URL`, `NEXT_PUBLIC_API_URL`) apuntando a la raíz del backend (los paths llevan **`/api/v1/...`**).
- [ ] Pantalla de login → `POST /api/v1/auth/login`.
- [ ] Tras login → `GET /api/v1/auth/me` para nombre, rol y `restaurant_id`.
- [ ] Alta sin sesión → `POST /api/v1/auth/registro/restaurante` (solo local o `restaurante` + `empleado`).
- [ ] Almacenamiento seguro del token y datos mínimos de sesión (`kind`, `restaurant_id`).
- [ ] Cliente HTTP con `Authorization: Bearer` en todas las peticiones autenticadas.
- [ ] Rutas o layouts protegidos: sin token → redirección a login.
- [ ] Navegación y acciones condicionadas por `kind` (empleado vs admin plataforma).
- [ ] Manejo global de 401 (logout + redirección).
- [ ] Verificar que el origen del front en desarrollo coincide con `FRONT_URL` del backend.

## Referencia de endpoints

Las rutas de negocio viven bajo **`/api/v1`** (ej. `GET /api/v1/ConsultarRestaurante`, `POST /api/v1/IngresarReserva`). La lista completa y los esquemas de cuerpo están en `{baseUrl}/docs`.

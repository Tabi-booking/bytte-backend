# Roles y permisos — guía frontend

El backend aplica **RBAC** (permisos por rol). El front debe **ocultar UI** según permisos y confiar en que el API devuelve **403** si intentan una acción no permitida.

Complementa [`FRONTEND_AUTH.md`](FRONTEND_AUTH.md).

---

## Flujo recomendado

1. `POST /api/v1/auth/login` o `/auth/register`
2. **`GET /api/v1/auth/me`** → hidratar sesión con `rol`, `permissions`, `is_admin`
3. Opcional al arrancar la app: **`GET /api/v1/auth/roles/permissions`** → matriz completa rol → permisos (pública)
4. Mostrar menús y botones solo si `permissions.includes("...")`
5. Ante **403** con `Permiso requerido: xxx` → toast o pantalla de acceso denegado

---

## Respuesta `GET /auth/me` (empleado)

```json
{
  "user_id": "12",
  "email": "ana@restaurant.test",
  "kind": "user",
  "restaurant_id": "24",
  "nombre": "Ana",
  "apellido": "García",
  "rol": "Propietario",
  "permissions": [
    "clients.read",
    "clients.write",
    "menu.read",
    "menu.write",
    "orders.read",
    "orders.write",
    "payments.read",
    "payments.write",
    "reservations.read",
    "reservations.write",
    "restaurant.read",
    "restaurant.submit_onboarding",
    "restaurant.write",
    "reviews.read",
    "schedules.read",
    "schedules.write",
    "uploads.write",
    "users.read",
    "users.write"
  ],
  "is_admin": true
}
```

| Campo | Uso en UI |
|-------|-----------|
| `rol` | Etiqueta visible (“Mesero”, “Administrador”) |
| `permissions` | **Fuente de verdad** para mostrar/ocultar acciones |
| `is_admin` | Atajo: `true` si rol es **Propietario** o **Administrador** (todos los permisos del restaurante) |

`is_admin` no sustituye a `permissions` para lógica fina; úsalo para secciones de “configuración” o “equipo”.

---

## Roles por defecto

| Rol | Quién lo recibe | Alcance |
|-----|-----------------|---------|
| **Propietario** | Primer usuario (`POST /auth/register` tras onboarding) | **Todos** los permisos del restaurante |
| **Administrador** | Legacy `/registro/restaurante` o asignado por admin | **Todos** los permisos del restaurante |
| **Mesero** | Asignado por admin | Reservas, pedidos, clientes, menú lectura |
| **Cocinero** | Asignado por admin | Pedidos, menú lectura |
| **Cajero** | Asignado por admin | Pedidos, pagos, clientes, reservas lectura |

**Regla:** solo **Propietario** y **Administrador** pueden crear/editar/eliminar empleados (`users.write`). **Nadie** puede asignar el rol **Propietario** a otro usuario vía API (solo el registro inicial).

---

## Catálogo de permisos

| Permiso | Acción típica en UI | Endpoints principales |
|---------|---------------------|------------------------|
| `restaurant.read` | Ver perfil del local | `GET /restaurants/me`, `GET /ConsultarRestaurante`, `GET /ConsultarRangoPrecioRestaurante` |
| `restaurant.write` | Editar perfil / rangos | `PATCH/PUT /restaurants/me`, `POST /IngresarRangoPrecioRestaurante`, `POST /IngresarCalificacion` |
| `restaurant.submit_onboarding` | Finalizar alta | `POST /onboarding/submit` |
| `users.read` | Listar empleados | `GET /ConsultarUsuario` |
| `users.write` | Alta/baja empleados | `POST /IngresarUsuario`, `PUT/DELETE` usuario |
| `reservations.read` | Ver reservas | `GET /ConsultarReserva` |
| `reservations.write` | Crear/editar reservas | `POST /IngresarReserva`, etc. |
| `orders.read` | Ver pedidos | `GET /ConsultarPedido` |
| `orders.write` | Gestionar pedidos | `POST /IngresarPedido`, etc. |
| `menu.read` | Ver carta / ítems de pedido | `GET /ConsultarMenuPorPedido`, `GET /ConsultarCategoriaMenuPorMenu` |
| `menu.write` | Editar carta | `POST /IngresarMenu`, `PUT/DELETE` menú y categoría menú |
| `payments.read` | Ver pagos | `GET /ConsultarPagos` |
| `payments.write` | Registrar pagos | `POST /IngresarPagos` |
| `clients.read` | Ver clientes | `GET /ConsultarCliente` |
| `clients.write` | CRUD clientes | `POST /IngresarCliente`, etc. |
| `schedules.read` | Ver horarios | `GET /ConsultarHorarios` |
| `schedules.write` | Editar horarios | `POST /IngresarHorario`, etc. |
| `uploads.write` | Subir logo/imágenes | `POST /uploads/presigned`, `/confirm` |
| `reviews.read` | Ver calificaciones | `GET /ConsultarCalificacionRestaurante` |

**Catálogos globales** (solo JWT válido, sin permiso de tenant): `GET /ConsultarCategorias`, `/ConsultarEtiquetas`, `/ConsultarUbicacion`, `/ConsultarDepartamentos`, `/ConsultarCiudadPorDepartamento`.

---

## Matriz rol → permisos (resumen)

Consulta en vivo: **`GET /api/v1/auth/roles/permissions`** (sin JWT).

### Propietario / Administrador
Todos los permisos de la tabla anterior.

### Mesero
`restaurant.read`, `reservations.*`, `orders.*`, `menu.read`, `clients.*`, `reviews.read`

### Cocinero
`restaurant.read`, `orders.*`, `menu.read`

### Cajero
`restaurant.read`, `orders.*`, `payments.*`, `clients.*`, `reservations.read`

---

## Implementación en React (ejemplo)

```typescript
type AuthMe = {
  rol: string | null;
  permissions: string[];
  is_admin: boolean;
};

function can(perms: string[], permission: string): boolean {
  return perms.includes(permission);
}

// Tras GET /auth/me
const { permissions, is_admin } = authMe;

// Menú equipo
{is_admin && <NavLink to="/equipo">Empleados</NavLink>}

// Botón con permiso explícito
{can(permissions, "orders.write") && (
  <Button onClick={crearPedido}>Nuevo pedido</Button>
)}
```

Hook sugerido:

```typescript
function usePermission(permission: string): boolean {
  const { permissions } = useAuth();
  return permissions.includes(permission);
}
```

---

## Crear empleados (admin)

1. `GET /ConsultarRol` → listar roles asignables (**no** ofrecer Propietario en el select)
2. `POST /IngresarUsuario` con `ID_Rol` de Mesero, Cocinero, Cajero o Administrador
3. Si el usuario actual no es admin → **403** antes de llegar a BD

---

## Errores

| HTTP | `detail` | UI |
|------|----------|-----|
| 403 | `Permiso requerido: orders.write` | Acción no permitida para tu rol |
| 403 | `Requiere rol Propietario o Administrador` | Solo admins gestionan equipo |
| 403 | `No puede asignar el rol Propietario...` | Quitar Propietario del selector |

---

## Checklist frontend

- [ ] Tras login → `GET /auth/me` y guardar `permissions` + `is_admin`
- [ ] Rutas protegidas por permiso (no solo por `kind === "user"`)
- [ ] Selector de rol al crear empleado **sin** Propietario
- [ ] Manejo global de 403 con mensaje del `detail`
- [ ] Opcional: precargar matriz con `GET /auth/roles/permissions` en settings/ayuda

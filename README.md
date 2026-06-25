# bytte OS Backend

Bytte es un ERP para restaurantes. Este documento explica cómo montar y utilizar el servidor backend de Bytte OS.

## Requisitos

- Python (versión 3.8 o superior)
- Base de datos **PostgreSQL** (recomendado: [Supabase](https://supabase.com/))

## Variables de entorno

Crea un archivo `.env` a partir de [`.env.example`](.env.example):

- **`DATABASE_URL`**: URI `postgresql://...` desde Supabase → **Project Settings** → **Database** → **Connection string** (modo *URI*, no la URL `https://` del proyecto).
- **`DB_HOST`, `DB_PASSWORD`, …`**: si `DATABASE_URL` da *password authentication failed*, usa las variables sueltas en `.env` (ver [`.env.example`](.env.example)); **tienen prioridad** sobre `DATABASE_URL` y evitan problemas al codificar la contraseña en la URI.
- **IPv4**: el host directo `db.<ref>.supabase.co:5432` a veces no es compatible con redes solo IPv4. En ese caso usa **Session pooler** (puerto **6543**, otro host) en la URI o en `DB_HOST`/`DB_PORT`.
- **`FRONT_URL`**: origen permitido en CORS (ej. `http://localhost:3000` en desarrollo).
- **`JWT_SECRET`**: clave para firmar tokens (obligatorio en producción; usa una cadena larga y aleatoria). Ver [`.env.example`](.env.example).
- **`JWT_EXPIRE_MINUTES`**: opcional; minutos de validez del access token (por defecto 480).

Opcional: `CHECK_DB_ON_IMPORT=1` para comprobar la BD al cargar el módulo `Database` (por defecto desactivado).

Herramienta opcional para el IDE: `npx skills add supabase/agent-skills` (no es dependencia del servidor).

## Instalación

1. Clona el repositorio:

```bash
    git clone https://github.com/tu-usuario/bytte-backend.git
    cd bytte-backend
```

2. Crea y activa un entorno virtual:

```bash
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
```

3. Instala las dependencias:

```bash
    pip install -r requirements.txt
```

4. Copia `.env.example` a `.env` y define `DATABASE_URL` con tu proyecto Supabase.

## Uso

1. Inicia el servidor:

```bash
    uvicorn Application.ApiBytte:app --reload
```

2. Por defecto Uvicorn usa el puerto **8000** (`http://localhost:8000`). Documentación interactiva: `http://localhost:8000/docs`.
3. **`GET /health`** (sin prefijo): `{"status":"ok","database":"ok"|"error"}` para comprobar proceso y disponibilidad de BD.

Equivalente al entrypoint de Vercel:

```bash
uvicorn index:app --reload --port 8000
```

## Despliegue en Vercel

Ver guía completa: [`docs/VERCEL_DEPLOY.md`](docs/VERCEL_DEPLOY.md).

Resumen:

```bash
vercel link
vercel --prod
```

Variables obligatorias en el dashboard: `DATABASE_URL` (pooler `:6543`), `JWT_SECRET`, `FRONT_URL`, `SUPABASE_*`.

## Rutas (`/api/v1`)

Todos los endpoints de negocio y autenticación REST están bajo el prefijo **`/api/v1`** (ej. `GET /api/v1/ConsultarRestaurante`, `POST /api/v1/auth/login`). El monitoreo usa **`GET /health`** en la raíz.

## Autenticación (JWT)

- **Login (público):** `POST /api/v1/auth/login` con cuerpo JSON `{"correo": "...", "contrasena": "..."}`. Límite de peticiones por IP (SlowAPI).
- **Respuesta:** incluye `access_token`, `token_type` (`bearer`), `kind` (`user` o `super`) y, si aplica, `restaurant_id` del empleado.
- **Resto de rutas:** requieren cabecera `Authorization: Bearer <access_token>` salvo `POST /api/v1/auth/login`, `POST /api/v1/auth/registro/restaurante` y `GET /health`.
- **Refresh:** no hay endpoint de refresh; al expirar el token hay que iniciar sesión de nuevo (`JWT_EXPIRE_MINUTES`).
- **`JWT_SECRET`:** en producción usar cadena larga y aleatoria y rotarla desde un secret manager; al cambiar sólo el secreto, las sesiones anteriores dejan de valer salvo proceso de convivencia de dos claves.
- **Roles:**
  - **`user`**: usuario de restaurante; los datos de reservas, pedidos, pagos y empleados se limitan al `id_restaurante` del token.
  - **`super`**: puede crear/editar/borrar restaurantes, gestionar superusuarios y catálogos globales (rol, ubicación, categorías, etiquetas) en escritura; ve todos los datos donde la API no filtra por tenant.

En Swagger UI, usa **Authorize** y pega el token como `Bearer <token>` (o solo el token, según el cliente).

### Cuentas de ejemplo (tras ejecutar [`scripts/seed_database.sql`](scripts/seed_database.sql))

| Rol | Correo | Contraseña (demo) |
|-----|--------|-------------------|
| Empleado (restaurante Bogotá) | `carlos.ruiz@bytte.demo` | `hash_demo_u1` |
| Empleado (restaurante Medellín) | `diana.perez@bytte.demo` | `hash_demo_u2` |
| Superusuario | `admin@bytte.os` | `hash_super_demo` |

El seed usa contraseñas en texto plano con prefijo `hash_` solo para pruebas. En producción conviene guardar **bcrypt** (la API hashea contraseñas nuevas o actualizadas que no vengan ya como hash `$2…`).

## Endpoints (resumen)

Las rutas siguen los nombres expuestos en la app con prefijo **`/api/v1`** (por ejemplo `GET /api/v1/ConsultarRestaurante`, `POST /api/v1/IngresarReserva`). Varias listas (`ConsultarReserva`, `ConsultarPedido`, `ConsultarCalificacionRestaurante`) devuelven **`items`, `total`, `limit`, `offset`**. Para el panel del empleado existe `GET /api/v1/restaurantes/mi`. La lista completa está en `/docs`.

## Migraciones Alembic

Si la base ya tiene el esquema aplicado manualmente, tras instalar dependencias:

```bash
alembic stamp baseline001
alembic upgrade head
```

Las revisiones pueden contener SQL crudo (`op.execute`), por ejemplo sincronización de columnas visibles desde tablas hijas (`tr_sync_01`). La URL se toma de las mismas variables que `Infraestructure/Database.py` (`DATABASE_URL` o `DB_*`).

## Tests

```bash
pip install -r requirements-dev.txt
pytest -m "not integration"    # Sin depender de PostgreSQL
pytest                          # Incluye pruebas de integración si hay DATABASE_URL / DB_* en entorno
```

## Contribuir

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -am 'Añadir nueva funcionalidad'`).
4. Sube tus cambios (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.

## Licencia

Este proyecto está bajo la Licencia MIT.

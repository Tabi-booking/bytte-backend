# Despliegue en Vercel

Guía para publicar **bytte-backend** (FastAPI) como función serverless en [Vercel](https://vercel.com).

---

## Requisitos

- Cuenta Vercel + [Vercel CLI](https://vercel.com/docs/cli) (`npm i -g vercel`)
- Proyecto Supabase con **Session pooler** (puerto **6543**) — obligatorio en serverless
- Front desplegado (Vercel u otro) para configurar CORS

---

## Archivos del repo

| Archivo | Rol |
|---------|-----|
| `Application/ApiBytte.py` | App FastAPI (`app`) — entrypoint Vercel vía `pyproject.toml` |
| `index.py` | Alias local: `uvicorn index:app --reload` |
| `vercel.json` | Solo `installCommand` (sin bloque `functions`) |
| `vercel.json` | `maxDuration` 30s, install con `requirements.txt` |
| `pyproject.toml` | Python ≥3.12, `tool.vercel.entrypoint` |
| `.vercelignore` | Excluye tests, venv, docs del bundle |

---

## Variables de entorno (Vercel → Project → Settings → Environment Variables)

Configúralas en **Production** (y Preview si aplica):

| Variable | Obligatoria | Notas |
|----------|-------------|--------|
| `DATABASE_URL` | Sí* | URI del **Session pooler** Supabase (`:6543`) |
| `DB_HOST` + `DB_PASSWORD` | Sí* | Alternativa a `DATABASE_URL` (tiene prioridad) |
| `DB_PORT` | Recomendado | `6543` con pooler |
| `DB_CONNECT_TIMEOUT_SEC` | Recomendado | `15` en serverless |
| `JWT_SECRET` | Sí | Cadena larga y aleatoria |
| `FRONT_URL` | Sí | URL del front, ej. `https://restaurante.tabiapp.tech` |
| `SUPABASE_URL` | Sí (uploads) | URL del proyecto Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | Sí (uploads) | Service role (solo backend) |
| `STORAGE_BUCKET` | Sí (uploads) | `restaurant-documents` |

\* Una de las dos formas de conexión a PostgreSQL.

### CORS

`FRONT_URL` puede llevar **varios orígenes separados por coma**:

```env
FRONT_URL=http://localhost:3000,https://tabi-front.vercel.app
```

En despliegues Vercel, también se aceptan automáticamente `VERCEL_URL` y `VERCEL_BRANCH_URL` (previews).

---

## Desplegar

```bash
# Desde la raíz del repo
vercel login
vercel link          # primera vez: vincula proyecto
vercel env pull .env.vercel.local   # opcional: revisar vars localmente

vercel               # preview
vercel --prod        # producción
```

Tras el deploy, la API queda en:

- `https://<tu-proyecto>.vercel.app/health`
- `https://<tu-proyecto>.vercel.app/api/v1/auth/login`
- `https://<tu-proyecto>.vercel.app/docs`

En el front, define la base URL del API, por ejemplo:

```env
NEXT_PUBLIC_API_URL=https://<tu-proyecto>.vercel.app
```

---

## Comprobar

```bash
curl https://<tu-proyecto>.vercel.app/health
# {"status":"ok","database":"ok"}

curl -X POST https://<tu-proyecto>.vercel.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"correo":"...","contrasena":"..."}'
```

Si `database` es `"error"`: revisa `DATABASE_URL`/pooler y variables en el dashboard de Vercel.

---

## Limitaciones serverless

1. **Sin estado en memoria** — el rate limit (SlowAPI) no es fiable entre instancias; en producción conviene Redis o límites en el edge más adelante.
2. **Cold starts** — primera petición puede tardar más; usa pooler Supabase y `DB_CONNECT_TIMEOUT_SEC=15`.
3. **Migraciones Alembic** — ejecútalas desde tu máquina o CI contra la misma BD, no en Vercel:
   ```bash
   alembic upgrade head
   ```
4. **Tamaño** — dependencias deben caber en el límite de función Vercel (~250–500 MB según plan).

---

## Desarrollo local (mismo entrypoint que Vercel)

```bash
pip install -r requirements.txt
uvicorn index:app --reload --port 8000
```

Tests (requieren `requirements-dev.txt`):

```bash
pip install -r requirements-dev.txt
pytest -m "not integration"
```

---

## Solución de problemas

### Error exacto: `Cannot assign requested address` / `db.*.supabase.co` puerto 5432

En los logs de Vercel verás algo como:

```text
psycopg2.OperationalError: connection to server at "db.bakkcbqdcuktgmzztxcr.supabase.co"
(2600:1f14:...) port 5432 failed: Cannot assign requested address
```

**Causa:** la función serverless intenta la conexión **directa** a Supabase (IPv6, puerto 5432). Vercel no puede usar ese endpoint de forma fiable.

**Solución (Vercel → Project → Settings → Environment Variables → Production):**

1. Abre [Supabase Dashboard](https://supabase.com/dashboard) → tu proyecto → **Database** → **Connection string**.
2. Elige **Session pooler** (no *Direct connection*).
3. Copia la URI (host tipo `aws-0-<region>.pooler.supabase.com`, puerto **6543**, usuario `postgres.<project_ref>`).

**Opción A — solo `DATABASE_URL` (recomendado):**

```env
DATABASE_URL=postgresql://postgres.bakkcbqdcuktgmzztxcr:TU_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
```

Elimina o deja vacías `DB_HOST` y `DB_PASSWORD` si existen: **tienen prioridad** sobre `DATABASE_URL`.

**Opción B — variables `DB_*`:**

```env
DB_HOST=aws-0-us-east-1.pooler.supabase.com
DB_PORT=6543
DB_USER=postgres.bakkcbqdcuktgmzztxcr
DB_PASSWORD=TU_PASSWORD
DB_NAME=postgres
DB_SSLMODE=require
DB_CONNECT_TIMEOUT_SEC=15
```

4. **Redeploy** (Deployments → ⋮ → Redeploy) para que las funciones carguen las nuevas vars.
5. Comprueba: `curl https://bytte-backend.vercel.app/health` → `"database":"ok"`.

| Síntoma | Acción |
|---------|--------|
| CORS bloqueado | `FRONT_URL` debe coincidir exactamente con el `Origin` del navegador |
| 503 base de datos | Usar Session pooler `:6543`, no host directo `:5432` |
| 401 en rutas protegidas | Token JWT válido; re-login tras rotar `JWT_SECRET` |
| Build falla con `functions` / `api/index.py` | No uses bloque `functions` en `vercel.json`; el entrypoint es `Application.ApiBytte:app` en `pyproject.toml` |
| Timeout en cold start | Dashboard → Functions → **Max Duration** 30s; `DB_CONNECT_TIMEOUT_SEC=15` |

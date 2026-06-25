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
| `api/index.py` | Entrada ASGI que Vercel detecta (`app`) |
| `index.py` | Alias local: `uvicorn index:app --reload` |
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
| `FRONT_URL` | Sí | URL del front, ej. `https://tu-app.vercel.app` |
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

| Síntoma | Acción |
|---------|--------|
| CORS bloqueado | `FRONT_URL` debe coincidir exactamente con el `Origin` del navegador |
| 503 base de datos | Usar Session pooler `:6543`, no host directo `:5432` |
| 401 en rutas protegidas | Token JWT válido; re-login tras rotar `JWT_SECRET` |
| Build falla en Python | `requires-python >=3.12` en `pyproject.toml` |

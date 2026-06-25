"""Mensajes de ayuda cuando falla la conexión PostgreSQL (p. ej. en Vercel)."""

from __future__ import annotations


def hint_for_operational_error(exc: BaseException) -> str | None:
    msg = str(exc).lower()
    if "cannot assign requested address" in msg or "2600:" in msg:
        return (
            "Vercel no alcanza el host directo db.<ref>.supabase.co:5432 (IPv6). "
            "En Vercel → Environment Variables usa el **Session pooler** de Supabase "
            "(puerto 6543): Dashboard → Database → Connection string → Session pooler."
        )
    if "db." in msg and "supabase.co" in msg and ":5432" in msg:
        return (
            "Estás usando la conexión directa :5432. En serverless configura el "
            "Session pooler Supabase (puerto 6543)."
        )
    if "timeout expired" in msg or "timed out" in msg:
        return (
            "Timeout de BD. Usa Session pooler (:6543), sube DB_CONNECT_TIMEOUT_SEC=15 "
            "y verifica DB_HOST/DB_PASSWORD o DATABASE_URL en Vercel."
        )
    return None

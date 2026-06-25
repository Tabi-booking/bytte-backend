"""Utilidades HTTP para coexistencia modelo legacy `resultado` vs códigos HTTP."""

from typing import Any

from fastapi import HTTPException


def raise_if_resultado_fallido(obj: Any, attr: str = "resultado") -> None:
    """Si el modelo trae '... Fallido' en resultado, lanza HTTPException."""
    r = getattr(obj, attr, None) or ""
    if isinstance(r, str) and "Fallido" in r:
        raise HTTPException(status_code=400, detail=r.strip())


def return_or_raise_legacy(obj: Any, attr: str = "resultado") -> Any:
    """Útil encadenando: valida resultado y devuelve el mismo objeto."""
    raise_if_resultado_fallido(obj, attr)
    return obj

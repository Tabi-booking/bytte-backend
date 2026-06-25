"""Traducción onboarding_estado API ↔ BD y utilidades JSONB paso_N."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

ESTADO_BD_TO_API = {
    "borrador": "draft",
    "enviado": "submitted",
    "aprobado": "approved",
    "rechazado": "rejected",
}

ESTADO_API_TO_BD = {v: k for k, v in ESTADO_BD_TO_API.items()}


def estado_bd_a_api(valor: Optional[str]) -> Optional[str]:
    if not valor:
        return None
    return ESTADO_BD_TO_API.get(str(valor).strip().lower(), str(valor).strip().lower())


def estado_api_a_bd(valor: Optional[str]) -> Optional[str]:
    if not valor:
        return None
    v = str(valor).strip().lower()
    return ESTADO_API_TO_BD.get(v, v)


def parse_onboarding_datos(raw: Any) -> Dict[str, Any]:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def get_paso(datos: Dict[str, Any], n: int) -> Dict[str, Any]:
    key = f"paso_{n}"
    block = datos.get(key)
    return block if isinstance(block, dict) else {}


def merge_paso(datos: Dict[str, Any], n: int, patch: Dict[str, Any]) -> Dict[str, Any]:
    """Devuelve copia de datos con paso_N reemplazado (merge superficial del paso)."""
    out = dict(datos)
    key = f"paso_{n}"
    current = get_paso(out, n)
    merged = {**current, **{k: v for k, v in patch.items() if v is not None}}
    out[key] = merged
    return out


def onboarding_datos_to_json(datos: Dict[str, Any]) -> str:
    return json.dumps(datos, ensure_ascii=False)

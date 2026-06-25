"""Manejo centralizado de errores HTTP y de base de datos."""

import logging
from json import JSONDecodeError

import psycopg2
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from Infraestructure.exceptions import ConfigurationError
from Application.db_connection_hint import hint_for_operational_error

logger = logging.getLogger("bytte.api")


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "error_type": "http"},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": exc.errors(), "error_type": "validation"},
        )

    @app.exception_handler(JSONDecodeError)
    async def json_decode_exception_handler(_request: Request, _exc: JSONDecodeError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "detail": "JSON decode error. Please check your request body.",
                "error_type": "json_decode",
            },
        )

    @app.exception_handler(ConfigurationError)
    async def configuration_error(_request: Request, exc: ConfigurationError) -> JSONResponse:
        logger.error("Configuración: %s", exc)
        return JSONResponse(
            status_code=503,
            content={"detail": str(exc), "error_type": "configuration"},
        )

    async def db_connection_error(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Error de conexión a la base de datos")
        hint = hint_for_operational_error(exc)
        detail = "No se pudo conectar con la base de datos."
        if hint:
            detail = f"{detail} {hint}"
        payload: dict[str, str] = {
            "detail": detail,
            "error_type": "database_connection",
        }
        if hint:
            payload["hint"] = hint
        return JSONResponse(status_code=503, content=payload)

    app.add_exception_handler(psycopg2.OperationalError, db_connection_error)
    app.add_exception_handler(psycopg2.InterfaceError, db_connection_error)

    @app.exception_handler(psycopg2.IntegrityError)
    async def db_integrity(_request: Request, exc: psycopg2.IntegrityError) -> JSONResponse:
        logger.warning("Restricción de integridad: %s", exc)
        return JSONResponse(
            status_code=409,
            content={
                "detail": "Los datos violan una restricción de integridad en la base de datos.",
                "error_type": "database_integrity",
            },
        )

    @app.exception_handler(psycopg2.ProgrammingError)
    async def db_programming(_request: Request, exc: psycopg2.ProgrammingError) -> JSONResponse:
        logger.exception("Error SQL / programación: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Error en la consulta a la base de datos.",
                "error_type": "database_programming",
            },
        )

    @app.exception_handler(psycopg2.Error)
    async def db_generic(_request: Request, exc: psycopg2.Error) -> JSONResponse:
        logger.exception("Error PostgreSQL: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Error al procesar la operación en la base de datos.",
                "error_type": "database",
            },
        )

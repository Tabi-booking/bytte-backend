"""Errores de dominio / persistencia para elevar hasta HTTP desde las rutas."""


class DomainError(Exception):
    """Base para errores recuperables que deben traducirse a HTTP."""

    status_code = 400

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class ConflictError(DomainError):
    status_code = 409


class NotFoundError(DomainError):
    status_code = 404


class ForbiddenError(DomainError):
    status_code = 403

import os

import pytest
from starlette.testclient import TestClient

from Application.ApiBytte import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def db_configured() -> bool:
    return bool(os.getenv("DATABASE_URL") or (os.getenv("DB_HOST") and os.getenv("DB_PASSWORD")))


@pytest.fixture
def integration_db() -> None:
    """PostgreSQL configurado **y** alcanzable (salta si no aplica)."""
    if not db_configured():
        pytest.skip("Variables DATABASE_URL o DB_HOST+DB_PASSWORD no definidas")
    from Infraestructure.Database import ping_db

    if not ping_db():
        pytest.skip("PostgreSQL no alcanzable desde este entorno (ping_db falló)")

"""Alembic runtime: URLs desde las mismas variables que `Infraestructure/Database.py`."""

from __future__ import annotations

import os
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import URL

_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env", override=True)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def get_sqlalchemy_url() -> str:
    host = os.getenv("DB_HOST")
    password = os.getenv("DB_PASSWORD")
    if host and password:
        port = int(os.getenv("DB_PORT", "5432"))
        user = os.getenv("DB_USER", "postgres")
        dbname = os.getenv("DB_NAME", "postgres")
        sslmode = os.getenv("DB_SSLMODE", "require")
        u = URL.create(
            "postgresql+psycopg2",
            username=user,
            password=password,
            host=host,
            port=port,
            database=dbname,
            query={"sslmode": sslmode},
        )
        return u.render_as_string(hide_password=False)

    url = os.getenv("DATABASE_URL")
    if not url or not url.strip():
        raise RuntimeError(
            "Alembic: define DB_HOST y DB_PASSWORD, o DATABASE_URL (véase .env.example)"
        )
    url = url.strip()
    if url.startswith("postgresql://") and "+" not in url.split("://", 1)[0]:
        rest = url.split("://", 1)[1]
        url = "postgresql+psycopg2://" + rest
    return url


def run_migrations_online() -> None:
    ini_section = config.get_section(config.config_ini_section, {})
    ini_section["sqlalchemy.url"] = get_sqlalchemy_url()
    connectable = engine_from_config(
        ini_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


def run_migrations_offline() -> None:
    context.configure(url=get_sqlalchemy_url(), literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

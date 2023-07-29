import asyncio
import os
import traceback
from pathlib import Path
from importlib import import_module
from logging.config import fileConfig
from typing import Iterator

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import SQLModel

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
alembic_cfg = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if alembic_cfg.config_file_name is not None:
    fileConfig(alembic_cfg.config_file_name)  # skipcq: PY-A6006


def scan_models() -> Iterator[str]:
    """扫描 models/models 目录下所有 *.py 文件"""
    models_path = Path("models/models")
    for path in list(models_path.glob("*.py")):
        yield str(path.with_suffix("")).replace(os.sep, ".")


def import_models():
    """导入我们所有的 models，使 alembic 可以自动对比 db scheme 创建 migration revision"""
    for pkg in scan_models():
        print("Importing models from %s" % pkg)
        try:
            import_module(pkg)  # 导入 models
        except Exception:  # pylint: disable=W0703
            traceback.print_exc()
            print("Error importing models from %s" % pkg)


# register our models for alembic to auto-generate migrations
import_models()

target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# here we allow ourselves to pass interpolation vars to alembic.ini
# from the application config module

sqlalchemy_url = alembic_cfg.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = alembic_cfg.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = AsyncEngine(
        engine_from_config(
            alembic_cfg.get_section(alembic_cfg.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

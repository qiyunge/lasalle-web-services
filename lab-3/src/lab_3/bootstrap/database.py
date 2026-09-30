from pathlib import Path

from lab_3.adapters.outbound.sqlite.connection import SqliteConnectionFactory

_LAB_ROOT = Path(__file__).resolve().parents[3]


def bootstrap_database() -> SqliteConnectionFactory:
    connection_factory = SqliteConnectionFactory(_LAB_ROOT / "ecole.db")
    connection_factory.initialize_database()
    return connection_factory

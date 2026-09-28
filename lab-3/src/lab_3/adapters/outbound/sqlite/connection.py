import sqlite3
from pathlib import Path

def create_connection(database_file: str) -> sqlite3.Connection:
    connection = sqlite3.connect(database_file)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(connection: sqlite3.Connection)->None:
    schema_path = Path(__file__).parent / "schema.sql"
    schema = schema_path.read_text(encoding="utf-8")

    connection.executescript(schema)
    connection.commit()

class SqliteConnectionFactory:
    def __init__(self, database_file: str|Path):
        self._database_file = str(database_file)

    def create_connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_file)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.row_factory = sqlite3.Row
        return connection

    def initialize_database(self) -> None:
        schema_path = Path(__file__).parent / "schema.sql"
        schema = schema_path.read_text(encoding="utf-8")
        connection = self.create_connection()
        try:
            connection.executescript(schema)
            connection.commit()
        except Exception as e:
            connection.rollback()
            raise 
        finally:
            connection.close()


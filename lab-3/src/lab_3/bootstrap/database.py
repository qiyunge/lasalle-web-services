import sqlite3
from lab_3.adapters.outbound.sqlite.connection import SqliteConnectionFactory

def bootstrap_database()->SqliteConnectionFactory:
    connection_factory = SqliteConnectionFactory("ecloe.db")
    connection_factory.initialize_database()
    return connection_factory
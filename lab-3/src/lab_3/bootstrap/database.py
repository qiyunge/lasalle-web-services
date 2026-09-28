import sqlite3
from lab_3.adapters.outbound.sqlite.connection import create_connection

def bootstrap_database()->sqlite3.Connection:
    connection = create_connection("ecloe.db")
    return connection
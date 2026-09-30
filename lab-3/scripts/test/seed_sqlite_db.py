import pathlib
import sqlite3

root = pathlib.Path(__file__).resolve().parents[2]
db_path = root / "lab-3" / "ecole.db"
seed_path = root / "scripts/test" / "seed.sql"


if db_path.exists():
    db_path.unlink()

connection = sqlite3.connect(db_path)
try:
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(seed_path.read_text(encoding="utf-8"))
    connection.commit()
finally:
    connection.close()

try:
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM PROGRAMMES")
    print(cursor.fetchall())
finally:
    connection.close()

import sqlite3

from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4


class SQLiteConversationStore:
    def __init__(self, db_path: str = "data/conversations.db"):
        self.db_path = db_path

        Path(db_path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        try:
            conn.execute("PRAGMA foreign_keys = ON")

            with conn:
                yield conn
        finally:
            conn.close()

    def _initialize(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (conversation_id)
                        REFERENCES conversations(id)
                        ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_messages_conversation
                ON messages(conversation_id, id);
            """)

    def create(self) -> str:
        conversation_id = str(uuid4())

        with self._connect() as conn:
            conn.execute(
                "INSERT INTO conversations (id) VALUES (?)",
                (conversation_id,),
            )

        return conversation_id

    def exists(self, conversation_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT 1 FROM conversations
                WHERE id = ?
                """,
                (conversation_id,),
            ).fetchone()

        return row is not None

    def get(self, conversation_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT role, content
                FROM messages
                WHERE conversation_id = ?
                ORDER BY id
                """,
                (conversation_id,),
            ).fetchall()

        return [dict(row) for row in rows]

    def append(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO messages (
                    conversation_id, role, content
                )
                VALUES (?, ?, ?)
                """,
                (conversation_id, role, content),
            )
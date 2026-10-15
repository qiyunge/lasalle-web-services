"""Course storage. Reads the course table only."""

import sqlite3

from college.domain.course import Course


class SqliteCourseRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def get(self, course_id: int) -> Course | None:
        row = self.connection.execute(
            "SELECT id, course_code, name FROM course WHERE id = ?",
            (course_id,),
        ).fetchone()
        if row is None:
            return None
        return Course(row["id"], row["course_code"], row["name"])

    def list_all(self) -> list[Course]:
        rows = self.connection.execute(
            "SELECT id, course_code, name FROM course"
        ).fetchall()
        return [Course(row["id"], row["course_code"], row["name"]) for row in rows]

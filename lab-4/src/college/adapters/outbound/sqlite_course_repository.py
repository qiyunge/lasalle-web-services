"""Course storage. Reads the course table only."""

import sqlite3

from college.application.ports import CourseList, Missing
from college.domain.course import Course
from college.domain.result import Failure, Success


class SqliteCourseRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def get(self, course_id: int):
        row = self.connection.execute(
            "SELECT id, course_code, name FROM course WHERE id = ?",
            (course_id,),
        ).fetchone()
        if row is None:
            return Failure(Missing())
        return Course.create(row["id"], row["course_code"], row["name"])

    def list_all(self) -> CourseList:
        rows = self.connection.execute(
            "SELECT id, course_code, name FROM course"
        ).fetchall()
        courses = []
        invalid = []
        for row in rows:
            result = Course.create(row["id"], row["course_code"], row["name"])
            if isinstance(result, Success):
                courses.append(result.value)
            else:
                invalid.append(result.error)
        return CourseList(tuple(courses), tuple(invalid))

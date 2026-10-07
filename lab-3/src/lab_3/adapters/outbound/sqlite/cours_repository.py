from __future__ import annotations

import sqlite3

from lab_3.adapters.outbound.sqlite.unit_of_work import SqliteConnectionProvider
from lab_3.core.application.ports.outbound.cours_repository import (
    CreateCoursCodeAlreadyExistsPersistenceError,
    CreateCoursIdConflictPersistenceError,
    CreateCoursPersistenceResult,
    GetCoursNotFoundPersistenceError,
    GetCoursPersistenceResult,
)
from lab_3.core.domain import Cours
from lab_3.core.domain.common import Failure, Success, collect_errors
from lab_3.core.domain.value_objects import CoursCode, CoursId, CoursName


class SqliteCoursRepository:
    def __init__(self, connections: SqliteConnectionProvider) -> None:
        self._connections = connections

    def exists(self, id: CoursId) -> bool:
        cursor = self._connections.execute(
            "SELECT 1 FROM COURS WHERE id = ? LIMIT 1",
            (id.value,),
        )
        return cursor.fetchone() is not None

    def find_by_id(self, id: CoursId) -> GetCoursPersistenceResult:
        cursor = self._connections.execute(
            "SELECT id, code, name FROM COURS WHERE id = ?",
            (id.value,),
        )
        row = cursor.fetchone()
        if row is None:
            return Failure(GetCoursNotFoundPersistenceError(id))
        return Success(_cours_from_row(row))

    def find_all(self, offset: int, limit: int) -> tuple[Cours, ...]:
        cursor = self._connections.execute(
            "SELECT id, code, name FROM COURS ORDER BY id LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return tuple(_cours_from_row(row) for row in cursor.fetchall())

    def save(self, cours: Cours) -> CreateCoursPersistenceResult:
        try:
            self._connections.execute(
                "INSERT INTO COURS (id, code, name) VALUES (?, ?, ?)",
                (cours.id.value, cours.code.value, cours.name.value),
            )
            return Success(cours)
        except sqlite3.IntegrityError as error:
            message = str(error)
            if "COURS.id" in message:
                return Failure(CreateCoursIdConflictPersistenceError(cours.code))
            if "COURS.code" in message:
                return Failure(CreateCoursCodeAlreadyExistsPersistenceError(cours.code))
            raise


def _cours_from_row(row: sqlite3.Row) -> Cours:
    id_result = CoursId.create(row["id"])
    code_result = CoursCode.create(row["code"])
    name_result = CoursName.create(row["name"])
    if collect_errors(id_result, code_result, name_result):
        raise RuntimeError("Invalid cours data in persistence")
    assert isinstance(id_result, Success)
    assert isinstance(code_result, Success)
    assert isinstance(name_result, Success)
    return Cours.restore(id_result.outcome, code_result.outcome, name_result.outcome)

from __future__ import annotations

import sqlite3

from lab_3.adapters.outbound.sqlite.unit_of_work import SqliteConnectionProvider
from lab_3.core.application.ports.outbound.inscription_repository import (
    InscriptionDuplicate,
    InscriptionIdConflict,
    SaveInscriptionError,
)
from lab_3.core.domain.common import Failure, Result, Success
from lab_3.core.domain.inscription import Inscription
from lab_3.core.domain.value_objects import CoursId, StudentId


class SqliteInscriptionRepository:
    def __init__(self, connections: SqliteConnectionProvider) -> None:
        self._connections = connections

    def exists(self, student_id: StudentId, cours_id: CoursId) -> bool:
        cursor = self._connections.execute(
            "SELECT 1 FROM INSCRIPTIONS WHERE student_id = ? AND cours_id = ? LIMIT 1",
            (student_id.value, cours_id.value),
        )
        return cursor.fetchone() is not None

    def save(
        self, inscription: Inscription
    ) -> Result[Inscription, SaveInscriptionError]:
        if inscription.id is None:
            raise RuntimeError("Inscription id is required")
        inscription_id = inscription.id

        try:
            self._connections.execute(
                "INSERT INTO INSCRIPTIONS (id, student_id, cours_id, note) VALUES (?, ?, ?, ?)",
                (
                    inscription_id.value,
                    inscription.student_id.value,
                    inscription.cours_id.value,
                    inscription.note.value if inscription.note is not None else None,
                ),
            )
            return Success(inscription)
        except sqlite3.IntegrityError as error:
            return Failure(_save_conflict(error, inscription))


def _save_conflict(
    error: sqlite3.IntegrityError, inscription: Inscription
) -> SaveInscriptionError:
    if inscription.id is None:
        raise RuntimeError("Inscription id is required")
    constraint = _unique_constraint(error)
    if constraint == "INSCRIPTIONS.id":
        raise InscriptionIdConflict(inscription.id)
    if constraint == "INSCRIPTIONS.student_id, INSCRIPTIONS.cours_id":
        return InscriptionDuplicate(inscription.student_id, inscription.cours_id)
    raise error


def _unique_constraint(error: sqlite3.IntegrityError) -> str | None:
    prefix = "UNIQUE constraint failed: "
    message = str(error)
    if prefix not in message:
        return None
    return message.split(prefix, 1)[1]

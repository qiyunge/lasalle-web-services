from __future__ import annotations

import sqlite3

from lab_3.core.domain.value_objects import StudentId, CoursId, InscriptionId
from lab_3.core.domain.inscription import Inscription
from lab_3.core.domain.common import Result, Success, Failure
from lab_3.core.application.ports.outbound.inscription_repository import InscriptionConflict

class SqliteInscriptionRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def exists(self, student_id: StudentId, course_id: CoursId) -> bool:
        cursor = self._connection.cursor()
        cursor.execute("SELECT 1 FROM INSCRIPTIONS WHERE student_id = ? AND course_id = ? LIMIT 1", 
            (student_id.value, course_id.value))
        return cursor.fetchone() is not None

    def save(self, inscription: Inscription) -> Result[Inscription, InscriptionConflict]:

        try:
            cursor = self._connection.cursor()
            cursor.execute("INSERT INTO INSCRIPTIONS (student_id, course_id, note) VALUES (?, ?, ?) RETURNING id", 
                (inscription.student_id.value, inscription.cours_id.value, inscription.note.value if inscription.note else None))
            self._connection.commit()

            row = cursor.fetchone()
            new_inscription_id_result = InscriptionId.create(row["id"])
            if isinstance(new_inscription_id_result, Failure):
                raise RuntimeError("SQLite generated an invalid inscription ID")

            saved_inscription = Inscription.restore(
                id=new_inscription_id_result.value,
                student_id=inscription.student_id,
                cours_id=inscription.cours_id,
                note=inscription.note
            )
            return Success(saved_inscription)
           
            
        except sqlite3.IntegrityError as e:
            if self._is_duplicate_key_error(e):
                return Failure(InscriptionConflict(student_id=inscription.student_id, course_id=inscription.cours_id))  
            raise 

    @staticmethod
    def _is_duplicate_key_error(
        error: sqlite3.IntegrityError,
    ) -> bool:
        return "UNIQUE constraint failed" in str(error)
       
from __future__ import annotations

import sqlite3

from lab_3.core.domain.value_objects import StudentId, CoursId, InscriptionId
from lab_3.core.domain.inscription import Inscription
from lab_3.core.domain.common import Result, Success, Failure
from lab_3.core.application.ports.outbound.inscription_repository import InscriptionConflict
from lab_3.adapters.outbound.sqlite.connection import SqliteConnectionFactory

class SqliteInscriptionRepository:
    def __init__(self, connection_factory: SqliteConnectionFactory):
        self._connection_factory = connection_factory

    def exists(self, student_id: StudentId, course_id: CoursId) -> bool:
        connection = self._connection_factory.create_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1 FROM INSCRIPTIONS WHERE student_id = ? AND course_id = ? LIMIT 1", 
                (student_id.value, course_id.value))
            return cursor.fetchone() is not None
        finally:
            connection.close()

    def save(self, inscription: Inscription) -> Result[Inscription, InscriptionConflict]:
        connection = self._connection_factory.create_connection()
        try:
           
            cursor = connection.cursor()
            cursor.execute("INSERT INTO INSCRIPTIONS (student_id, course_id, note) VALUES (?, ?, ?) RETURNING id", 
                (inscription.student_id.value, inscription.cours_id.value, inscription.note.value if inscription.note is not None else None))
            
            row = cursor.fetchone()
            if row is None:
                raise RuntimeError("SQLite generated an invalid inscription ID")

            

            new_inscription_id_result = InscriptionId.create(row["id"])
            if isinstance(new_inscription_id_result, Failure):
                raise RuntimeError("SQLite generated an invalid inscription ID")
            
            connection.commit()
            return Success(Inscription.restore(
                id=new_inscription_id_result.value,
                student_id=inscription.student_id,
                cours_id=inscription.cours_id,
                note=inscription.note
            ))
      
            
        except sqlite3.IntegrityError as e:
            if self._is_duplicate_key_error(e):
                return Failure(InscriptionConflict(student_id=inscription.student_id, course_id=inscription.cours_id))  
            raise 
        finally:
            connection.close()

    @staticmethod
    def _is_duplicate_key_error(
        error: sqlite3.IntegrityError,
    ) -> bool:
        return "UNIQUE constraint failed" in str(error)
       
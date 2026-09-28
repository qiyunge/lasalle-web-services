from __future__ import annotations
from lab_3.core.domain.inscription import Inscription
from lab_3.core.domain.value_objects import StudentId, CoursId, InscriptionId, Note
from lab_3.core.domain.common import Result, Success, Failure, ValidationErrors, ValidationError, collect_errors

class InscriptionFactory:
    @staticmethod
    def create_from_primitive(
                student_id: int, 
                course_id: int, 
                note: float|None=None
              ) -> Result[Inscription, ValidationErrors]:

                student_id_result = StudentId.create(student_id)
                course_id_result = CoursId.create(course_id)
                note_result= Success(None) if note is None else Note.create(note)

                errors = collect_errors(student_id_result, course_id_result, note_result)
                if errors:
                    return Failure(ValidationErrors(tuple(errors)))

                return Success(Inscription.create(student_id=student_id_result.value,
                                                               cours_id=course_id_result.value,
                                                               note=note_result.value))

    @staticmethod
    def restore_from_primitive(
                id: int,
                student_id: int,
                course_id: int,
                note: float|None=None
    ) -> Result[Inscription, ValidationErrors]:
        id_result = InscriptionId.create(id)
        student_id_result = StudentId.create(student_id)
        course_id_result = CoursId.create(course_id)
        note_result = Success(None) if note is None else Note.create(note)

        errors = collect_errors(id_result, student_id_result, course_id_result, note_result)
        if errors:
            return Failure(ValidationErrors(tuple(errors)))
        return Success(Inscription.restore(id=id_result.value,
                                           student_id=student_id_result.value,
                                           cours_id=course_id_result.value,
                                           note=note_result.value))
from __future__ import annotations

from lab_3.core.domain import Inscription
from lab_3.core.domain.factories import InscriptionFactory
from lab_3.core.domain.common import Result, Success, Failure
from lab_3.core.application.ports.inbound.create_inscription import (
    CreateInscriptionCommand, 
    CreateInscriptionResult, 
    InscriptionCreationFailed, 
    StudentNotFound, 
    CourseNotFound, 
    InscriptionAlreadyExists
)

from lab_3.core.application.ports.outbound import (
    CoursRepository,
    StudentRepository,
    InscriptionRepository
)

class CreateInscriptionHandler:
    def __init__(self, inscription_repository: InscriptionRepository, student_repository: StudentRepository, cours_repository: CoursRepository):
        self._inscription_repository = inscription_repository
        self._student_repository = student_repository
        self._cours_repository = cours_repository

    def handle(self, command: CreateInscriptionCommand) -> Result[CreateInscriptionResult, InscriptionCreationFailed]:
        creation_result = InscriptionFactory.create_from_primitive(student_id=command.student_id, 
                                                                    course_id=command.course_id)

        if isinstance(creation_result, Failure):
            return creation_result

        inscription = creation_result.value

        # application lvl checks
        if not self._student_repository.exists(command.student_id):
            return Failure(StudentNotFound(command.student_id))

        if not self._cours_repository.exists(command.course_id):
            return Failure(CourseNotFound(command.course_id))

        if self._inscription_repository.exists(command.student_id, command.course_id):
            return Failure(InscriptionAlreadyExists(command.student_id, command.course_id))
        
        # save inscription  
        saved_result = self._inscription_repository.save(inscription)
        if isinstance(saved_result, Failure):
            return saved_result

        inscription = saved_result.value
        return Success(
            CreateInscriptionResult(
                id=inscription.id.value, 
                student_id=inscription.student_id.value, 
                course_id=inscription.cours_id.value, 
                note=(inscription.note.value if inscription.note is not None else None)))
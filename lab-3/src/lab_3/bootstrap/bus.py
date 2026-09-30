from lab_3.adapters.outbound.sqlite.cours_repository import SqliteCoursRepository
from lab_3.adapters.outbound.sqlite.inscription_repository import (
    SqliteInscriptionRepository,
)
from lab_3.adapters.outbound.sqlite.student_repository import SqliteStudentRepository
from lab_3.core.application.bus import CommandBus, SimpleCommandBus
from lab_3.core.application.ports.inbound.create_inscription import (
    CreateInscriptionCommand,
)
from lab_3.core.application.ports.outbound import UnitOfWork
from lab_3.core.application.services.create_inscription import CreateInscriptionHandler


def bootstrap_command_bus(
    student_repository: SqliteStudentRepository,
    cours_repository: SqliteCoursRepository,
    inscription_repository: SqliteInscriptionRepository,
    unit_of_work: UnitOfWork,
) -> CommandBus:
    bus = SimpleCommandBus()
    bus.register(
        CreateInscriptionCommand,
        CreateInscriptionHandler(
            inscription_repository=inscription_repository,
            student_repository=student_repository,
            cours_repository=cours_repository,
            unit_of_work=unit_of_work,
        ),
    )
    return bus

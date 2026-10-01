from lab_3.core.application.bus.simple_query_bus import SimpleQueryBus
from lab_3.core.application.ports.inbound.programmes.list import (
    ProgrammeListQuery,
)
from lab_3.core.application.ports.outbound.programme_repository import ProgrammeRepository
from lab_3.core.application.ports.outbound.unit_of_work import UnitOfWork
from lab_3.core.application.services.programmes.list import ProgrammeListHandler
from lab_3.core.application.bus.query_bus import QueryBus
from lab_3.adapters.outbound.sqlite.student_repository import SqliteStudentRepository
from lab_3.adapters.outbound.sqlite.cours_repository import SqliteCoursRepository
from lab_3.adapters.outbound.sqlite.inscription_repository import SqliteInscriptionRepository


def bootstrap_query_bus(
    programme_repository: ProgrammeRepository,
    student_repository: SqliteStudentRepository,
    cours_repository: SqliteCoursRepository,
    inscription_repository: SqliteInscriptionRepository,
    unit_of_work: UnitOfWork,
) -> QueryBus:
    bus = SimpleQueryBus()
    bus.register(
        ProgrammeListQuery,
        ProgrammeListHandler(programme_repository, unit_of_work),
    )
    return bus
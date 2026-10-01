from lab_3.adapters.outbound.sqlite.cours_repository import SqliteCoursRepository
from lab_3.adapters.outbound.sqlite.inscription_repository import (
    SqliteInscriptionRepository,
)
from lab_3.adapters.outbound.sqlite.student_repository import SqliteStudentRepository
from lab_3.core.application.bus import CommandBus, SimpleCommandBus
from lab_3.core.application.ports.inbound.create_inscription import (
    CreateInscriptionCommand,

)
from lab_3.core.application.ports.inbound.update_inscription import (
    UpdateInscriptionNoteCommand,
)
from lab_3.core.application.ports.inbound.delete_inscription import (
    DeleteInscriptionCommand,
)
from lab_3.core.application.ports.outbound import UnitOfWork
from lab_3.core.application.services.create_inscription import CreateInscriptionHandler
from lab_3.core.application.services.update_inscription_note import UpdateInscriptionNoteHandler
from lab_3.core.application.services.delete_inscription import DeleteInscriptionHandler
from lab_3.core.application.ports.outbound.programme_repository import ProgrammeRepository

#programme 
from lab_3.core.application.ports.inbound.programmes.list import ProgrammeListQuery
from lab_3.core.application.services.programmes.list import ProgrammeListHandler

def bootstrap_command_bus(
    programme_repository: ProgrammeRepository,
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
    bus.register(
        UpdateInscriptionNoteCommand,
        UpdateInscriptionNoteHandler(
            inscription_repository=inscription_repository,
            unit_of_work=unit_of_work,
        ),
    )
    bus.register(
        DeleteInscriptionCommand,
        DeleteInscriptionHandler(
            inscription_repository=inscription_repository,
            unit_of_work=unit_of_work,
        ),
    )
    #programme commands
    bus.register(
        ProgrammeListQuery,
        ProgrammeListHandler(programme_repository, unit_of_work),
    )
    return bus

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
from lab_3.core.application.ports.inbound.programmes.create import CreateProgrammeCommand
from lab_3.core.application.services.programmes.create import CreateProgrammeHandler
from lab_3.core.application.ports.inbound.students.create import CreateStudentCommand
from lab_3.core.application.services.students.create import CreateStudentHandler
#programme 
from lab_3.core.application.ports.inbound.programmes.list import ProgrammeListQuery
from lab_3.core.application.services.programmes.list import ProgrammeListHandler
from lab_3.core.application.ports.inbound.students.get import GetStudentCommand
from lab_3.core.application.services.students.get import GetStudentHandler
from lab_3.core.application.ports.inbound.students.delete import DeleteStudentCommand
from lab_3.core.application.services.students.delete import DeleteStudentHandler
from lab_3.core.application.ports.inbound.cours.create import CreateCoursCommand
from lab_3.core.application.ports.inbound.cours.get import GetCoursCommand
from lab_3.core.application.services.cours.create import CreateCoursHandler
from lab_3.core.application.services.cours.get import GetCoursHandler
from lab_3.core.application.ports.inbound.cours.list import ListCoursCommand
from lab_3.core.application.services.cours.list import ListCoursHandler
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
    bus.register(
        CreateProgrammeCommand,
        CreateProgrammeHandler(programme_repository, unit_of_work),
    )
    #student commands
    bus.register(
        CreateStudentCommand,
        CreateStudentHandler(student_repository=student_repository, programme_repository=programme_repository, unit_of_work=unit_of_work),
    )
    bus.register(
        GetStudentCommand,
        GetStudentHandler(student_repository=student_repository, unit_of_work=unit_of_work),
    )
    bus.register(
        DeleteStudentCommand,
        DeleteStudentHandler(student_repository=student_repository, unit_of_work=unit_of_work),
    )
    bus.register(
        CreateCoursCommand,
        CreateCoursHandler(cours_repository=cours_repository, unit_of_work=unit_of_work),
    )
    bus.register(
        GetCoursCommand,
        GetCoursHandler(cours_repository=cours_repository, unit_of_work=unit_of_work),
    )
    bus.register(
        ListCoursCommand,
        ListCoursHandler(cours_repository=cours_repository, unit_of_work=unit_of_work),
    )   

    return bus

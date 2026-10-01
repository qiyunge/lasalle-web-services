from lab_3.adapters.outbound.sqlite.cours_repository import SqliteCoursRepository
from lab_3.adapters.outbound.sqlite.inscription_repository import (
    SqliteInscriptionRepository,
)
from lab_3.adapters.outbound.sqlite.student_repository import SqliteStudentRepository
from lab_3.adapters.outbound.sqlite.unit_of_work import SqliteConnectionProvider
from lab_3.adapters.outbound.sqlite.programme_repository import SqliteProgrammeRepository


def bootstrap_repositories(connections: SqliteConnectionProvider):
    programme_repository = SqliteProgrammeRepository(connections)
    student_repository = SqliteStudentRepository(connections)
    cours_repository = SqliteCoursRepository(connections)
    inscription_repository = SqliteInscriptionRepository(connections)
    return programme_repository, student_repository, cours_repository, inscription_repository

import sqlite3

from lab_3.adapters.outbound.sqlite.student_repository import SqliteStudentRepository
from lab_3.adapters.outbound.sqlite.cours_repository import SqliteCoursRepository
from lab_3.adapters.outbound.sqlite.inscription_repository import SqliteInscriptionRepository
from lab_3.adapters.outbound.sqlite.connection import SqliteConnectionFactory

def bootstrap_repositories(connection_factory: SqliteConnectionFactory):

    student_repository = SqliteStudentRepository(connection_factory)
    cours_repository = SqliteCoursRepository(connection_factory)
    inscription_repository = SqliteInscriptionRepository(connection_factory)

    return student_repository, cours_repository, inscription_repository
import sqlite3

from lab_3.adapters.outbound.sqlite.student_repository import SqliteStudentRepository
from lab_3.adapters.outbound.sqlite.cours_repository import SqliteCoursRepository
from lab_3.adapters.outbound.sqlite.inscription_repository import SqliteInscriptionRepository

def bootstrap_repositories(connection:sqlite3.Connection):

    student_repository = SqliteStudentRepository(connection)
    cours_repository = SqliteCoursRepository(connection)
    inscription_repository = SqliteInscriptionRepository(connection)

    return student_repository, cours_repository, inscription_repository
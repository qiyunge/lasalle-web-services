# from __future__ import annotations
# from lab_3.core.domain.student import Student
# from lab_3.core.domain.value_objects import StudentId, StudentName, StudentEmail
# from lab_3.core.domain.value_objects import ProgrammeId
# from lab_3.core.domain.common import Result, Success, Failure, ValidationErrors, ValidationError, collect_errors

# class StudentFactory:
#     @staticmethod
#     def create_from_primitive(
#                 name: str,
#                 email: str,
#                 programme_id: int,
#     ) -> Result[Student, ValidationErrors]:
#         name_result = StudentName.create(name)
#         email_result = StudentEmail.create(email)
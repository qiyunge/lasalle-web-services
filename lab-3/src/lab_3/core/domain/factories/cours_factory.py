from typing import Any


from __future__ import annotations
from lab_3.core.domain.cours import Cours
from lab_3.core.domain.value_objects import CoursId, CoursCode, CoursName
from lab_3.core.domain.common import Result, Success, Failure, ValidationErrors, ValidationError, collect_errors

class CoursFactory:
    @staticmethod
    def create_from_primitive(
                code: str, 
                name: str, 
              ) -> Result[Cours, ValidationError]:

                code_result = CoursCode.create(code)
                name_result = CoursName.create(name)
                errors = collect_errors(code_result, name_result)
                if errors:
                    return Failure(ValidationErrors(tuple(errors)))
                return Success(Cours.create(code=code_result.value, name=name_result.value))

    @staticmethod
    def restore_from_primitive(
                id: int,    
                code: str,
                name: str,
              
    ) -> Result[Cours, ValidationErrors]:
        id_result = CoursId.create(id)
        code_result = CoursCode.create(code)
        name_result = CoursName.create(name)
        errors = collect_errors(id_result, code_result, name_result)
        if errors:
            return Failure(ValidationErrors(tuple(errors)))
        return Success(Cours.restore(id=id_result.value,
                                     code=code_result.value,
                                     name=name_result.value))
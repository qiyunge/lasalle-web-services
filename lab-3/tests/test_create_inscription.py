from __future__ import annotations

from typing import Self

from lab_3.core.application.ports.inbound.create_inscription import (
    CourseNotFound,
    CreateInscriptionCommand,
    InscriptionAlreadyExists,
    StudentNotFound,
)
from lab_3.core.application.ports.outbound.inscription_repository import (
    InscriptionDuplicate,
    InscriptionIdConflict,
    SaveInscriptionError,
)
from lab_3.core.application.ports.outbound.unit_of_work import (
    TransactionRestartRequired,
)
from lab_3.core.application.services.create_inscription import CreateInscriptionHandler
from lab_3.core.domain.common import Failure, Result, Success
from lab_3.core.domain.common.validation import ValidationError
from lab_3.core.domain.inscription import Inscription
from lab_3.core.domain.value_objects import CoursId, InscriptionId, StudentId


def _value[T](result: Result[T, ValidationError]) -> T:
    if isinstance(result, Failure):
        raise AssertionError(result.error.message)
    return result.value


def _inscription_id(inscription: Inscription) -> InscriptionId:
    if inscription.id is None:
        raise AssertionError("Inscription id is required")
    return inscription.id


def _command(student_id: int = 1, cours_id: int = 2) -> CreateInscriptionCommand:
    return CreateInscriptionCommand(
        student_id=_value(StudentId.create(student_id)),
        cours_id=_value(CoursId.create(cours_id)),
    )


class _UnitOfWork:
    def __init__(self) -> None:
        self.entered = 0
        self.commits = 0

    def __enter__(self) -> Self:
        self.entered += 1
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def commit(self) -> None:
        self.commits += 1


class _Students:
    def __init__(self, present: bool = True) -> None:
        self.present = present
        self.calls = 0

    def exists(self, id: StudentId) -> bool:
        self.calls += 1
        return self.present


class _Cours:
    def __init__(self, present: bool = True) -> None:
        self.present = present
        self.calls = 0

    def exists(self, id: CoursId) -> bool:
        self.calls += 1
        return self.present


class _Inscriptions:
    def __init__(
        self,
        existing: bool = False,
        failures: list[SaveInscriptionError | TransactionRestartRequired] | None = None,
    ) -> None:
        self.existing = existing
        self.failures = list(failures or [])
        self.saved: list[Inscription] = []
        self.exists_calls = 0

    def exists(self, student_id: StudentId, cours_id: CoursId) -> bool:
        self.exists_calls += 1
        return self.existing

    def save(self, inscription: Inscription) -> Result[Inscription, SaveInscriptionError]:
        self.saved.append(inscription)
        if self.failures:
            error = self.failures.pop(0)
            if isinstance(error, TransactionRestartRequired):
                raise error
            return Failure(error)
        return Success(inscription)


def _handler(
    students: _Students | None = None,
    cours: _Cours | None = None,
    inscriptions: _Inscriptions | None = None,
    unit_of_work: _UnitOfWork | None = None,
) -> tuple[CreateInscriptionHandler, _UnitOfWork, _Inscriptions]:
    students = students or _Students()
    cours = cours or _Cours()
    inscriptions = inscriptions or _Inscriptions()
    unit_of_work = unit_of_work or _UnitOfWork()
    handler = CreateInscriptionHandler(inscriptions, students, cours, unit_of_work)
    return handler, unit_of_work, inscriptions


def test_creates_inscription_and_commits() -> None:
    handler, unit_of_work, inscriptions = _handler()

    result = handler.handle(_command())

    assert isinstance(result, Success)
    assert result.value.student_id == 1
    assert result.value.cours_id == 2
    assert result.value.note is None
    assert result.value.id == _inscription_id(inscriptions.saved[0]).value
    assert unit_of_work.entered == 1
    assert unit_of_work.commits == 1


def test_returns_student_not_found_without_writing() -> None:
    students = _Students(present=False)
    cours = _Cours()
    handler, unit_of_work, inscriptions = _handler(students=students, cours=cours)

    result = handler.handle(_command())

    assert isinstance(result, Failure)
    assert isinstance(result.error, StudentNotFound)
    assert result.error.student_id.value == 1
    assert cours.calls == 0
    assert inscriptions.saved == []
    assert unit_of_work.commits == 0


def test_returns_course_not_found_without_writing() -> None:
    handler, unit_of_work, inscriptions = _handler(cours=_Cours(present=False))

    result = handler.handle(_command(cours_id=9))

    assert isinstance(result, Failure)
    assert isinstance(result.error, CourseNotFound)
    assert result.error.cours_id.value == 9
    assert inscriptions.saved == []
    assert unit_of_work.commits == 0


def test_returns_already_exists_without_writing() -> None:
    handler, unit_of_work, inscriptions = _handler(
        inscriptions=_Inscriptions(existing=True)
    )

    result = handler.handle(_command())

    assert isinstance(result, Failure)
    assert isinstance(result.error, InscriptionAlreadyExists)
    assert inscriptions.saved == []
    assert unit_of_work.commits == 0


class _IdConflictThenSuccess(_Inscriptions):
    def save(self, inscription: Inscription) -> Result[Inscription, SaveInscriptionError]:
        self.saved.append(inscription)
        if len(self.saved) == 1:
            raise InscriptionIdConflict(_inscription_id(inscription))
        return Success(inscription)


class _AlwaysIdConflict(_Inscriptions):
    def save(self, inscription: Inscription) -> Result[Inscription, SaveInscriptionError]:
        self.saved.append(inscription)
        raise InscriptionIdConflict(_inscription_id(inscription))


def test_retries_with_a_new_id_after_id_conflict() -> None:
    handler, unit_of_work, inscriptions = _handler(inscriptions=_IdConflictThenSuccess())

    result = handler.handle(_command())

    assert isinstance(result, Success)
    assert len(inscriptions.saved) == 2
    assert _inscription_id(inscriptions.saved[0]) != _inscription_id(inscriptions.saved[1])
    assert result.value.id == _inscription_id(inscriptions.saved[1]).value
    assert unit_of_work.entered == 2
    assert unit_of_work.commits == 1


def test_raises_when_every_generated_id_conflicts() -> None:
    inscriptions = _AlwaysIdConflict()
    handler, unit_of_work, _ = _handler(inscriptions=inscriptions)

    try:
        handler.handle(_command())
    except RuntimeError as error:
        assert str(error) == "Failed to allocate an inscription id"
    else:
        raise AssertionError("id allocation failure was returned to the caller")

    assert len(inscriptions.saved) == 3
    assert unit_of_work.commits == 0


def test_retries_the_same_id_when_the_transaction_restarts() -> None:
    inscriptions = _Inscriptions(failures=[TransactionRestartRequired()])
    handler, unit_of_work, inscriptions = _handler(inscriptions=inscriptions)

    result = handler.handle(_command())

    assert isinstance(result, Success)
    assert _inscription_id(inscriptions.saved[0]) is _inscription_id(inscriptions.saved[1])
    assert result.value.id == _inscription_id(inscriptions.saved[1]).value
    assert unit_of_work.entered == 2
    assert unit_of_work.commits == 1


def test_raises_when_the_transaction_keeps_restarting() -> None:
    inscriptions = _Inscriptions(
        failures=[
            TransactionRestartRequired(),
            TransactionRestartRequired(),
            TransactionRestartRequired(),
        ]
    )
    handler, _, _ = _handler(inscriptions=inscriptions)

    try:
        handler.handle(_command())
    except TransactionRestartRequired:
        pass
    else:
        raise AssertionError("transaction restart was hidden")


def test_returns_duplicate_without_another_attempt() -> None:
    command = _command()
    inscriptions = _Inscriptions(
        failures=[InscriptionDuplicate(command.student_id, command.cours_id)]
    )
    handler, unit_of_work, inscriptions = _handler(inscriptions=inscriptions)

    result = handler.handle(command)

    assert isinstance(result, Failure)
    assert isinstance(result.error, InscriptionAlreadyExists)
    assert len(inscriptions.saved) == 1
    assert unit_of_work.entered == 1
    assert unit_of_work.commits == 0

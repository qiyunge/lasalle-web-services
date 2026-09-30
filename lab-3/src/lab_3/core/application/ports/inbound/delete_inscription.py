from dataclasses import dataclass
from typing import Protocol

from lab_3.core.application.command import Command
from lab_3.core.domain.common import Result
from lab_3.core.domain.value_objects import InscriptionId

@dataclass(frozen=True)
class InscriptionIdNotFound:
    id: InscriptionId

@dataclass(frozen=True)
class DeleteInscriptionResult:
    id: int


type DeleteInscriptionOutcome = Result[DeleteInscriptionResult, InscriptionIdNotFound]

@dataclass(frozen=True)
class DeleteInscriptionCommand(Command[DeleteInscriptionOutcome]):
    id: InscriptionId

class DeleteInscriptionUseCase(Protocol):
    def handle(self, command: DeleteInscriptionCommand) -> DeleteInscriptionOutcome: ...
from __future__ import annotations
from typing import Protocol

from dataclasses import dataclass

from lab_3.core.application.command import Command
from lab_3.core.domain.common import Result
from lab_3.core.domain.value_objects import InscriptionId, Note

@dataclass(frozen=True)
class InscriptionNotFound:
    id: InscriptionId

@dataclass(frozen=True)
class UpdateInscriptionNoteResult:
    id:int
    note:float|None

type UpdateInscriptionNoteOutcome = Result[UpdateInscriptionNoteResult, InscriptionNotFound]

@dataclass(frozen=True)
class UpdateInscriptionNoteCommand(Command[UpdateInscriptionNoteOutcome]):
    id: InscriptionId
    note: Note | None

class UpdateInscriptionNoteUseCase(Protocol):
    def handle(self, command: UpdateInscriptionNoteCommand) -> UpdateInscriptionNoteOutcome: ...
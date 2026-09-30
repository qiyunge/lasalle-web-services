from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CreateInscriptionResponse:
    id: int
    student_id: int
    cours_id: int
    note: float | None

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass(frozen=True)
class UpdateInscriptionNoteResponse:
    id: int
    note: float | None

    def to_dict(self) -> dict:
        return asdict(self)
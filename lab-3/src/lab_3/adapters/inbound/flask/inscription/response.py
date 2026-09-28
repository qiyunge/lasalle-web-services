from dataclasses import dataclass,asdict

@dataclass(frozen=True)
class CreateInscriptionResponse:
    id: int
    student_id: int
    course_id: int
    note: float|None

    def to_dict(self) -> dict:
        return asdict(self)

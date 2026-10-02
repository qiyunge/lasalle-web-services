from dataclasses import dataclass, asdict
@dataclass(frozen=True)
class CreateStudentResponse:
    student_id: int
    name: str
    email: str
    programme_id: int

    def to_dict(self) -> dict:
        return asdict(self)
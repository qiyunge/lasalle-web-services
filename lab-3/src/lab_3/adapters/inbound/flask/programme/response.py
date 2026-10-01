from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CreateProgrammeResponse:
    id: int
    name: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
        }
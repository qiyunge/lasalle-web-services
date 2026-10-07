from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CreateCoursResponse:
    cours_id: int
    cours_code: str
    cours_name: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class GetCoursResponse:
    cours_id: int
    cours_code: str
    cours_name: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class CoursListItemResponse:
    cours_id: int
    cours_code: str
    cours_name: str


@dataclass(frozen=True)
class ListCoursResponse:
    items: tuple[CoursListItemResponse, ...]
    page: int
    page_size: int

    def to_dict(self) -> dict:
        return {
            "items": [asdict(item) for item in self.items],
           
            "page": self.page,
            "page_size": self.page_size,
        }

"""Programme capability. Imports no other capability."""

from dataclasses import dataclass

from college.domain.identifiers import ProgrammeId
from college.domain.result import ConstructionError, Failure, Success
from college.domain.text import is_present


@dataclass(frozen=True)
class InvalidProgramme:
    """A stored programme that cannot be constructed. id is the stored value."""

    id: object


@dataclass(frozen=True)
class Programme:
    """id is required. name is required and present. Names are not unique.

    This feature does not create programmes, so the only factory rebuilds
    a stored one.
    """

    id: ProgrammeId
    name: str

    def __post_init__(self) -> None:
        if not (isinstance(self.id, ProgrammeId) and is_present(self.name)):
            raise ConstructionError

    @classmethod
    def reconstitute(
        cls, id: ProgrammeId, name: object
    ) -> Success["Programme"] | Failure[InvalidProgramme]:
        if not is_present(name):
            return Failure(InvalidProgramme(id.value))
        return Success(cls(id, name))

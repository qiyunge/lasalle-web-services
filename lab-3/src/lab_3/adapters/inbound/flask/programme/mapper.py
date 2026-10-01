from lab_3.core.application.ports.inbound.programmes.list import (
    ProgrammeListResult,
  
)

def to_programme_list_response(result: ProgrammeListResult) -> list[dict]:
    return [{"id": programme_item.id, "name": programme_item.name} for programme_item in result.programmes]
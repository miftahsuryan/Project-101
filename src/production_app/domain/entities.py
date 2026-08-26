from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Asset:
    id: UUID
    asset_code: str
    name: str

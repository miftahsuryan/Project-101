from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from production_app.domain.entities import Reading


@dataclass(frozen=True)
class ReadingSummary:
    total: int
    average: float | None
    latest: float | None


class ReadingRepository(Protocol):
    def add_many(self, readings: Sequence[Reading]) -> None: ...

    def get_summary(self) -> ReadingSummary: ...

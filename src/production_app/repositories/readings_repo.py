from collections.abc import Sequence
from typing import Protocol

from production_app.domain.entities import Reading


class ReadingRepository(Protocol):
    def add_many(self, readings: Sequence[Reading]) -> None: ...

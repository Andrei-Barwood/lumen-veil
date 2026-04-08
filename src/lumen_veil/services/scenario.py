from __future__ import annotations

from typing import Dict, List

from ..scenario import ScenarioBook


class ScenarioService:
    def __init__(self, book: ScenarioBook | None = None) -> None:
        self.book = book or ScenarioBook()

    def list(self) -> List[Dict[str, object]]:
        return self.book.list()

    def load(self, path: str):
        return self.book.load(path)

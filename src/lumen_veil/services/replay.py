from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from ..events import Event


@dataclass
class ReplayVault:
    records: List[Dict[str, object]] = field(default_factory=list)

    def capture(self, event: Event) -> None:
        self.records.append(event.to_dict())

    def summary(self) -> Dict[str, object]:
        return {
            "count": len(self.records),
            "names": [record["name"] for record in self.records],
        }

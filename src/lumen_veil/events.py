from __future__ import annotations

import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Dict, List


@dataclass
class Event:
    name: str
    payload: Dict[str, object]
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "payload": dict(self.payload),
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
        }


class EventBus:
    def __init__(self) -> None:
        self._subscribers = defaultdict(list)
        self.stream: List[Event] = []

    def subscribe(self, name: str, callback: Callable[[Event], None]) -> None:
        self._subscribers[name].append(callback)

    def publish(self, name: str, payload: Dict[str, object]) -> Event:
        event = Event(name=name, payload=payload)
        self.stream.append(event)
        for callback in self._subscribers.get(name, []):
            callback(event)
        for callback in self._subscribers.get("*", []):
            callback(event)
        return event

    def replay(self, callback: Callable[[Event], None]) -> None:
        for event in self.stream:
            callback(event)

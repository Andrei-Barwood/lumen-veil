from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": time.time(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "context"):
            payload["context"] = record.context
        return json.dumps(payload, sort_keys=True)


def build_logger(name: str = "lumen_veil") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


@dataclass
class MetricsLedger:
    counters: Dict[str, int] = field(default_factory=dict)
    gauges: Dict[str, float] = field(default_factory=dict)
    transitions: List[Dict[str, object]] = field(default_factory=list)

    def increment(self, name: str, amount: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + amount

    def set_gauge(self, name: str, value: float) -> None:
        self.gauges[name] = value

    def record_transition(self, vessel_id: str, state: str, reason: str) -> None:
        self.transitions.append({"vessel_id": vessel_id, "state": state, "reason": reason})

    def snapshot(self) -> Dict[str, object]:
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "transitions": list(self.transitions),
        }


@dataclass
class HealthCheck:
    name: str
    status: str
    detail: str

    def to_dict(self) -> Dict[str, str]:
        return {"name": self.name, "status": self.status, "detail": self.detail}

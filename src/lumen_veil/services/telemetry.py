from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from ..domain import World
from ..observability import MetricsLedger, build_logger


@dataclass
class TelemetryService:
    metrics: MetricsLedger
    frames: List[Dict[str, object]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.logger = build_logger("lumen_veil.telemetry")

    def capture(self, world: World) -> Dict[str, object]:
        frame = {
            "tick": world.tick,
            "time": world.time,
            "jurisdiction": world.jurisdiction,
            "vessels": [
                {
                    "id": vessel.ident,
                    "state": vessel.state.value,
                    "classification": vessel.classification,
                    "behavior": vessel.behavior,
                    "position": vessel.position.to_dict(),
                    "systems": vessel.systems.to_dict(),
                    "exposure": vessel.exposure,
                }
                for vessel in world.vessels
            ],
        }
        self.frames.append(frame)
        self.metrics.set_gauge("world.tick", float(world.tick))
        self.metrics.set_gauge("world.time", float(world.time))
        self.logger.info("telemetry frame", extra={"context": {"tick": world.tick, "vessels": len(world.vessels)}})
        return frame

from __future__ import annotations

from typing import Dict

from ..domain import Vessel, WitnessRecord, World
from ..events import EventBus


class WitnessService:
    def observe(self, world: World, bus: EventBus) -> Dict[str, WitnessRecord]:
        records: Dict[str, WitnessRecord] = {}
        for vessel in world.vessels:
            best_confidence = 0.0
            notes = []
            for array in world.witness_arrays:
                distance = vessel.position.distance_to(array.position)
                if distance > array.reach:
                    continue
                range_factor = max(0.0, 1.0 - (distance / max(array.reach, 1e-6)))
                confidence = array.fidelity * range_factor
                if confidence > best_confidence:
                    best_confidence = confidence
                notes.append(f"array:{array.name}")
            if best_confidence == 0.0:
                best_confidence = 0.08
                notes.append("array:none")
            behavior_signal = min(1.0, vessel.velocity.magnitude() / 12.0)
            transponder = vessel.seal.trust if vessel.seal else 0.0
            record = WitnessRecord(
                vessel_id=vessel.ident,
                confidence=best_confidence,
                thermal=vessel.thermal_signature * best_confidence,
                engine=vessel.engine_signature * best_confidence,
                transponder=transponder * max(0.4, best_confidence),
                behavior=behavior_signal,
                notes=notes,
            )
            records[vessel.ident] = record
            bus.publish(
                "VesselWitnessed",
                {
                    "tick": world.tick,
                    "vessel_id": vessel.ident,
                    "confidence": record.confidence,
                    "notes": list(record.notes),
                },
            )
        return records

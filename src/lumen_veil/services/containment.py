from __future__ import annotations

from ..domain import CanonDecision, Vessel
from ..events import EventBus


class MercyService:
    def apply(self, world_tick: int, vessel: Vessel, decision: CanonDecision, bus: EventBus) -> None:
        self._apply_effects(vessel, decision)
        vessel.transition(decision.target_state, decision.reason_code)
        for event_name in self._default_events(decision):
            bus.publish(
                event_name,
                {
                    "tick": world_tick,
                    "vessel_id": vessel.ident,
                    "action": decision.action,
                    "reason_code": decision.reason_code,
                },
            )
        for event_name in decision.emitted_events:
            bus.publish(
                event_name,
                {
                    "tick": world_tick,
                    "vessel_id": vessel.ident,
                    "rule_name": decision.rule_name,
                    "reason_code": decision.reason_code,
                },
            )

    def _apply_effects(self, vessel: Vessel, decision: CanonDecision) -> None:
        sensors = decision.effects.get("sensors", 0.0)
        comms = decision.effects.get("comms", 0.0)
        navigation = decision.effects.get("navigation", 0.0)
        control = decision.effects.get("control_link", 0.0)
        hardpoint = decision.effects.get("hardpoint_sync", 0.0)
        damping = decision.effects.get("velocity_damping", 1.0)
        restore = decision.effects.get("restore", 0.0)

        vessel.systems.sensors = vessel.systems.sensors - sensors + restore
        vessel.systems.comms = vessel.systems.comms - comms + restore
        vessel.systems.navigation = vessel.systems.navigation - navigation + restore
        vessel.systems.control_link = vessel.systems.control_link - control + restore
        vessel.systems.hardpoint_sync = vessel.systems.hardpoint_sync - hardpoint + restore
        vessel.velocity = vessel.velocity.scale(damping)
        vessel.systems.clamp()

    def _default_events(self, decision: CanonDecision):
        mapping = {
            "warn": ["GraceDenied"],
            "shadow": ["AegisShifted"],
            "degrade": ["SilenceInvoked"],
            "contain": ["ContainmentRaised"],
            "release": ["TransitPurified"],
            "bless": ["TransitPurified"],
            "exile": ["GraceDenied"],
        }
        return mapping.get(decision.action, [])

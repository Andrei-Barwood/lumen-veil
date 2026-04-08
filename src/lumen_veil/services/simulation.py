from __future__ import annotations

from typing import Dict

from ..domain import JurisdictionProfile, World
from ..events import Event, EventBus
from ..observability import MetricsLedger
from ..physics import PhysicsEngine
from .audit import AuditLedger
from .authority import JudicatorService
from .containment import MercyService
from .replay import ReplayVault
from .sensing import WitnessService
from .telemetry import TelemetryService
from .training import TrainingService


class SimulationOrchestrator:
    def __init__(self, profile: JurisdictionProfile) -> None:
        self.profile = profile
        self.bus = EventBus()
        self.metrics = MetricsLedger()
        self.audit = AuditLedger()
        self.telemetry = TelemetryService(self.metrics)
        self.replay = ReplayVault()
        self.training = TrainingService()
        self.witness = WitnessService()
        self.judicator = JudicatorService(profile)
        self.canon = self.judicator.canon
        self.mercy = MercyService()
        self.physics = PhysicsEngine()
        self.bus.subscribe("*", self._capture_event)

    def _capture_event(self, event: Event) -> None:
        self.replay.capture(event)
        self.metrics.increment(f"event.{event.name}")

    def step(self, world: World, dt: float = 1.0) -> Dict[str, object]:
        world.tick += 1
        world.time += dt
        self._emit_thresholds(world)
        witness_records = self.witness.observe(world, self.bus)
        decisions = {}
        for vessel in world.vessels:
            witness = witness_records[vessel.ident]
            assessment, decision = self.judicator.judge(world, vessel, witness.confidence)
            previous_state = vessel.state.value
            self.mercy.apply(world.tick, vessel, decision, self.bus)
            self.metrics.record_transition(vessel.ident, vessel.state.value, decision.reason_code)
            self.audit.record(world.tick, vessel, assessment, decision, previous_state)
            decisions[vessel.ident] = {
                "assessment": assessment.to_dict(),
                "decision": decision.to_dict(),
            }
        self.physics.advance(world, dt=dt)
        frame = self.telemetry.capture(world)
        return {
            "tick": world.tick,
            "decisions": decisions,
            "telemetry": frame,
            "litany": self._compose_tick_litany(world, decisions),
        }

    def run(self, world: World, steps: int = 6, dt: float = 1.0) -> Dict[str, object]:
        ticks = []
        for _ in range(steps):
            ticks.append(self.step(world, dt=dt))
        final_states = {vessel.ident: vessel.state.value for vessel in world.vessels}
        report = {
            "scenario": world.scenario,
            "jurisdiction": world.jurisdiction,
            "doctrine": world.doctrine,
            "canon_name": self.profile.name,
            "steps": steps,
            "dt": dt,
            "ticks": ticks,
            "final_states": final_states,
            "events": [event.to_dict() for event in self.bus.stream],
            "audit": list(self.audit.entries),
            "metrics": self.metrics.snapshot(),
            "replay": self.replay.summary(),
            "training": {},
            "native_physics": self.physics.native_available,
        }
        report["training"] = self.training.review(report)
        report["rite_summary"] = self._compose_rite_summary(world, report)
        return report

    def _emit_thresholds(self, world: World) -> None:
        for vessel in world.vessels:
            for threshold in world.thresholds:
                if threshold.jurisdiction != world.jurisdiction:
                    continue
                if threshold.contains(vessel.position):
                    self.bus.publish(
                        "ThresholdCrossed",
                        {"tick": world.tick, "vessel_id": vessel.ident, "threshold": threshold.name},
                    )

    def _compose_tick_litany(self, world: World, decisions: Dict[str, Dict[str, object]]) -> str:
        phrases = []
        for vessel in world.vessels:
            decision = decisions[vessel.ident]["decision"]
            phrases.append(
                f"{vessel.callsign} was set to {vessel.state.value} through {decision['rule_name']}"
            )
        return f"Tick {world.tick}: " + "; ".join(phrases) + "."

    def _compose_rite_summary(self, world: World, report: Dict[str, object]) -> str:
        outcomes = []
        for vessel in world.vessels:
            outcomes.append(f"{vessel.callsign} ended {vessel.state.value}")
        return (
            f"{self.profile.name} completed {world.scenario} after {report['steps']} steps; "
            + "; ".join(outcomes)
            + "."
        )

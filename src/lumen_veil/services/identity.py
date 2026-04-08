from __future__ import annotations

from typing import Optional

from ..domain import IdentityAssessment, TransitCorridor, Vessel, World


class SealService:
    def assess(self, world: World, vessel: Vessel, confidence: float) -> IdentityAssessment:
        corridor = self._best_corridor(world, vessel)
        corridor_violation = corridor is None
        permit_present = bool(
            vessel.permit
            and vessel.permit.jurisdiction == world.jurisdiction
            and (corridor is None or vessel.permit.corridor == corridor.name)
        )
        sacred_violation = self._sacred_violation(world, vessel, corridor, permit_present)
        seal_present = bool(vessel.seal and vessel.seal.trust >= 0.45)
        behavior = self._behavior(vessel, corridor)
        anomaly = 0.0
        reasons = []

        if confidence < 0.22:
            anomaly += 0.18
            reasons.append("witness.veiled")
        if not seal_present:
            anomaly += 0.24
            reasons.append("seal.unproven")
        if not permit_present:
            anomaly += 0.18
            reasons.append("permit.ungranted")
        if corridor_violation:
            anomaly += 0.26
            reasons.append("corridor.departed")
        if sacred_violation:
            anomaly += 0.34
            reasons.append("sanctuary.transgressed")
        if vessel.engine_signature >= 0.72:
            anomaly += 0.22
            reasons.append("engine.hymn.dissonant")
        if vessel.thermal_signature >= 0.6:
            anomaly += 0.08
            reasons.append("thermal.halo.elevated")
        if behavior in {"erratic", "pressing"}:
            anomaly += 0.14
            reasons.append("bearing.disordered")

        anomaly = min(1.0, anomaly)

        classification = "unknown"
        if sacred_violation and not permit_present:
            classification = "intruder"
        elif seal_present and permit_present and not corridor_violation and anomaly < 0.25:
            classification = "ally" if vessel.allegiance == world.jurisdiction else "authorized"
        elif anomaly >= 0.75:
            classification = "hostile"
        elif anomaly >= 0.45:
            classification = "suspicious"
        elif seal_present:
            classification = "known"

        vessel.classification = classification
        vessel.behavior = behavior
        return IdentityAssessment(
            vessel_id=vessel.ident,
            classification=classification,
            behavior=behavior,
            anomaly_score=anomaly,
            corridor_violation=corridor_violation,
            sacred_violation=sacred_violation,
            permit_present=permit_present,
            seal_present=seal_present,
            reasons=reasons,
        )

    def _best_corridor(self, world: World, vessel: Vessel) -> Optional[TransitCorridor]:
        local = [corridor for corridor in world.corridors if corridor.jurisdiction == world.jurisdiction]
        if not local:
            return None
        ranked = sorted(local, key=lambda corridor: corridor.distance_to(vessel.position))
        best = ranked[0]
        return best if best.contains(vessel.position) else None

    def _sacred_violation(
        self,
        world: World,
        vessel: Vessel,
        corridor: Optional[TransitCorridor],
        permit_present: bool,
    ) -> bool:
        in_sanctuary = any(
            sanctuary.contains(vessel.position) and sanctuary.jurisdiction == world.jurisdiction
            for sanctuary in world.sanctuaries
        )
        sacred_corridor = bool(corridor and corridor.sacred and not (vessel.permit and vessel.permit.sacred_clearance))
        return in_sanctuary or (sacred_corridor and not permit_present)

    def _behavior(self, vessel: Vessel, corridor: Optional[TransitCorridor]) -> str:
        speed = vessel.velocity.magnitude()
        if corridor and speed <= 6.0:
            return "disciplined"
        if corridor and speed <= 9.0:
            return "drifting"
        if speed > 10.0:
            return "pressing"
        return "erratic"

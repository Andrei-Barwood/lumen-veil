from __future__ import annotations

from typing import Tuple

from ..domain import CanonDecision, IdentityAssessment, JurisdictionProfile, Vessel, World
from ..policy import CanonEngine
from .identity import SealService


class JudicatorService:
    def __init__(self, profile: JurisdictionProfile) -> None:
        self.profile = profile
        self.seals = SealService()
        self.canon = CanonEngine(profile)

    def judge(self, world: World, vessel: Vessel, confidence: float) -> Tuple[IdentityAssessment, CanonDecision]:
        assessment = self.seals.assess(world, vessel, confidence)
        decision = self.canon.evaluate(vessel, assessment)
        return assessment, decision

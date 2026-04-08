from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from ..domain import CanonDecision, IdentityAssessment, Vessel


@dataclass
class AuditLedger:
    entries: List[Dict[str, object]] = field(default_factory=list)

    def record(
        self,
        tick: int,
        vessel: Vessel,
        assessment: IdentityAssessment,
        decision: CanonDecision,
        previous_state: str,
    ) -> None:
        self.entries.append(
            {
                "tick": tick,
                "vessel_id": vessel.ident,
                "callsign": vessel.callsign,
                "state_before": previous_state,
                "state_after": vessel.state.value,
                "classification": assessment.classification,
                "behavior": assessment.behavior,
                "anomaly_score": assessment.anomaly_score,
                "action": decision.action,
                "reason_code": decision.reason_code,
                "rule_name": decision.rule_name,
                "effects": dict(decision.effects),
                "explanation": decision.explanation,
            }
        )

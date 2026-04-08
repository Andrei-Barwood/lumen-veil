from __future__ import annotations

from typing import Dict, Iterable

from .domain import CanonDecision, CanonRule, IdentityAssessment, JurisdictionProfile, Vessel


class CanonEngine:
    def __init__(self, profile: JurisdictionProfile) -> None:
        self.profile = profile

    def evaluate(self, vessel: Vessel, assessment: IdentityAssessment) -> CanonDecision:
        context = self._build_context(vessel, assessment)
        for rule in sorted(self.profile.rules, key=lambda item: item.priority):
            if self._matches(rule, context):
                return CanonDecision(
                    action=rule.action,
                    target_state=rule.target_state,
                    reason_code=rule.reason_code,
                    rule_name=rule.name,
                    effects=dict(rule.effects),
                    emitted_events=list(rule.emit),
                    explanation=self._explain(rule, context),
                )
        return CanonDecision(
            action="observe",
            target_state=vessel.state,
            reason_code="canon.witness.sustained",
            rule_name="default-observe",
            effects={},
            emitted_events=[],
            explanation="No canon rule matched; vessel remains beneath witness.",
        )

    def _build_context(self, vessel: Vessel, assessment: IdentityAssessment) -> Dict[str, object]:
        return {
            "classification": assessment.classification,
            "behavior": assessment.behavior,
            "anomaly_score": assessment.anomaly_score,
            "corridor_violation": assessment.corridor_violation,
            "sacred_violation": assessment.sacred_violation,
            "permit_present": assessment.permit_present,
            "seal_present": assessment.seal_present,
            "current_state": vessel.state.value,
            "exposure": vessel.exposure,
            "subsystem_health": vessel.subsystem_health(),
        }

    def _matches(self, rule: CanonRule, context: Dict[str, object]) -> bool:
        for key, expected in rule.match.items():
            value = context.get(key)
            if key.endswith("_in"):
                actual_key = key[:-3]
                if context.get(actual_key) not in expected:
                    return False
                continue
            if key.endswith("_gte"):
                actual_key = key[:-4]
                if float(context.get(actual_key, 0.0)) < float(expected):
                    return False
                continue
            if key.endswith("_lte"):
                actual_key = key[:-4]
                if float(context.get(actual_key, 0.0)) > float(expected):
                    return False
                continue
            if key.endswith("_ne"):
                actual_key = key[:-3]
                if context.get(actual_key) == expected:
                    return False
                continue
            if value != expected:
                return False
        return True

    def _explain(self, rule: CanonRule, context: Dict[str, object]) -> str:
        terms = []
        for key, value in sorted(rule.match.items()):
            terms.append(f"{key}={value!r}")
        clause = ", ".join(terms) if terms else "no predicates"
        return (
            f"{self.profile.name} selected {rule.name} because {clause}; "
            f"current_state={context['current_state']}, exposure={context['exposure']:.3f}."
        )

    def describe(self) -> Iterable[Dict[str, object]]:
        for rule in sorted(self.profile.rules, key=lambda item: item.priority):
            yield {
                "name": rule.name,
                "priority": rule.priority,
                "action": rule.action,
                "state": rule.target_state.value,
                "reason_code": rule.reason_code,
                "match": dict(rule.match),
            }

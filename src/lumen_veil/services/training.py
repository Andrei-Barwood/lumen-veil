from __future__ import annotations

from typing import Dict


class TrainingService:
    def review(self, report: Dict[str, object]) -> Dict[str, object]:
        final_states = report.get("final_states", {})
        contained = sum(1 for state in final_states.values() if state == "contained")
        released = sum(1 for state in final_states.values() if state == "released")
        exiled = sum(1 for state in final_states.values() if state == "exiled")
        score = max(0.0, 1.0 - exiled * 0.15 + released * 0.05 + contained * 0.08)
        return {
            "containment_count": contained,
            "release_count": released,
            "exile_count": exiled,
            "discipline_score": round(min(score, 1.0), 3),
        }

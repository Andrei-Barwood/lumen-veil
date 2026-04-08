import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lumen_veil.domain import AegisState, TransitCorridor, Vector2, Vessel


class DomainTests(unittest.TestCase):
    def test_corridor_distance_detects_inside_and_outside(self):
        corridor = TransitCorridor(
            name="test",
            jurisdiction="sorox",
            start=Vector2(10.0, 0.0),
            end=Vector2(-10.0, 0.0),
            width=5.0,
            sacred=False,
        )
        self.assertTrue(corridor.contains(Vector2(0.0, 2.0)))
        self.assertFalse(corridor.contains(Vector2(0.0, 8.0)))

    def test_state_transition_supports_containment_and_release(self):
        vessel = Vessel.from_dict(
            {
                "ident": "VT-1",
                "callsign": "Test",
                "allegiance": "neutral",
                "route": "test",
                "mass": 1.0,
                "thermal_signature": 0.2,
                "engine_signature": 0.2,
                "susceptibility": 0.4,
                "shielding": 0.3,
                "position": {"x": 0.0, "y": 0.0},
                "velocity": {"x": 0.0, "y": 0.0},
                "acceleration": {"x": 0.0, "y": 0.0},
            }
        )
        vessel.transition(AegisState.CONTAINED, "test.contained")
        vessel.transition(AegisState.RELEASED, "test.released")
        self.assertEqual(vessel.state, AegisState.RELEASED)


if __name__ == "__main__":
    unittest.main()

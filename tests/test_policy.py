import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lumen_veil.scenario import ScenarioBook
from lumen_veil.services.simulation import SimulationOrchestrator


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.book = ScenarioBook()

    def test_sorox_contains_unsealed_arrival(self):
        world = self.book.load("scenarios/sorox_unsealed_arrival.json")
        profile = self.book.load_profile(world.jurisdiction)
        report = SimulationOrchestrator(profile).run(world, steps=2)
        self.assertEqual(report["final_states"]["SV-001"], "contained")

    def test_vossk_minor_intrusion_is_shadowed_then_degraded(self):
        world = self.book.load("scenarios/vossk_minor_intrusion.json")
        profile = self.book.load_profile(world.jurisdiction)
        report = SimulationOrchestrator(profile).run(world, steps=2)
        self.assertEqual(report["ticks"][0]["decisions"]["VV-113"]["decision"]["action"], "shadow")
        self.assertEqual(report["final_states"]["VV-113"], "degraded")

    def test_convoy_anomaly_splits_release_and_shadow(self):
        world = self.book.load("scenarios/authorized_convoy_anomaly.json")
        profile = self.book.load_profile(world.jurisdiction)
        report = SimulationOrchestrator(profile).run(world, steps=4)
        self.assertEqual(report["final_states"]["SC-201"], "released")
        self.assertEqual(report["final_states"]["SC-202"], "shadowed")


if __name__ == "__main__":
    unittest.main()

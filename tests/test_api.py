import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lumen_veil.api import SimulationAPI


class APITests(unittest.TestCase):
    def test_api_lists_scenarios(self):
        api = SimulationAPI()
        payload = api.list_scenarios()
        self.assertGreaterEqual(len(payload["items"]), 6)

    def test_api_runs_scenario(self):
        api = SimulationAPI()
        payload = api.run("scenarios/vossk_minor_intrusion.json", steps=2, dt=1.0)
        self.assertEqual(payload["scenario"], "vossk_minor_intrusion")
        self.assertIn("final_states", payload)


if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lumen_veil.events import EventBus
from lumen_veil.scenario import ScenarioBook
from lumen_veil.services.simulation import SimulationOrchestrator


class EventTests(unittest.TestCase):
    def test_event_bus_replays_messages(self):
        bus = EventBus()
        seen = []
        bus.publish("ThresholdCrossed", {"tick": 1})
        bus.publish("GraceDenied", {"tick": 2})
        bus.replay(lambda event: seen.append(event.name))
        self.assertEqual(seen, ["ThresholdCrossed", "GraceDenied"])

    def test_replay_vault_captures_run_stream(self):
        book = ScenarioBook()
        world = book.load("scenarios/sorox_unsealed_arrival.json")
        profile = book.load_profile(world.jurisdiction)
        report = SimulationOrchestrator(profile).run(world, steps=2)
        self.assertEqual(report["replay"]["count"], len(report["events"]))
        self.assertIn("ContainmentRaised", report["replay"]["names"])


if __name__ == "__main__":
    unittest.main()

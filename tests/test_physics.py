import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lumen_veil.physics import PhysicsEngine
from lumen_veil.scenario import ScenarioBook


class PhysicsTests(unittest.TestCase):
    def test_physics_engine_advances_and_degrades_within_bounds(self):
        book = ScenarioBook()
        world = book.load("scenarios/sorox_unsealed_arrival.json")
        vessel = world.vessels[0]
        initial_x = vessel.position.x
        engine = PhysicsEngine()
        engine.advance(world, dt=1.0)
        self.assertLess(world.vessels[0].position.x, initial_x)
        self.assertGreaterEqual(world.vessels[0].systems.comms, 0.0)
        self.assertLessEqual(world.vessels[0].systems.comms, 1.0)
        self.assertGreater(world.vessels[0].exposure, 0.0)


if __name__ == "__main__":
    unittest.main()

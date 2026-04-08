import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lumen_veil.physics import _python_propagate


class PropertyStylePhysicsTests(unittest.TestCase):
    def test_shielding_reduces_exposure_over_random_samples(self):
        random.seed(7)
        for _ in range(50):
            susceptibility = random.uniform(0.2, 1.0)
            node = [(0.0, 0.0, 60.0, 0.5, 1.0, 1.0)]
            low_shield = [(20.0, 0.0, -1.0, 0.0, 0.0, 0.0, susceptibility, 0.1, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0)]
            high_shield = [(20.0, 0.0, -1.0, 0.0, 0.0, 0.0, susceptibility, 0.8, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0)]
            low = _python_propagate(low_shield, node, 1.0)[0]
            high = _python_propagate(high_shield, node, 1.0)[0]
            self.assertGreaterEqual(high[4], low[4])
            self.assertLessEqual(high[9], low[9])


if __name__ == "__main__":
    unittest.main()

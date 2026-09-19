"""Проверить симметрию, захват лучей и численную сходимость."""

import math
import unittest

from src.models.animation_model import Model


class ModelTests(unittest.TestCase):
    """Проверить расчёт траекторий независимо от Tkinter."""

    def test_zero_mass_is_straight(self):
        """Проверить прямолинейность света при отсутствии гравитации."""
        model = Model(0)
        for path in model.paths:
            self.assertFalse(path.captured)
            self.assertTrue(all(y == path.points[0][1]
                                for _, y in path.points))
            self.assertGreater(path.points[-1][0], model.LIMIT_X)

    def test_beam_is_mirror_symmetric(self):
        """Проверить зеркальную симметрию противоположных лучей."""
        model = Model(4)
        for lower, upper in zip(model.paths, reversed(model.paths)):
            self.assertEqual(lower.captured, upper.captured)
            self.assertEqual(len(lower.points), len(upper.points))
            for (x1, y1), (x2, y2) in zip(lower.points, upper.points):
                self.assertAlmostEqual(x1, x2)
                self.assertAlmostEqual(y1, -y2)

    def test_capture_and_escape(self):
        """Проверить захват центральных лучей и выход далёких лучей."""
        model = Model(4)
        self.assertTrue(model.paths[12].captured)
        self.assertFalse(model.paths[0].captured)
        for path in model.paths:
            if path.captured:
                self.assertAlmostEqual(math.hypot(*path.points[-1]), 8)
            self.assertTrue(all(math.isfinite(v)
                                for point in path.points for v in point))

    def test_mass_increases_capture(self):
        """Проверить увеличение числа захватов при увеличении массы."""
        small = sum(p.captured for p in Model(2).paths)
        large = sum(p.captured for p in Model(6).paths)
        self.assertGreater(large, small)

    def test_step_convergence(self):
        """Проверить сходимость угла при уменьшении шага RK4 вдвое."""
        model = Model(4)
        angles = []
        for step in (0.16, 0.08):
            path = model.trace(30, step)
            self.assertFalse(path.captured)
            first, last = path.points[-2:]
            angles.append(math.atan2(last[1] - first[1], last[0] - first[0]))
        self.assertAlmostEqual(*angles, places=4)

    def test_invalid_mass(self):
        """Проверить отклонение недопустимой массы без изменения модели."""
        model = Model(0)
        for mass in (-1, 9, math.nan, math.inf):
            with self.assertRaises(ValueError):
                model.set_mass(mass)
        self.assertEqual(model.mass, 0)


if __name__ == "__main__":
    unittest.main()

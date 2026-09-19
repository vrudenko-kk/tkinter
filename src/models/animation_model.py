"""Рассчитать плоские световые геодезические метрики Шварцшильда."""

from dataclasses import dataclass
from math import hypot, isfinite


@dataclass(frozen=True)
class PhotonPath:
    """Хранить точки траектории и признак захвата светового луча."""

    points: tuple[tuple[float, float], ...]
    captured: bool


class Model:
    """Рассчитать параллельный пучок в единицах, где G = c = 1."""

    STEP = 0.16
    MAX_STEPS = 2200
    START_X = -72.0
    LIMIT_X = 80.0
    LIMIT_Y = 48.0

    def __init__(self, mass: float = 4.0):
        self.mass = 0.0
        self.paths: list[PhotonPath] = []
        self.set_mass(mass)

    @property
    def horizon_radius(self) -> float:
        """Вернуть радиус Шварцшильда в единицах модели."""
        return 2.0 * self.mass

    def set_mass(self, mass: float) -> None:
        """Проверить массу и пересчитать пучок от конечного источника."""
        if not isfinite(mass) or not 0.0 <= mass <= 8.0:
            raise ValueError("Mass must be finite and between 0 and 8.")
        self.mass = float(mass)
        self.paths = [self.trace(index * 3.0) for index in range(-12, 13)]

    def trace(self, offset: float, step: float = STEP) -> PhotonPath:
        """Рассчитать путь горизонтального луча до захвата или выхода."""
        if not isfinite(offset) or not isfinite(step) or step <= 0:
            raise ValueError("Offset and positive step must be finite.")
        state = (self.START_X, float(offset), 1.0, 0.0)
        angular_momentum = -offset
        points = [(state[0], state[1])]
        for _ in range(self.MAX_STEPS):
            x, y, _, _ = state
            radius = hypot(x, y)
            if self.mass > 0 and radius <= self.horizon_radius:
                return PhotonPath(tuple(points), True)
            if abs(x) > self.LIMIT_X or abs(y) > self.LIMIT_Y:
                break
            # Уменьшаем шаг у горизонта для расчёта захвата и поворотов.
            dt = min(step, 0.03 * radius) if self.mass else step
            next_state = self._rk4(state, dt, angular_momentum)
            nx, ny = next_state[:2]
            if self.mass and hypot(nx, ny) <= self.horizon_radius:
                # Уточняем конец пути пересечением отрезка с r = 2M.
                dx, dy = nx - x, ny - y
                a = dx * dx + dy * dy
                b = 2 * (x * dx + y * dy)
                c = radius * radius - self.horizon_radius ** 2
                fraction = (-b - (b * b - 4 * a * c) ** 0.5) / (2 * a)
                points.append((x + fraction * dx, y + fraction * dy))
                return PhotonPath(tuple(points), True)
            state = next_state
            points.append((nx, ny))
        return PhotonPath(tuple(points), False)

    def _derivative(self, state, angular_momentum):
        x, y, vx, vy = state
        if not self.mass:
            return vx, vy, 0.0, 0.0
        radius = hypot(x, y)
        # Плоская световая геодезическая: r'' = -3 M L² r / |r|⁵.
        # Производные берутся по аффинному параметру, а не по времени.
        factor = -3 * self.mass * angular_momentum ** 2 / radius ** 5
        return vx, vy, factor * x, factor * y

    def _rk4(self, state, step, angular_momentum):
        def shifted(derivative, scale):
            return tuple(s + scale * d for s, d in zip(state, derivative))

        k1 = self._derivative(state, angular_momentum)
        k2 = self._derivative(shifted(k1, step / 2), angular_momentum)
        k3 = self._derivative(shifted(k2, step / 2), angular_momentum)
        k4 = self._derivative(shifted(k3, step), angular_momentum)
        return tuple(
            s + step * (a + 2 * b + 2 * c + d) / 6
            for s, a, b, c, d in zip(state, k1, k2, k3, k4)
        )

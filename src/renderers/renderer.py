"""Отобразить координатную сетку и следы фотонов на холсте Tkinter."""

import tkinter as tk

from src.models.animation_model import Model


class Renderer:
    """Отрисовать масштабируемую сцену без изменения физической модели."""

    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.scale = 1.0
        self.center = (0.0, 0.0)
        self.items = []

    def _point(self, point):
        x, y = point
        return (self.center[0] + x * self.scale,
                self.center[1] - y * self.scale)

    def _circle(self, radius, **options):
        x, y = self.center
        radius *= self.scale
        return self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius, **options
        )

    def rebuild(self, model: Model, show_paths: bool) -> None:
        """Перестроить сцену после изменения размеров окна или настроек."""
        canvas = self.canvas
        canvas.delete("all")
        width, height = canvas.winfo_width(), canvas.winfo_height()
        self.scale = min(width / 164, height / 102)
        self.center = (width / 2, height / 2)
        self.items = []
        for x in range(-80, 81, 10):
            canvas.create_line(*self._point((x, -48)),
                               *self._point((x, 48)), fill="#142232")
        for y in range(-40, 41, 10):
            canvas.create_line(*self._point((-80, y)),
                               *self._point((80, y)), fill="#142232")
        if model.mass:
            self._circle(3 * model.mass, outline="#b78955", dash=(4, 5))
            self._circle(model.horizon_radius + 0.5, fill="#684626",
                         outline="")
            self._circle(model.horizon_radius, fill="#020409",
                         outline="#edb775", width=2)
        for path in model.paths:
            if show_paths:
                coords = [v for p in path.points[::3] for v in self._point(p)]
                if len(coords) >= 4:
                    canvas.create_line(*coords, fill="#234957", width=1)
            trail = canvas.create_line(0, 0, 0, 0, fill="#58cbe0", width=2)
            dot = canvas.create_oval(0, 0, 0, 0, fill="#e3fbff", outline="")
            self.items.append((trail, dot))
        canvas.create_text(
            20, 20, anchor="nw", text="ПАРАЛЛЕЛЬНЫЙ ПУЧОК  →",
            fill="#90b9cc", font=("Helvetica", 11, "bold")
        )
        canvas.create_text(
            20, height - 22, anchor="w", fill="#8197ab",
            text="Бирюзовый — свет   ·   Золотой — горизонт   ·   "
                 "Пунктир — фотонная сфера (r = 3M)"
        )

    def draw(self, model: Model, position: float) -> None:
        """Переместить волну фотонов вдоль рассчитанных траекторий."""
        cycle = max(len(path.points) for path in model.paths) + 100
        index = int(position) % cycle
        for path, (trail, dot) in zip(model.paths, self.items):
            if index >= len(path.points):
                self.canvas.itemconfigure(trail, state="hidden")
                self.canvas.itemconfigure(dot, state="hidden")
                continue
            self.canvas.itemconfigure(dot, state="normal")
            x, y = self._point(path.points[index])
            self.canvas.coords(dot, x - 3, y - 3, x + 3, y + 3)
            points = path.points[max(0, index - 65):index + 1:2]
            if len(points) > 1:
                self.canvas.itemconfigure(trail, state="normal")
                coords = [v for point in points for v in self._point(point)]
                self.canvas.coords(trail, *coords)
            else:
                self.canvas.itemconfigure(trail, state="hidden")

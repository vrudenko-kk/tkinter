"""Связать окно, математическую модель и таймер анимации."""

import time
import tkinter as tk
from tkinter import ttk

from src.models.animation_model import Model
from src.renderers.renderer import Renderer
from src.widgets.controls import Controls


class App:
    """Управлять симуляцией чёрной дыры и обработкой событий."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Чёрная дыра · Лаборатория света")
        self.root.geometry("1120x760")
        self.root.minsize(850, 580)
        self.root.configure(bg="#0b1420")
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background="#142232")
        style.configure("TLabel", background="#142232", foreground="#deebf5")
        style.configure("TCheckbutton", background="#142232",
                        foreground="#deebf5")
        tk.Label(self.root, text="ЧЁРНАЯ ДЫРА / лаборатория света",
                 bg="#0b1420", fg="#e1edf5", anchor="w",
                 font=("Helvetica", 22, "bold"), padx=22, pady=16).pack(
                     fill="x"
                 )
        self.model = Model()
        self.position = 0.0
        self.paused = False
        self._mass_job = None
        self._frame_job = None
        self.controls = Controls(self.root, self._change_mass,
                                 self.toggle_pause, self.reset, self._redraw)
        self.controls.pack(side="bottom", fill="x")
        self.status = tk.Label(self.root, bg="#0b1420", fg="#90a8bc",
                               anchor="w", padx=22, pady=8)
        self.status.pack(side="bottom", fill="x")
        self.canvas = tk.Canvas(self.root, bg="#0b1420", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.renderer = Renderer(self.canvas)
        self.canvas.bind("<Configure>", lambda event: self._redraw())
        self.root.bind("<space>", lambda event: self.toggle_pause())
        self.root.bind("<Key-r>", lambda event: self.reset())
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self._last_time = time.perf_counter()
        self._tick()

    def run(self) -> None:
        """Запустить обработку событий окна."""
        self.root.mainloop()

    def toggle_pause(self) -> None:
        """Приостановить или продолжить анимацию без изменения траекторий."""
        self.paused = not self.paused
        self.controls.pause_button.configure(
            text="Продолжить" if self.paused else "Пауза"
        )

    def reset(self) -> None:
        """Вернуть волну фотонов к источнику, сохранив настройки."""
        self.position = 0.0
        self.renderer.draw(self.model, self.position)

    def close(self) -> None:
        """Отменить запланированные вызовы и закрыть окно."""
        for job in (self._frame_job, self._mass_job):
            if job is not None:
                self.root.after_cancel(job)
        self.root.destroy()

    def _change_mass(self, value):
        self.controls.mass_label.configure(
            text=f"Масса: {float(value):.1f} M₀"
        )
        if self._mass_job is not None:
            self.root.after_cancel(self._mass_job)
        self._mass_job = self.root.after(150, self._apply_mass)

    def _apply_mass(self):
        self._mass_job = None
        self.model.set_mass(self.controls.mass.get())
        self.position = 0.0
        self._last_time = time.perf_counter()
        self._redraw()

    def _redraw(self):
        self.renderer.rebuild(self.model, self.controls.show_paths.get())
        self.renderer.draw(self.model, self.position)
        captured = sum(path.captured for path in self.model.paths)
        self.status.configure(
            text=f"rₛ = {self.model.horizon_radius:.1f}  ·  "
                 f"Захват: {captured} из 25 лучей  ·  "
                 "Пробел — пауза   /   R — заново   ·   G = c = 1"
        )

    def _tick(self):
        now = time.perf_counter()
        elapsed = min(now - self._last_time, 0.1)
        self._last_time = now
        if not self.paused:
            self.position += elapsed * 140 * self.controls.speed.get()
        self.renderer.draw(self.model, self.position)
        self._frame_job = self.root.after(16, self._tick)

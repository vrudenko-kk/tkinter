"""Создать панель управления симуляцией."""

import tkinter as tk
from tkinter import ttk


class Controls(ttk.Frame):
    """Объединить элементы управления и их текущие значения."""

    def __init__(self, parent, on_mass, on_pause, on_reset, on_paths):
        super().__init__(parent, padding=(22, 16))
        self.mass = tk.DoubleVar(value=4.0)
        self.speed = tk.DoubleVar(value=1.0)
        self.show_paths = tk.BooleanVar(value=True)
        self.mass_label = ttk.Label(self, text="Масса: 4.0 M₀")
        self.mass_label.grid(row=0, column=0, sticky="w")
        ttk.Scale(self, from_=0, to=8, variable=self.mass,
                  command=on_mass).grid(row=1, column=0, sticky="ew")
        ttk.Label(self, text="Скорость: 0.25–3×").grid(
            row=0, column=1, sticky="w", padx=24
        )
        ttk.Scale(self, from_=0.25, to=3, variable=self.speed).grid(
            row=1, column=1, sticky="ew", padx=24
        )
        self.pause_button = ttk.Button(self, text="Пауза", command=on_pause)
        self.pause_button.grid(row=0, column=2, rowspan=2, padx=8)
        ttk.Button(self, text="Заново", command=on_reset).grid(
            row=0, column=3, rowspan=2, padx=8
        )
        ttk.Checkbutton(self, text="Траектории", variable=self.show_paths,
                        command=on_paths).grid(row=0, column=4, rowspan=2)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)

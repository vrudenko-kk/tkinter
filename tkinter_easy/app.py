"""Показать узоры умножения точек на окружности."""

import colorsys
import math
import tkinter as tk
from tkinter import ttk


def multiplication_lines(count, multiplier):
    """Вернуть концы хорд в координатах единичной окружности."""
    lines = []
    for index in range(count):
        # Остаток возвращает результат умножения на ту же окружность.
        # Дробный множитель задаёт конец хорды между отмеченными точками.
        start = math.tau * index / count - math.pi / 2
        end = math.tau * ((index * multiplier) % count) / count
        end -= math.pi / 2
        lines.append((math.cos(start), math.sin(start),
                      math.cos(end), math.sin(end)))
    return lines


class CircleView(tk.Canvas):
    """Нарисовать таблицу умножения хордами между точками окружности."""

    def __init__(self, parent, multiplier=2.0, count=240,
                 animated=False, **options):
        super().__init__(parent, bg="#101827", highlightthickness=0,
                         **options)
        self.multiplier = multiplier
        self.count = count
        self.animated = animated
        self._animation_job = None
        self._lines = []
        self._visible_count = 0 if animated else count
        self.bind("<Configure>",
                  lambda event: self.redraw(restart=False))

    def redraw(self, multiplier=None, restart=True):
        """Обновить узор, при необходимости начав анимацию заново."""
        self.stop_animation()
        if restart:
            self._visible_count = 0 if self.animated else self.count
        self._lines = []
        if multiplier is not None:
            self.multiplier = multiplier
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        cx, cy = width / 2, height / 2
        radius = max(1, min(width, height) / 2 - 15)
        self.create_oval(cx - radius, cy - radius,
                         cx + radius, cy + radius, outline="#60748a")
        for index, (x1, y1, x2, y2) in enumerate(
            multiplication_lines(self.count, self.multiplier)
        ):
            red, green, blue = colorsys.hsv_to_rgb(
                0.46 + 0.32 * index / self.count, 0.62, 0.95
            )
            color = f"#{int(red * 255):02x}"
            color += f"{int(green * 255):02x}{int(blue * 255):02x}"
            line = self.create_line(
                cx + radius * x1, cy + radius * y1,
                cx + radius * x2, cy + radius * y2, fill=color,
                state="normal" if index < self._visible_count else "hidden"
            )
            self._lines.append(line)
            self.create_oval(cx + radius * x1 - 1,
                             cy + radius * y1 - 1,
                             cx + radius * x1 + 1,
                             cy + radius * y1 + 1,
                             fill="#dbeafe", outline="")

        if self._visible_count < self.count:
            self._animation_job = self.after(25, self._animate)

    def stop_animation(self):
        """Отменить ожидающий кадр анимации."""
        if self._animation_job is not None:
            self.after_cancel(self._animation_job)
            self._animation_job = None

    def _animate(self):
        self._animation_job = None
        # Показываем по три хорды за кадр: весь узор займёт около 2 с.
        end = min(self._visible_count + 3, self.count)
        for index in range(self._visible_count, end):
            self.itemconfigure(self._lines[index], state="normal")
        self._visible_count = end
        if end < self.count:
            self._animation_job = self.after(25, self._animate)


class App:
    """Связать главное окно, слайдер и галерею готовых узоров."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Умножение на окружности")
        self.root.geometry("860x800")
        self.root.minsize(640, 650)
        self.root.configure(bg="#101827")
        self.multiplier = tk.DoubleVar(value=2.0)
        self._redraw_job = None
        title = tk.Label(
            self.root, text="Умножение на окружности", bg="#101827",
            fg="#edf4ff", font=("Helvetica", 22, "bold"), pady=12
        )
        title.pack()
        tk.Label(self.root, text="240 точек · соединяем k и (k × m) mod 240",
                 bg="#101827", fg="#a5b6cc").pack()
        self.view = CircleView(self.root, animated=True)
        self.view.pack(fill="both", expand=True, padx=12, pady=8)
        panel = ttk.Frame(self.root, padding=(18, 8))
        panel.pack(fill="x")
        self.value_label = ttk.Label(panel, text="Множитель: 2.00")
        self.value_label.pack(side="left")
        self.slider = ttk.Scale(
            panel, from_=0, to=12, variable=self.multiplier,
            command=self._schedule_redraw
        )
        self.slider.pack(side="left", fill="x", expand=True, padx=16)
        ttk.Button(panel, text="Кардиоида ×2",
                   command=lambda: self.select(2)).pack(side="right")
        ttk.Button(panel, text="Повторить",
                   command=self._schedule_redraw).pack(side="right", padx=6)
        tk.Label(self.root, text="Готовые узоры — нажмите для просмотра",
                 bg="#101827", fg="#a5b6cc", pady=8).pack()
        gallery = tk.Frame(self.root, bg="#101827")
        gallery.pack(fill="x", padx=12, pady=(0, 12))
        self.previews = []
        for column, (multiplier, name) in enumerate(
            ((2, "Кардиоида"), (3, "Нефроида"),
             (4, "Три лепестка"), (7, "Шесть лепестков"))
        ):
            gallery.columnconfigure(column, weight=1, uniform="preview")
            tile = tk.Frame(gallery, bg="#101827")
            tile.grid(row=0, column=column, sticky="ew", padx=4)
            preview = CircleView(tile, multiplier, count=180,
                                 width=140, height=140, cursor="hand2")
            preview.pack(fill="x")
            preview.bind("<Button-1>",
                         lambda event, m=multiplier: self.select(m))
            ttk.Button(tile, text=f"×{multiplier} · {name}",
                       command=lambda m=multiplier: self.select(m)).pack(
                           fill="x"
                       )
            self.previews.append(preview)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def run(self):
        """Запустить обработку событий окна."""
        self.root.mainloop()

    def select(self, multiplier):
        """Выбрать множитель из галереи и обновить главное изображение."""
        self.multiplier.set(multiplier)
        self._schedule_redraw()

    def close(self):
        """Отменить отложенную отрисовку и закрыть окно."""
        if self._redraw_job is not None:
            self.root.after_cancel(self._redraw_job)
        self.view.stop_animation()
        self.root.destroy()

    def _schedule_redraw(self, value=None):
        self.value_label.configure(
            text=f"Множитель: {self.multiplier.get():.2f}"
        )
        # Объединяем частые события слайдера в один кадр отрисовки.
        if self._redraw_job is None:
            self._redraw_job = self.root.after(16, self._redraw)

    def _redraw(self):
        self._redraw_job = None
        self.view.redraw(self.multiplier.get())

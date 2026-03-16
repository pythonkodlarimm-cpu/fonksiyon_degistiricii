# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/kart.py

ROL:
- Uygulama genelinde ortak kart görünümü sağlar
- Tek tip radius, border ve arka plan dili oluşturur

SURUM: 2
TARIH: 2026-03-16
IMZA: FY.
"""

from __future__ import annotations

from kivy.graphics import Color
from kivy.graphics import Line
from kivy.graphics import RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout


class Kart(BoxLayout):
    def __init__(
        self,
        bg=(0.08, 0.11, 0.16, 1),
        border=(0.18, 0.21, 0.27, 1),
        radius=16,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._bg = tuple(bg)
        self._border = tuple(border)
        self._radius = float(radius)

        with self.canvas.before:
            self._bg_color = Color(*self._bg)
            self._bg_rect = RoundedRectangle(radius=[dp(self._radius)])

        with self.canvas.after:
            self._border_color = Color(*self._border)
            self._border_line = Line(
                rounded_rectangle=(0, 0, 0, 0, dp(self._radius)),
                width=1.05,
            )

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

    def _update_canvas(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._border_line.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(self._radius),
        )

    def set_bg_rgba(self, rgba) -> None:
        try:
            self._bg_color.rgba = tuple(rgba)
        except Exception:
            pass

    def set_border_rgba(self, rgba) -> None:
        try:
            self._border_color.rgba = tuple(rgba)
        except Exception:
            pass

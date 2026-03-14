# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/kart.py
ROL:
- Ortak kart/panel görünümü
- İçeriğin üstünü kapatmayan sade arka plan katmanı sağlar
"""

from __future__ import annotations

from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout


class Kart(BoxLayout):
    """
    Ortak kart bileşeni.

    Özellikler:
    - sadece canvas.before kullanır
    - içeriği kapatmaz
    - yuvarlatılmış arka plan çizer
    """

    def __init__(self, bg=(0.16, 0.16, 0.20, 1), radius=18, **kwargs):
        super().__init__(**kwargs)

        self._bg_rgba = tuple(bg)
        self._radius = float(radius)

        with self.canvas.before:
            self._bg_color = Color(*self._bg_rgba)
            self.bg_rect = RoundedRectangle(radius=[dp(self._radius)])

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

    def _update_canvas(self, *_args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def set_bg(self, rgba) -> None:
        self._bg_rgba = tuple(rgba)
        self._bg_color.rgba = self._bg_rgba
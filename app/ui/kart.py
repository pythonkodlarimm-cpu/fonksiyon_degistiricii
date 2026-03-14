# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/kart.py
ROL:
- Ortak kart/panel görünümü
- İçeriğin üstünü kapatmayan sade arka plan katmanı sağlar

APK / ANDROID NOTLARI:
- Sadece canvas.before kullanır
- İçeriği kapatmaz
- Boyut/konum değişimlerinde güvenli şekilde yeniden çizilir
"""

from __future__ import annotations

from kivy.graphics import Color
from kivy.graphics import RoundedRectangle
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

        self._bg_rgba = self._normalize_rgba(bg, fallback=(0.16, 0.16, 0.20, 1))
        self._radius = self._normalize_radius(radius, fallback=18)

        with self.canvas.before:
            self._bg_color = Color(*self._bg_rgba)
            self.bg_rect = RoundedRectangle(radius=[dp(self._radius)])

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

    def _normalize_rgba(self, rgba, fallback=(0.16, 0.16, 0.20, 1)):
        try:
            veri = tuple(rgba)
            if len(veri) != 4:
                return tuple(fallback)
            return veri
        except Exception:
            return tuple(fallback)

    def _normalize_radius(self, radius, fallback=18):
        try:
            return float(radius)
        except Exception:
            return float(fallback)

    def _update_canvas(self, *_args):
        try:
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
            self.bg_rect.radius = [dp(self._radius)]
        except Exception:
            pass

    def set_bg(self, rgba) -> None:
        self._bg_rgba = self._normalize_rgba(rgba, fallback=self._bg_rgba)
        try:
            self._bg_color.rgba = self._bg_rgba
        except Exception:
            pass

    def set_radius(self, radius) -> None:
        self._radius = self._normalize_radius(radius, fallback=self._radius)
        self._update_canvas()
# -*- coding: utf-8 -*-
from __future__ import annotations

import math

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image


class TiklanabilirIcon(ButtonBehavior, Image):
    pass


class AnimatedSeparator(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(6),
            **kwargs,
        )

        self._phase = 0.0
        self._segment_count = 7
        self._segment_colors = []
        self._segment_rects = []
        self._anim_event = None

        with self.canvas.before:
            for _ in range(self._segment_count):
                color = Color(1, 1, 1, 1)
                rect = RoundedRectangle(radius=[dp(4)])
                self._segment_colors.append(color)
                self._segment_rects.append(rect)

        self.bind(pos=self._update_graphics, size=self._update_graphics)
        self._update_graphics()
        self._start_animation()

    def _update_graphics(self, *_args):
        if self._segment_count <= 0:
            return

        bosluk = dp(3)
        toplam_bosluk = bosluk * (self._segment_count - 1)
        parca_genislik = max(1.0, (self.width - toplam_bosluk) / self._segment_count)

        x = self.x
        for rect in self._segment_rects:
            rect.pos = (x, self.y)
            rect.size = (parca_genislik, self.height)
            x += parca_genislik + bosluk

    def _animate(self, dt):
        self._phase += dt * 3.2

        for i, color in enumerate(self._segment_colors):
            p = self._phase + (i * 0.55)
            r = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(p + 0.0))
            g = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(p + 2.1))
            b = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(p + 4.2))
            color.rgba = (r, g, b, 1)

    def _start_animation(self):
        self._stop_animation()
        self._anim_event = Clock.schedule_interval(self._animate, 1 / 24)

    def _stop_animation(self):
        try:
            if self._anim_event is not None:
                self._anim_event.cancel()
        except Exception:
            pass
        self._anim_event = None

    def on_parent(self, _instance, parent):
        if parent is None:
            self._stop_animation()
        elif self._anim_event is None:
            self._start_animation()


def start_icon_glow(widget, size_small_dp=36, size_big_dp=40, duration=0.60):
    try:
        anim = (
            Animation(opacity=0.72, size=(dp(size_big_dp), dp(size_big_dp)), duration=duration)
            + Animation(opacity=1.0, size=(dp(size_small_dp), dp(size_small_dp)), duration=duration)
        )
        anim.repeat = True
        anim.start(widget)
        return anim
    except Exception:
        return None
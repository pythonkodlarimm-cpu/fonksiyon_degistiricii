# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tarama_gostergesi_paketi/loading_overlay.py
"""

from __future__ import annotations

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import (
    Color,
    PopMatrix,
    PushMatrix,
    Rectangle,
    Rotate,
    RoundedRectangle,
    Translate,
)
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from app.ui.icon_yardimci import icon_path
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY


class DonenYuklemeIkonu(Widget):
    angle = NumericProperty(0.0)
    speed_factor = NumericProperty(1.0)

    def __init__(
        self,
        source: str = "",
        size_dp: int = 72,
        deg_per_sec: float = 220.0,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.size_hint = (None, None)
        self.size = (dp(size_dp), dp(size_dp))

        self._deg_per_sec = float(deg_per_sec)
        self._event = None
        self._slow_anim = None

        self._img = Image(
            source=str(source or ""),
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(None, None),
        )
        self.add_widget(self._img)

        with self.canvas.before:
            PushMatrix()
            self._tr1 = Translate(0, 0, 0)
            self._rot = Rotate(angle=0.0, axis=(0, 0, 1), origin=(0, 0))
            self._tr2 = Translate(0, 0, 0)

        with self.canvas.after:
            PopMatrix()

        self.bind(pos=self._sync, size=self._sync, angle=self._sync_angle)
        self._sync()

    def set_source(self, source: str) -> None:
        try:
            self._img.source = str(source or "")
        except Exception:
            pass

    def start(self) -> None:
        self._cancel_slow_anim()

        try:
            self.speed_factor = 1.0
        except Exception:
            pass

        if self._event is not None:
            return

        def _tick(dt):
            try:
                hiz = float(self.speed_factor or 0.0)
                self.angle = (
                    float(self.angle)
                    + (self._deg_per_sec * hiz * float(dt))
                ) % 360.0
            except Exception:
                pass

        self._event = Clock.schedule_interval(_tick, 1 / 60.0)

    def finish_then_stop(self, on_done=None) -> None:
        self.start()
        self._cancel_slow_anim()

        def _finish(*_args):
            self.stop()
            try:
                if on_done is not None:
                    on_done()
            except Exception:
                pass

        try:
            anim = Animation(speed_factor=0.10, duration=0.42) + Animation(
                speed_factor=0.0,
                duration=0.22,
            )
            anim.bind(on_complete=lambda *_: _finish())
            anim.start(self)
            self._slow_anim = anim
        except Exception:
            self.stop()
            try:
                if on_done is not None:
                    on_done()
            except Exception:
                pass

    def stop(self) -> None:
        self._cancel_slow_anim()

        try:
            if self._event is not None:
                self._event.cancel()
        except Exception:
            pass

        self._event = None

        try:
            self.speed_factor = 1.0
            self.angle = 0.0
        except Exception:
            pass

    def _cancel_slow_anim(self) -> None:
        try:
            if self._slow_anim is not None:
                self._slow_anim.cancel(self)
        except Exception:
            pass
        self._slow_anim = None

    def _sync(self, *_args) -> None:
        try:
            self._img.pos = self.pos
            self._img.size = self.size
        except Exception:
            pass
        self._sync_angle()

    def _sync_angle(self, *_args) -> None:
        try:
            cx = self.x + (self.width / 2.0)
            cy = self.y + (self.height / 2.0)

            self._tr1.x = cx
            self._tr1.y = cy
            self._rot.origin = (0, 0)
            self._rot.angle = float(self.angle)
            self._tr2.x = -cx
            self._tr2.y = -cy
        except Exception:
            pass


class TaramaLoadingOverlay(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(
            size_hint=(1, 1),
            opacity=0,
            disabled=True,
            **kwargs,
        )

        self._fade_anim = None

        with self.canvas.before:
            self._overlay_color = Color(0, 0, 0, 0.50)
            self._overlay_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_overlay_canvas, size=self._update_overlay_canvas)

        self.card = FloatLayout(
            size_hint=(None, None),
            size=(dp(220), dp(185)),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.add_widget(self.card)

        with self.card.canvas.before:
            self._card_color = Color(0.08, 0.11, 0.16, 0.98)
            self._card_rect = RoundedRectangle(
                pos=self.card.pos,
                size=self.card.size,
                radius=[dp(24)],
            )

        self.card.bind(pos=self._update_card_canvas, size=self._update_card_canvas)

        self.spinner_wrap = FloatLayout(
            size_hint=(None, None),
            size=(dp(88), dp(88)),
            pos_hint={"center_x": 0.5, "center_y": 0.68},
        )
        self.card.add_widget(self.spinner_wrap)

        self.spinner_icon = DonenYuklemeIkonu(
            source=icon_path("yuvarlak.png"),
            size_dp=72,
            deg_per_sec=240.0,
        )
        self.spinner_wrap.add_widget(self.spinner_icon)
        self.spinner_wrap.bind(pos=self._layout_spinner, size=self._layout_spinner)

        self.title_label = Label(
            text="Taranıyor...",
            color=TEXT_PRIMARY,
            font_size="18sp",
            bold=True,
            size_hint=(None, None),
            size=(dp(180), dp(28)),
            pos_hint={"center_x": 0.5, "center_y": 0.32},
            halign="center",
            valign="middle",
        )
        self.title_label.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        self.card.add_widget(self.title_label)

        self.detail_label = Label(
            text="Fonksiyonlar analiz ediliyor",
            color=TEXT_MUTED,
            font_size="12sp",
            size_hint=(None, None),
            size=(dp(190), dp(22)),
            pos_hint={"center_x": 0.5, "center_y": 0.18},
            halign="center",
            valign="middle",
        )
        self.detail_label.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        self.card.add_widget(self.detail_label)

        self._layout_spinner()

    def on_touch_down(self, touch):
        if self.disabled or self.opacity <= 0:
            return False
        return True

    def on_touch_move(self, touch):
        if self.disabled or self.opacity <= 0:
            return False
        return True

    def on_touch_up(self, touch):
        if self.disabled or self.opacity <= 0:
            return False
        return True

    def _layout_spinner(self, *_args) -> None:
        try:
            self.spinner_icon.pos = (
                self.spinner_wrap.center_x - (self.spinner_icon.width / 2.0),
                self.spinner_wrap.center_y - (self.spinner_icon.height / 2.0),
            )
        except Exception:
            pass

    def _update_overlay_canvas(self, *_args):
        try:
            self._overlay_rect.pos = self.pos
            self._overlay_rect.size = self.size
        except Exception:
            pass

    def _update_card_canvas(self, *_args):
        try:
            self._card_rect.pos = self.card.pos
            self._card_rect.size = self.card.size
        except Exception:
            pass

    def _cancel_fade_anim(self) -> None:
        try:
            if self._fade_anim is not None:
                self._fade_anim.cancel(self)
        except Exception:
            pass
        self._fade_anim = None

    def show(
        self,
        title: str = "Taranıyor...",
        detail: str = "Fonksiyonlar analiz ediliyor",
    ) -> None:
        self._cancel_fade_anim()

        try:
            self.title_label.text = str(title or "Taranıyor...")
            self.detail_label.text = str(detail or "Fonksiyonlar analiz ediliyor")
        except Exception:
            pass

        try:
            self.opacity = 1
            self.disabled = False
        except Exception:
            pass

        try:
            self._layout_spinner()
            self.spinner_icon.start()
        except Exception:
            pass

    def finish_and_hide(self, on_done=None) -> None:
        self._cancel_fade_anim()

        def _after_spin():
            def _finish(*_args):
                try:
                    self.opacity = 0
                    self.disabled = True
                except Exception:
                    pass

                try:
                    if on_done is not None:
                        on_done()
                except Exception:
                    pass

            try:
                anim = Animation(opacity=0.0, duration=0.10)
                anim.bind(on_complete=lambda *_: _finish())
                anim.start(self)
                self._fade_anim = anim
            except Exception:
                _finish()

        try:
            self.spinner_icon.finish_then_stop(on_done=_after_spin)
        except Exception:
            try:
                self.spinner_icon.stop()
            except Exception:
                pass
            _after_spin()

    def hide(self) -> None:
        self._cancel_fade_anim()
        try:
            self.spinner_icon.stop()
        except Exception:
            pass

        try:
            self.opacity = 0
            self.disabled = True
        except Exception:
            pass

    def hide_immediately(self) -> None:
        self.hide()
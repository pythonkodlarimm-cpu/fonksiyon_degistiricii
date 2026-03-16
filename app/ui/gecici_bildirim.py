# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/gecici_bildirim.py

ROL:
- Ekran üzerinde geçici bildirim gösterir
- İkon + kısa metin taşır
- Otomatik kapanır
- Çift dokunma ile hemen kapanır

MİMARİ:
- Sadece görünüm ve animasyon içerir
- İş mantığı servis dışından tetiklenir
- Root içine overlay olarak eklenir

SURUM: 2
TARIH: 2026-03-16
IMZA: FY.
"""

from __future__ import annotations

import time

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

from app.ui.icon_yardimci import icon_path
from app.ui.kart import Kart
from app.ui.tema import TEXT_PRIMARY


class _DokunmatikBildirim(ButtonBehavior, Kart):
    def __init__(self, on_double_tap=None, **kwargs):
        super().__init__(
            orientation="horizontal",
            spacing=dp(8),
            padding=(dp(12), dp(10), dp(12), dp(10)),
            size_hint=(None, None),
            size=(dp(320), dp(54)),
            bg=(0.08, 0.11, 0.16, 0.97),
            border=(0.22, 0.26, 0.33, 1),
            radius=16,
            **kwargs,
        )

        self.on_double_tap = on_double_tap
        self._last_tap_ts = 0.0

        self.icon = Image(
            source="",
            size_hint=(None, None),
            size=(dp(22), dp(22)),
            opacity=0,
            allow_stretch=True,
            keep_ratio=True,
        )
        self.add_widget(self.icon)

        self.label = Label(
            text="",
            color=TEXT_PRIMARY,
            halign="left",
            valign="middle",
            font_size="13sp",
            shorten=True,
            shorten_from="right",
        )
        self.label.bind(size=self._sync_label_size)
        self.add_widget(self.label)

    def _sync_label_size(self, widget, size):
        widget.text_size = (size[0], size[1])

    def set_message(self, text: str, icon_name: str = "") -> None:
        self.label.text = str(text or "").strip()

        if icon_name:
            try:
                p = icon_path(icon_name)
            except Exception:
                p = ""

            if p:
                self.icon.source = p
                self.icon.opacity = 1
                try:
                    self.icon.reload()
                except Exception:
                    pass
                return

        self.icon.source = ""
        self.icon.opacity = 0

    def on_press(self):
        now = time.time()
        fark = now - self._last_tap_ts
        self._last_tap_ts = now

        if fark <= 0.35:
            try:
                if self.on_double_tap is not None:
                    self.on_double_tap()
            except Exception:
                pass


class GeciciBildirimKatmani(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint=(1, 1),
            padding=(dp(10), dp(10), dp(10), dp(84)),
            **kwargs,
        )

        self._hide_event = None
        self._current_anim = None

        self.anchor = BoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
        )
        self.add_widget(self.anchor)

        alt = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(64),
        )
        self.anchor.add_widget(alt)

        alt.add_widget(Label(size_hint_x=1))

        self.toast = _DokunmatikBildirim(
            on_double_tap=self.hide_immediately,
        )
        self.toast.opacity = 0
        self.toast.disabled = True
        alt.add_widget(self.toast)

        alt.add_widget(Label(size_hint_x=1))

    def _cancel_hide_event(self):
        try:
            if self._hide_event is not None:
                self._hide_event.cancel()
        except Exception:
            pass
        self._hide_event = None

    def _cancel_anim(self):
        try:
            if self._current_anim is not None:
                self._current_anim.cancel(self.toast)
        except Exception:
            pass
        self._current_anim = None

    def show(self, text: str, icon_name: str = "", duration: float = 2.4):
        self._cancel_hide_event()
        self._cancel_anim()

        self.toast.set_message(text, icon_name=icon_name)
        self.toast.disabled = False

        try:
            self.toast.opacity = 0
            anim = Animation(opacity=1.0, duration=0.18)
            anim.start(self.toast)
            self._current_anim = anim
        except Exception:
            self.toast.opacity = 1.0

        self._hide_event = Clock.schedule_once(
            lambda *_: self.hide(),
            max(0.4, float(duration)),
        )

    def hide(self):
        self._cancel_hide_event()
        self._cancel_anim()

        def _finish(*_args):
            try:
                self.toast.opacity = 0
                self.toast.disabled = True
            except Exception:
                pass

        try:
            anim = Animation(opacity=0.0, duration=0.18)
            anim.bind(on_complete=lambda *_: _finish())
            anim.start(self.toast)
            self._current_anim = anim
        except Exception:
            _finish()

    def hide_immediately(self):
        self._cancel_hide_event()
        self._cancel_anim()
        try:
            self.toast.opacity = 0
            self.toast.disabled = True
        except Exception:
            pass
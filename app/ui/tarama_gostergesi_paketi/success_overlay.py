# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tarama_gostergesi_paketi/success_overlay.py

ROL:
- Tarama tamamlandıktan sonra kısa süreli başarı overlay göstermek
- onaylandi.png ikonunu pulse efektiyle göstermek
- Mesajı kısa süre gösterip otomatik kapatmak

MİMARİ:
- Root üzerine eklenen bağımsız overlay bileşenidir
- İş mantığı içermez, sadece görünüm ve animasyon yönetir
- show_then_hide API'si sunar
- Gizliyken dokunmaları engellemez
- Görünürken dokunmaları kontrollü biçimde yakalar

API UYUMLULUK:
- Kivy tabanlıdır
- Doğrudan Android bridge çağrısı içermez
- Android API 35 ile güvenli kullanılabilir

SURUM: 2
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

from app.ui.icon_yardimci import icon_path
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY


class TaramaSuccessOverlay(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(
            size_hint=(1, 1),
            opacity=0,
            disabled=True,
            **kwargs,
        )

        self._pulse_anim = None
        self._fade_anim = None
        self._hide_event = None

        with self.canvas.before:
            self._overlay_color = Color(0, 0, 0, 0.30)
            self._overlay_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_overlay_canvas, size=self._update_overlay_canvas)

        self.card = FloatLayout(
            size_hint=(None, None),
            size=(dp(220), dp(190)),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.add_widget(self.card)

        with self.card.canvas.before:
            self._card_color = Color(0.08, 0.15, 0.10, 0.98)
            self._card_rect = RoundedRectangle(
                pos=self.card.pos,
                size=self.card.size,
                radius=[dp(22)],
            )
        self.card.bind(pos=self._update_card_canvas, size=self._update_card_canvas)

        self.icon = Image(
            source=icon_path("onaylandi.png"),
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(None, None),
            size=(dp(72), dp(72)),
            pos_hint={"center_x": 0.5, "center_y": 0.66},
            opacity=1,
        )
        self.card.add_widget(self.icon)

        self.title_label = Label(
            text="Tarama tamamlandı",
            color=TEXT_PRIMARY,
            font_size="18sp",
            bold=True,
            size_hint=(None, None),
            size=(dp(180), dp(28)),
            pos_hint={"center_x": 0.5, "center_y": 0.32},
            halign="center",
            valign="middle",
        )
        self.title_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", size)
        )
        self.card.add_widget(self.title_label)

        self.detail_label = Label(
            text="Fonksiyon listesi hazırlanıyor",
            color=TEXT_MUTED,
            font_size="12sp",
            size_hint=(None, None),
            size=(dp(190), dp(22)),
            pos_hint={"center_x": 0.5, "center_y": 0.20},
            halign="center",
            valign="middle",
        )
        self.detail_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", size)
        )
        self.card.add_widget(self.detail_label)

    # =========================================================
    # TOUCH
    # =========================================================
    def on_touch_down(self, touch):
        if self.disabled or self.opacity <= 0:
            return False
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.disabled or self.opacity <= 0:
            return False
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.disabled or self.opacity <= 0:
            return False
        return super().on_touch_up(touch)

    # =========================================================
    # INTERNAL
    # =========================================================
    def _update_overlay_canvas(self, *_args):
        self._overlay_rect.pos = self.pos
        self._overlay_rect.size = self.size

    def _update_card_canvas(self, *_args):
        self._card_rect.pos = self.card.pos
        self._card_rect.size = self.card.size

    def _cancel_pulse(self):
        try:
            if self._pulse_anim is not None:
                self._pulse_anim.cancel(self.icon)
        except Exception:
            pass
        self._pulse_anim = None

        try:
            self.icon.opacity = 1
            self.icon.size = (dp(72), dp(72))
        except Exception:
            pass

    def _start_pulse(self):
        self._cancel_pulse()
        try:
            anim = (
                Animation(opacity=0.72, size=(dp(84), dp(84)), duration=0.28)
                + Animation(opacity=1.0, size=(dp(72), dp(72)), duration=0.28)
            )
            anim.repeat = True
            anim.start(self.icon)
            self._pulse_anim = anim
        except Exception:
            pass

    def _cancel_fade(self):
        try:
            if self._fade_anim is not None:
                self._fade_anim.cancel(self)
        except Exception:
            pass
        self._fade_anim = None

    def _cancel_hide_event(self):
        try:
            if self._hide_event is not None:
                self._hide_event.cancel()
        except Exception:
            pass
        self._hide_event = None

    # =========================================================
    # API
    # =========================================================
    def show_then_hide(
        self,
        title: str = "Tarama tamamlandı",
        detail: str = "Fonksiyon listesi hazırlanıyor",
        duration: float = 0.90,
    ) -> None:
        self._cancel_hide_event()
        self._cancel_fade()

        self.title_label.text = str(title or "Tarama tamamlandı")
        self.detail_label.text = str(detail or "Fonksiyon listesi hazırlanıyor")
        self.disabled = False

        try:
            self.size_hint = (1, 1)
        except Exception:
            pass

        try:
            self.opacity = 0
            anim = Animation(opacity=1.0, duration=0.10)
            anim.start(self)
            self._fade_anim = anim
        except Exception:
            self.opacity = 1.0

        self._start_pulse()
        self._hide_event = Clock.schedule_once(
            lambda *_: self.hide(),
            max(0.35, float(duration or 0.90)),
        )

    def hide(self) -> None:
        self._cancel_hide_event()
        self._cancel_fade()
        self._cancel_pulse()

        def _finish(*_args):
            try:
                self.opacity = 0
                self.disabled = True
            except Exception:
                pass

        try:
            anim = Animation(opacity=0.0, duration=0.12)
            anim.bind(on_complete=lambda *_: _finish())
            anim.start(self)
            self._fade_anim = anim
        except Exception:
            _finish()

    def hide_immediately(self) -> None:
        self._cancel_hide_event()
        self._cancel_fade()
        self._cancel_pulse()
        try:
            self.opacity = 0
            self.disabled = True
        except Exception:
            pass
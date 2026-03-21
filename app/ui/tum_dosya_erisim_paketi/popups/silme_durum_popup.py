# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/popups/silme_durum_popup.py

ROL:
- Silme işlemi sırasında durum popup'ı göstermek
- İlerleme çubuğu ile işlem durumunu yansıtmak
- Başarı durumunda ikon ve pulse animasyonu göstermek
- İşlem sonunda otomatik kapanabilmek

MİMARİ:
- Doğrudan ortak bileşen import etmez
- Ortak yonetici üzerinden AnimatedSeparator erişimi alır
- Popup yalnızca UI durum akışını yönetir

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 3
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY
from app.ui.tum_dosya_erisim_paketi.ortak.yoneticisi import (
    TumDosyaErisimOrtakYoneticisi,
)


def _animated_separator_widget():
    try:
        sinif = TumDosyaErisimOrtakYoneticisi().animated_separator_sinifi()
        return sinif()
    except Exception:
        return None


class RenkliIlerlemeCubugu(Widget):
    progress = NumericProperty(0.0)
    bar_color = ListProperty([1.0, 0.2, 0.2, 1.0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas:
            self._bg_color = Color(1, 1, 1, 0.08)
            self._bg_rect = RoundedRectangle(radius=[dp(10)])

            self._bar_color = Color(*self.bar_color)
            self._bar_rect = RoundedRectangle(radius=[dp(10)])

        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
            progress=self._update_canvas,
            bar_color=self._update_bar_color,
        )
        self._update_canvas()

    def _update_bar_color(self, *_args):
        self._bar_color.rgba = self.bar_color

    def _update_canvas(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

        dolu_genislik = max(0, min(self.width, self.width * self.progress))
        self._bar_rect.pos = self.pos
        self._bar_rect.size = (dolu_genislik, self.height)


def _interpolate_rgba(start_rgba, end_rgba, t: float):
    t = max(0.0, min(1.0, t))
    return [
        start_rgba[0] + (end_rgba[0] - start_rgba[0]) * t,
        start_rgba[1] + (end_rgba[1] - start_rgba[1]) * t,
        start_rgba[2] + (end_rgba[2] - start_rgba[2]) * t,
        start_rgba[3] + (end_rgba[3] - start_rgba[3]) * t,
    ]


class SilmeDurumPopup:
    def __init__(
        self,
        title_text="Silme İşlemi",
        body_text="Silme işlemi başlatılıyor...",
        success_text="Silme tamamlandı.",
        icon_name="onaylandi.png",
    ):
        self.title_text = str(title_text or "")
        self.body_text = str(body_text or "")
        self.success_text = str(success_text or "")
        self.icon_name = str(icon_name or "onaylandi.png")

        self.popup = None
        self.status_label = None
        self.progress_bar = None
        self.success_icon = None
        self._pulse_anim = None

    def open(self):
        content = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
        )

        title = Label(
            text=self.title_text,
            color=TEXT_PRIMARY,
            font_size="18sp",
            bold=True,
            size_hint_y=None,
            height=dp(28),
            halign="center",
            valign="middle",
        )
        title.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        content.add_widget(title)

        sep1 = _animated_separator_widget()
        if sep1 is not None:
            content.add_widget(sep1)

        self.status_label = Label(
            text=self.body_text,
            color=TEXT_MUTED,
            font_size="13sp",
            size_hint_y=None,
            height=dp(42),
            halign="center",
            valign="middle",
        )
        self.status_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
        content.add_widget(self.status_label)

        self.progress_bar = RenkliIlerlemeCubugu(
            size_hint_y=None,
            height=dp(16),
        )
        self.progress_bar.progress = 0.0
        self.progress_bar.bar_color = [1.0, 0.18, 0.18, 1.0]
        content.add_widget(self.progress_bar)

        self.success_icon = Image(
            source=f"app/assets/icons/{self.icon_name}",
            size_hint=(None, None),
            size=(dp(0), dp(0)),
            opacity=0,
            allow_stretch=True,
            keep_ratio=True,
            pos_hint={"center_x": 0.5},
        )

        icon_wrap = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(110),
            padding=(0, dp(6), 0, 0),
        )
        icon_wrap.add_widget(self.success_icon)
        content.add_widget(icon_wrap)

        sep2 = _animated_separator_widget()
        if sep2 is not None:
            content.add_widget(sep2)

        self.popup = Popup(
            title="",
            content=content,
            size_hint=(0.84, 0.36),
            auto_dismiss=False,
            separator_height=0,
        )
        self.popup.open()
        return self

    def set_progress(self, progress_value: float, text: str | None = None):
        if self.progress_bar is None:
            return

        progress_value = max(0.0, min(1.0, float(progress_value or 0.0)))
        self.progress_bar.progress = progress_value
        self.progress_bar.bar_color = _interpolate_rgba(
            [1.0, 0.18, 0.18, 1.0],
            [0.10, 0.85, 0.32, 1.0],
            progress_value,
        )

        if text is not None and self.status_label is not None:
            self.status_label.text = str(text or "")

    def finish_success(self, text: str | None = None, auto_close_seconds: float = 1.6):
        self.set_progress(1.0)

        if self.status_label is not None:
            if text:
                self.status_label.text = str(text)
            else:
                self.status_label.text = self.success_text

        if self.success_icon is not None:
            self.success_icon.opacity = 1
            self.success_icon.size = (dp(72), dp(72))

        self._start_pulse()
        Clock.schedule_once(
            lambda *_: self.dismiss(),
            max(0.3, float(auto_close_seconds or 1.6)),
        )

    def _start_pulse(self):
        if self.success_icon is None:
            return

        try:
            if self._pulse_anim:
                self._pulse_anim.cancel(self.success_icon)
        except Exception:
            pass

        self.success_icon.size = (dp(72), dp(72))
        anim = (
            Animation(size=(dp(92), dp(92)), duration=0.28)
            + Animation(size=(dp(78), dp(78)), duration=0.22)
        )
        anim.repeat = True
        anim.start(self.success_icon)
        self._pulse_anim = anim

    def dismiss(self):
        try:
            if self._pulse_anim and self.success_icon is not None:
                self._pulse_anim.cancel(self.success_icon)
        except Exception:
            pass

        self._pulse_anim = None

        try:
            if self.popup:
                self.popup.dismiss()
        except Exception:
            pass
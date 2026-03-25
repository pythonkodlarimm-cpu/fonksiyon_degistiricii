# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/icon_toolbar.py

ROL:
- Büyük ikonlu, yazısı altta olan sade toolbar bileşenleri
- Arka plan kutusunu minimumda tutar
- Mobil görünüm için ikonları belirgin yapar
- Toolbar buton metnini çalışma anında güncelleyebilmeyi destekler

MİMARİ:
- Görsel çizim burada tutulur
- İkon yolu güvenli fallback ile çözülür
- Buton metni set_text ile dışarıdan güncellenebilir
- Toolbar yalnızca butonları düzenler, iş akışı taşımaz

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 2
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path

from kivy.graphics import Color
from kivy.graphics import RoundedRectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

from app.ui.tema import TEXT_MUTED


def _icon_path(icon_name: str) -> str:
    """
    İkonu olabildiğince güvenli şekilde bul.
    icon_name doğrudan dosya adı olarak verilir.
    """
    adaylar = [
        Path("icons") / str(icon_name or ""),
        Path("app") / "assets" / "icons" / str(icon_name or ""),
        Path(str(icon_name or "")),
    ]

    for aday in adaylar:
        try:
            if aday.exists():
                return str(aday)
        except Exception:
            pass

    return str(adaylar[0])


class IconToolbarButton(ButtonBehavior, BoxLayout):
    """
    Üstte büyük ikon, altta sönük başlık.
    İstenirse arka plan tamamen kapatılabilir.
    """

    def __init__(
        self,
        icon_name: str,
        text: str = "",
        icon_size_dp: int = 34,
        text_size: str = "11sp",
        color=TEXT_MUTED,
        icon_bg=None,
        radius_dp: int = 14,
        **kwargs,
    ):
        super().__init__(
            orientation="vertical",
            spacing=dp(4),
            padding=(dp(4), dp(4), dp(4), dp(2)),
            **kwargs,
        )

        self.size_hint_y = None
        self.height = dp(64)

        self._icon_bg = icon_bg
        self._radius_dp = radius_dp

        with self.canvas.before:
            self._bg_color = Color(0, 0, 0, 0)
            self._bg_rect = RoundedRectangle(radius=[dp(self._radius_dp)])

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

        self.icon_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(icon_size_dp + 6),
            padding=0,
        )
        self.add_widget(self.icon_box)

        self.icon = Image(
            source=_icon_path(icon_name),
            size_hint=(None, None),
            size=(dp(icon_size_dp), dp(icon_size_dp)),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            allow_stretch=True,
            keep_ratio=True,
        )
        self.icon_box.add_widget(self.icon)

        self.label = Label(
            text=str(text or ""),
            color=color,
            font_size=text_size,
            size_hint_y=None,
            height=dp(16),
            halign="center",
            valign="middle",
            shorten=True,
            shorten_from="right",
        )
        self.label.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], size[1]))
        )
        self.add_widget(self.label)

    def set_text(self, text: str) -> None:
        try:
            self.label.text = str(text or "")
        except Exception:
            pass

    def get_text(self) -> str:
        try:
            return str(self.label.text or "")
        except Exception:
            return ""

    def set_icon(self, icon_name: str) -> None:
        try:
            self.icon.source = _icon_path(icon_name)
            self.icon.reload()
        except Exception:
            try:
                self.icon.source = _icon_path(icon_name)
            except Exception:
                pass

    def _update_canvas(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

        if self._icon_bg:
            self._bg_color.rgba = self._icon_bg
        else:
            self._bg_color.rgba = (0, 0, 0, 0)

    def on_press(self):
        if self._icon_bg:
            try:
                r, g, b, a = self._icon_bg
                self._bg_color.rgba = (r, g, b, min(1, a + 0.12))
            except Exception:
                self._bg_color.rgba = self._icon_bg

    def on_release(self):
        self._update_canvas()


class IconToolbar(BoxLayout):
    """
    Yatay ikon toolbar.
    """

    def __init__(self, spacing_dp: int = 14, padding_dp: int = 4, **kwargs):
        super().__init__(
            orientation="horizontal",
            spacing=dp(spacing_dp),
            padding=(dp(padding_dp), 0, dp(padding_dp), 0),
            size_hint_y=None,
            height=dp(70),
            **kwargs,
        )

    def add_tool(
        self,
        icon_name: str,
        text: str,
        on_release,
        icon_size_dp: int = 34,
        text_size: str = "11sp",
        color=TEXT_MUTED,
        icon_bg=None,
    ) -> IconToolbarButton:
        btn = IconToolbarButton(
            icon_name=icon_name,
            text=text,
            icon_size_dp=icon_size_dp,
            text_size=text_size,
            color=color,
            icon_bg=icon_bg,
        )
        btn.bind(on_release=on_release)
        self.add_widget(btn)
        return btn

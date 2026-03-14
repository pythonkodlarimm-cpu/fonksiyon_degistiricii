# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/durum_cubugu.py
ROL:
- Alt durum çubuğu
- İkon + metin gösterir
- Başarı / uyarı / hata gibi kısa mesajları taşır
"""

from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.label import Label

from app.ui.icon_yardimci import icon_path
from app.ui.kart import Kart
from app.ui.tema import CARD_BG_DARK, RADIUS_LG, TEXT_PRIMARY


class DurumCubugu(Kart):
    """
    Alt durum çubuğu.

    Root sadece set_status çağırır.
    Görsel çizim burada kalır.
    """

    def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            spacing=dp(8),
            padding=(dp(12), dp(9)),
            size_hint_y=None,
            height=dp(48),
            bg=CARD_BG_DARK,
            radius=RADIUS_LG,
            **kwargs,
        )

        self.icon = Image(
            source="",
            size_hint=(None, None),
            size=(dp(18), dp(18)),
            allow_stretch=True,
            keep_ratio=True,
        )
        self.add_widget(self.icon)

        self.label = Label(
            text="Hazır",
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
        widget.text_size = (size[0], None)

    def set_status(self, text: str, icon_name: str = "") -> None:
        self.label.text = str(text or "")
        self.icon.source = icon_path(icon_name) if icon_name else ""
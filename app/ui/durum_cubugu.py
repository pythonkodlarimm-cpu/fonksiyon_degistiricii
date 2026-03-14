# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/durum_cubugu.py
ROL:
- Alt durum çubuğu
- İkon + metin gösterir
- Başarı / uyarı / hata gibi kısa mesajları taşır

APK / Android UYUMLULUK NOTLARI:
- İkon değişiminde source güncellendikten sonra reload() çağrılır.
- Boş ikon durumunda source temizlenir ve opacity düşürülür.
- Label alanı yatayda genişleyerek taşmayı azaltır.
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
            opacity=0,
        )
        self.add_widget(self.icon)

        self.label = Label(
            text="Hazır",
            size_hint_x=1,
            color=TEXT_PRIMARY,
            halign="left",
            valign="middle",
            font_size="13sp",
            shorten=True,
            shorten_from="right",
            max_lines=1,
        )
        self.label.bind(size=self._sync_label_size)
        self.add_widget(self.label)

    def _sync_label_size(self, widget, size):
        widget.text_size = (size[0], size[1])

    def set_status(self, text: str, icon_name: str = "") -> None:
        temiz_metin = str(text or "").strip()
        self.label.text = temiz_metin if temiz_metin else " "

        if icon_name:
            try:
                ikon_yolu = icon_path(icon_name)
            except Exception:
                ikon_yolu = ""

            if ikon_yolu:
                self.icon.source = ikon_yolu
                self.icon.opacity = 1
                try:
                    self.icon.reload()
                except Exception:
                    pass
            else:
                self.icon.source = ""
                self.icon.opacity = 0
        else:
            self.icon.source = ""
            self.icon.opacity = 0

    def set_ready(self) -> None:
        self.set_status("Hazır")

    def set_success(self, text: str = "İşlem başarılı") -> None:
        self.set_status(text, "check.png")

    def set_warning(self, text: str = "Uyarı") -> None:
        self.set_status(text, "warning.png")

    def set_error(self, text: str = "Bir hata oluştu") -> None:
        self.set_status(text, "error.png")
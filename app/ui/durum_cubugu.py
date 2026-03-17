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
- Bu bileşen doğrudan Android API çağrısı yapmaz; API 34 ile güvenle kullanılabilir.

SURUM: 4
TARIH: 2026-03-17
IMZA: FY.
"""

from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.label import Label

from app.ui.icon_yardimci import icon_path
from app.ui.kart import Kart
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY


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
            padding=(dp(12), dp(8), dp(12), dp(8)),
            size_hint_y=None,
            height=dp(50),
            bg=(0.08, 0.11, 0.16, 1),
            border=(0.18, 0.21, 0.27, 1),
            radius=16,
            **kwargs,
        )

        self._bg_info = (0.08, 0.11, 0.16, 1)
        self._bg_success = (0.08, 0.22, 0.14, 1)
        self._bg_warning = (0.24, 0.18, 0.08, 1)
        self._bg_error = (0.24, 0.10, 0.10, 1)

        self._border_info = (0.18, 0.21, 0.27, 1)
        self._border_success = (0.14, 0.34, 0.22, 1)
        self._border_warning = (0.36, 0.26, 0.10, 1)
        self._border_error = (0.36, 0.14, 0.14, 1)

        self.icon = Image(
            source="",
            size_hint=(None, None),
            size=(dp(20), dp(20)),
            opacity=0,
            allow_stretch=True,
            keep_ratio=True,
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

        self._apply_info_style()

    def _sync_label_size(self, widget, size):
        try:
            widget.text_size = (size[0], size[1])
        except Exception:
            pass

    def _set_icon(self, icon_name: str = "") -> None:
        temiz_ad = str(icon_name or "").strip()

        if temiz_ad:
            try:
                ikon_yolu = icon_path(temiz_ad)
            except Exception:
                ikon_yolu = ""

            if ikon_yolu:
                try:
                    self.icon.source = ikon_yolu
                    self.icon.opacity = 1
                    self.icon.reload()
                except Exception:
                    try:
                        self.icon.source = ikon_yolu
                        self.icon.opacity = 1
                    except Exception:
                        pass
                return

        try:
            self.icon.source = ""
            self.icon.opacity = 0
        except Exception:
            pass

    def _apply_info_style(self) -> None:
        self.set_bg_rgba(self._bg_info)
        self.set_border_rgba(self._border_info)
        self.label.color = TEXT_PRIMARY

    def _apply_success_style(self) -> None:
        self.set_bg_rgba(self._bg_success)
        self.set_border_rgba(self._border_success)
        self.label.color = (0.84, 1.0, 0.88, 1)

    def _apply_warning_style(self) -> None:
        self.set_bg_rgba(self._bg_warning)
        self.set_border_rgba(self._border_warning)
        self.label.color = (1.0, 0.92, 0.72, 1)

    def _apply_error_style(self) -> None:
        self.set_bg_rgba(self._bg_error)
        self.set_border_rgba(self._border_error)
        self.label.color = (1.0, 0.82, 0.82, 1)

    def set_status(self, text: str, icon_name: str = "") -> None:
        temiz_metin = str(text or "").strip()
        self.label.text = temiz_metin if temiz_metin else " "
        self._set_icon(icon_name)
        self._apply_info_style()

    def set_ready(self) -> None:
        self.set_status("Hazır")

    def set_success(self, text: str = "İşlem başarılı") -> None:
        temiz_metin = str(text or "").strip() or "İşlem başarılı"
        self.label.text = temiz_metin
        self._set_icon("onaylandi.png")
        self._apply_success_style()

    def set_warning(self, text: str = "Uyarı") -> None:
        temiz_metin = str(text or "").strip() or "Uyarı"
        self.label.text = temiz_metin
        self._set_icon("warning.png")
        self._apply_warning_style()

    def set_error(self, text: str = "Bir hata oluştu") -> None:
        temiz_metin = str(text or "").strip() or "Bir hata oluştu"
        self.label.text = temiz_metin
        self._set_icon("error.png")
        self._apply_error_style()

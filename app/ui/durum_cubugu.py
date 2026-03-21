# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/durum_cubugu.py

ROL:
- Alt durum çubuğu
- İkon + metin gösterir
- Başarı / uyarı / hata gibi kısa mesajları taşır
- Detaylı hata metni geldiğinde kopyalanabilir popup açabilir

MİMARİ:
- Saf UI bileşenidir
- Doğrudan Android API çağrısı yapmaz
- Root ve diğer UI katmanları tarafından güvenli şekilde kullanılabilir
- Mevcut API korunur, ek olarak detaylı hata metni desteklenir

APK / ANDROID UYUMLULUK:
- İkon değişiminde source güncellendikten sonra reload() çağrılır
- Boş ikon durumunda source temizlenir ve opacity düşürülür
- Label alanı yatayda genişleyerek taşmayı azaltır
- API 35 ile güvenli kullanılabilir
- APK / AAB davranış farkını azaltmak için görsel fallback mantığı korunmuştur

SURUM: 6
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations

from kivy.core.clipboard import Clipboard
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

from app.ui.icon_yardimci import icon_path
from app.ui.kart import Kart
from app.ui.tema import TEXT_PRIMARY


class DurumCubugu(ButtonBehavior, Kart):
    """
    Alt durum çubuğu.

    Root sadece set_status çağırır.
    Görsel çizim burada kalır.

    Not:
    - set_error çağrısında detaylı hata metni verilirse,
      çubuğa dokununca kopyalanabilir popup açılır.
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

        self._popup_title = "Hata Detayı"
        self._detailed_error_text = ""
        self._popup_ref = None

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

    # =========================================================
    # INTERNAL
    # =========================================================
    def _sync_label_size(self, widget, size) -> None:
        try:
            widget.text_size = (size[0], size[1])
        except Exception:
            pass

    def _safe_text(self, text: str, fallback: str) -> str:
        temiz = str(text or "").strip()
        return temiz if temiz else fallback

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

    def _clear_detailed_error(self) -> None:
        self._detailed_error_text = ""
        self._popup_title = "Hata Detayı"

    def _set_detailed_error(self, text: str, title: str = "Hata Detayı") -> None:
        self._detailed_error_text = str(text or "").strip()
        self._popup_title = str(title or "Hata Detayı").strip() or "Hata Detayı"

    def _has_detailed_error(self) -> bool:
        return bool(str(self._detailed_error_text or "").strip())

    def _show_detailed_error_popup(self) -> None:
        if not self._has_detailed_error():
            return

        popup = None
        try:
            content = BoxLayout(
                orientation="vertical",
                spacing=dp(10),
                padding=(dp(12), dp(12), dp(12), dp(12)),
            )

            baslik = Label(
                text=str(self._popup_title or "Hata Detayı"),
                size_hint_y=None,
                height=dp(28),
                font_size="18sp",
                bold=True,
                color=(1.0, 0.42, 0.42, 1),
                halign="center",
                valign="middle",
            )
            baslik.bind(size=lambda inst, size: setattr(inst, "text_size", size))
            content.add_widget(baslik)

            alt = Label(
                text="Dosya yolu, fonksiyon, satır ve traceback metni kopyalanabilir.",
                size_hint_y=None,
                height=dp(20),
                font_size="11sp",
                color=(0.86, 0.86, 0.90, 1),
                halign="center",
                valign="middle",
            )
            alt.bind(size=lambda inst, size: setattr(inst, "text_size", size))
            content.add_widget(alt)

            scroll = ScrollView(
                do_scroll_x=True,
                do_scroll_y=True,
                bar_width=dp(8),
            )

            detay = Label(
                text=str(self._detailed_error_text or ""),
                color=TEXT_PRIMARY,
                halign="left",
                valign="top",
                size_hint_y=None,
                font_size="12sp",
            )
            detay.bind(
                texture_size=lambda inst, val: setattr(inst, "height", max(dp(180), val[1]))
            )
            detay.bind(
                size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
            )

            scroll.add_widget(detay)
            content.add_widget(scroll)

            button_row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(46),
                spacing=dp(8),
            )

            copy_btn = Button(
                text="Kopyala",
                background_normal="",
                background_down="",
                background_color=(0.18, 0.42, 0.72, 1),
                color=(1, 1, 1, 1),
            )

            close_btn = Button(
                text="Kapat",
                background_normal="",
                background_down="",
                background_color=(0.24, 0.24, 0.28, 1),
                color=(1, 1, 1, 1),
            )

            def _copy(*_args):
                try:
                    Clipboard.copy(str(self._detailed_error_text or ""))
                except Exception:
                    pass

            copy_btn.bind(on_release=_copy)
            button_row.add_widget(copy_btn)
            button_row.add_widget(close_btn)
            content.add_widget(button_row)

            popup = Popup(
                title="",
                content=content,
                size_hint=(0.94, 0.84),
                auto_dismiss=True,
                separator_height=0,
            )

            self._popup_ref = popup
            close_btn.bind(on_release=lambda *_: popup.dismiss())
            popup.open()

        except Exception:
            try:
                if popup is not None:
                    popup.dismiss()
            except Exception:
                pass

    # =========================================================
    # INTERACTION
    # =========================================================
    def on_press(self):
        try:
            if self._has_detailed_error():
                self._show_detailed_error_popup()
        except Exception:
            pass

    # =========================================================
    # PUBLIC API
    # =========================================================
    def set_status(self, text: str, icon_name: str = "") -> None:
        self._clear_detailed_error()
        self.label.text = self._safe_text(text, " ")
        self._set_icon(icon_name)
        self._apply_info_style()

    def set_ready(self) -> None:
        self.set_status("Hazır")

    def set_success(self, text: str = "İşlem başarılı") -> None:
        self._clear_detailed_error()
        self.label.text = self._safe_text(text, "İşlem başarılı")
        self._set_icon("onaylandi.png")
        self._apply_success_style()

    def set_warning(self, text: str = "Uyarı") -> None:
        self._clear_detailed_error()
        self.label.text = self._safe_text(text, "Uyarı")
        self._set_icon("warning.png")
        self._apply_warning_style()

    def set_error(
        self,
        text: str = "Bir hata oluştu",
        detailed_text: str = "",
        popup_title: str = "Hata Detayı",
    ) -> None:
        self.label.text = self._safe_text(text, "Bir hata oluştu")
        self._set_icon("error.png")
        self._apply_error_style()

        detay = str(detailed_text or "").strip()
        if detay:
            self._set_detailed_error(detay, title=popup_title)
        else:
            self._clear_detailed_error()
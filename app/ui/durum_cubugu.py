# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/durum_cubugu.py

ROL:
- Alt durum çubuğu
- İkon + metin gösterir
- Başarı / uyarı / hata gibi kısa mesajları taşır
- Detaylı hata metni geldiğinde kopyalanabilir popup açabilir
- İsteğe bağlı geçici aksiyon butonu gösterebilir
- Aksiyon butonunu dikkat çekici pulse animasyonu ile gösterebilir
- Seçilen dilde kullanıcıya metin gösterebilir

MİMARİ:
- Saf UI bileşenidir
- Doğrudan Android API çağrısı yapmaz
- Root ve diğer UI katmanları tarafından güvenli şekilde kullanılabilir
- Mevcut API korunur, ek olarak detaylı hata metni ve aksiyon butonu desteklenir
- Pulse animasyonu sadece aksiyon butonu görünürken çalışır
- Aynı aksiyon altyapısı hem tarama CTA hem güncelleme CTA için kullanılabilir
- Sabit metinler ServicesYoneticisi -> dil servisi üzerinden çözülebilir

APK / ANDROID UYUMLULUK:
- İkon değişiminde source güncellendikten sonra reload() çağrılır
- Boş ikon durumunda source temizlenir ve opacity düşürülür
- Label alanı yatayda genişleyerek taşmayı azaltır
- API 35 ile güvenli kullanılabilir
- APK / AAB davranış farkını azaltmak için görsel fallback mantığı korunmuştur

SURUM: 11
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from kivy.animation import Animation
from kivy.core.clipboard import Clipboard
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

from app.services.yoneticisi import ServicesYoneticisi
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
    - set_action çağrısı ile geçici aksiyon butonu gösterilebilir.
    - Aksiyon butonu görünürken pulse animasyonu çalışabilir.
    """

    def __init__(self, services: ServicesYoneticisi | None = None, **kwargs):
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

        self.services = services or ServicesYoneticisi()

        self._bg_info = (0.08, 0.11, 0.16, 1)
        self._bg_success = (0.08, 0.22, 0.14, 1)
        self._bg_warning = (0.24, 0.18, 0.08, 1)
        self._bg_error = (0.24, 0.10, 0.10, 1)

        self._border_info = (0.18, 0.21, 0.27, 1)
        self._border_success = (0.14, 0.34, 0.22, 1)
        self._border_warning = (0.36, 0.26, 0.10, 1)
        self._border_error = (0.36, 0.14, 0.14, 1)

        self._popup_title = self._m("error_title", "Hata Detayı")
        self._detailed_error_text = ""
        self._popup_ref = None

        self._action_callback = None
        self._action_visible = False
        self._action_pulse_anim = None
        self._action_tone = "info"
        self._last_status_kind = "info"

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
            text=self._m("app_ready", "Hazır."),
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

        self.action_button = Button(
            text="",
            size_hint=(None, None),
            size=(0, 0),
            opacity=0,
            disabled=True,
            background_normal="",
            background_down="",
            background_color=(0.18, 0.42, 0.72, 1),
            color=(1, 1, 1, 1),
            font_size="11sp",
        )
        self.action_button.bind(on_release=self._on_action_button_release)
        self.add_widget(self.action_button)

        self._apply_info_style()

    # =========================================================
    # LANGUAGE
    # =========================================================
    def _m(self, anahtar: str, default: str = "") -> str:
        try:
            return str(self.services.metin(anahtar, default) or default or anahtar)
        except Exception:
            return str(default or anahtar)

    def refresh_language(self) -> None:
        try:
            self._popup_title = self._m("error_title", "Hata Detayı")
        except Exception:
            self._popup_title = "Hata Detayı"

        try:
            if self._last_status_kind == "ready":
                self.label.text = self._m("app_ready", "Hazır.")
            elif self._last_status_kind == "success" and not str(self.label.text or "").strip():
                self.label.text = self._m("processing_successful", "İşlem başarılı")
            elif self._last_status_kind == "warning" and not str(self.label.text or "").strip():
                self.label.text = self._m("warning", "Uyarı")
            elif self._last_status_kind == "error" and not str(self.label.text or "").strip():
                self.label.text = self._m("an_error_occurred", "Bir hata oluştu")
        except Exception:
            pass

        try:
            if self._action_visible and self.action_button is not None:
                mevcut_buton = str(self.action_button.text or "").strip()
                if not mevcut_buton:
                    self.action_button.text = self._m("continue", "Devam Et")
        except Exception:
            pass

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
        self._popup_title = self._m("error_title", "Hata Detayı")

    def _set_detailed_error(self, text: str, title: str = "") -> None:
        self._detailed_error_text = str(text or "").strip()
        varsayilan = self._m("error_title", "Hata Detayı")
        self._popup_title = str(title or varsayilan).strip() or varsayilan

    def _has_detailed_error(self) -> bool:
        return bool(str(self._detailed_error_text or "").strip())

    def _apply_action_button_theme(self, tone: str = "info") -> None:
        self._action_tone = str(tone or "info").strip().lower() or "info"

        try:
            if self._action_tone == "success":
                self.action_button.background_color = (0.16, 0.50, 0.28, 1)
            elif self._action_tone == "warning":
                self.action_button.background_color = (0.78, 0.52, 0.10, 1)
            elif self._action_tone == "error":
                self.action_button.background_color = (0.62, 0.18, 0.18, 1)
            else:
                self.action_button.background_color = (0.18, 0.42, 0.72, 1)
        except Exception:
            pass

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
                text=str(self._popup_title or self._m("error_title", "Hata Detayı")),
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
                text=self._m(
                    "error_copy_hint",
                    "Dosya yolu, fonksiyon, satır ve traceback metni kopyalanabilir.",
                ),
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
                texture_size=lambda inst, val: setattr(
                    inst,
                    "height",
                    max(dp(180), val[1]),
                )
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
                text=self._m("copy", "Kopyala"),
                background_normal="",
                background_down="",
                background_color=(0.18, 0.42, 0.72, 1),
                color=(1, 1, 1, 1),
            )

            close_btn = Button(
                text=self._m("close", "Kapat"),
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

    def _stop_action_pulse(self) -> None:
        try:
            if self._action_pulse_anim is not None:
                self._action_pulse_anim.cancel(self.action_button)
        except Exception:
            pass
        self._action_pulse_anim = None

    def _start_action_pulse(self) -> None:
        self._stop_action_pulse()

        try:
            if not self._action_visible:
                return

            if self.action_button is None:
                return

            normal_w = dp(108)
            normal_h = dp(30)
            buyuk_w = dp(116)
            buyuk_h = dp(34)

            self.action_button.size = (normal_w, normal_h)

            anim_buyut = Animation(
                size=(buyuk_w, buyuk_h),
                duration=0.45,
            )
            anim_kucult = Animation(
                size=(normal_w, normal_h),
                duration=0.45,
            )

            self._action_pulse_anim = anim_buyut + anim_kucult
            self._action_pulse_anim.repeat = True
            self._action_pulse_anim.start(self.action_button)
        except Exception:
            self._action_pulse_anim = None

    def _show_action_button(self, text: str, callback, tone: str = "info") -> None:
        self._action_callback = callback
        self._action_visible = True

        try:
            self.action_button.text = self._safe_text(
                text,
                self._m("continue", "Devam Et"),
            )
            self.action_button.disabled = False
            self.action_button.opacity = 1
            self.action_button.size = (dp(108), dp(30))
            self.action_button.width = max(
                dp(108),
                dp(24) * len(self.action_button.text),
            )
        except Exception:
            pass

        self._apply_action_button_theme(tone=tone)
        self._start_action_pulse()

    def _hide_action_button(self) -> None:
        self._stop_action_pulse()

        self._action_callback = None
        self._action_visible = False
        self._action_tone = "info"

        try:
            self.action_button.text = ""
            self.action_button.disabled = True
            self.action_button.opacity = 0
            self.action_button.size = (0, 0)
        except Exception:
            pass

    def _on_action_button_release(self, *_args) -> None:
        callback = self._action_callback
        if callback is None:
            return

        try:
            callback()
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
        self._last_status_kind = "info"
        self._clear_detailed_error()
        self._hide_action_button()
        self.label.text = self._safe_text(text, " ")
        self._set_icon(icon_name)
        self._apply_info_style()

    def set_ready(self) -> None:
        self._last_status_kind = "ready"
        self.set_status(self._m("app_ready", "Hazır."))

    def set_success(self, text: str = "") -> None:
        self._last_status_kind = "success"
        self._clear_detailed_error()
        self._hide_action_button()
        self.label.text = self._safe_text(
            text,
            self._m("processing_successful", "İşlem başarılı"),
        )
        self._set_icon("onaylandi.png")
        self._apply_success_style()

    def set_warning(self, text: str = "") -> None:
        self._last_status_kind = "warning"
        self._clear_detailed_error()
        self._hide_action_button()
        self.label.text = self._safe_text(
            text,
            self._m("warning", "Uyarı"),
        )
        self._set_icon("warning.png")
        self._apply_warning_style()

    def set_error(
        self,
        text: str = "",
        detailed_text: str = "",
        popup_title: str = "",
    ) -> None:
        self._last_status_kind = "error"
        self._hide_action_button()
        self.label.text = self._safe_text(
            text,
            self._m("an_error_occurred", "Bir hata oluştu"),
        )
        self._set_icon("error.png")
        self._apply_error_style()

        detay = str(detailed_text or "").strip()
        if detay:
            self._set_detailed_error(
                detay,
                title=popup_title or self._m("error_title", "Hata Detayı"),
            )
        else:
            self._clear_detailed_error()

    def set_action(
        self,
        text: str,
        button_text: str = "",
        callback=None,
        icon_name: str = "onaylandi.png",
        tone: str = "success",
    ) -> None:
        """
        Durum çubuğunda metin + opsiyonel aksiyon butonu gösterir.
        Tarama tamamlandıktan sonra 'Listeyi Aç' veya
        güncelleme akışında 'Güncelle' gibi CTA'lar için kullanılır.
        """
        secili_ton = str(tone or "success").strip().lower() or "success"
        self._last_status_kind = f"action:{secili_ton}"

        self._clear_detailed_error()
        self.label.text = self._safe_text(text, " ")

        if secili_ton == "error":
            self._set_icon("error.png")
            self._apply_error_style()
        elif secili_ton == "warning":
            self._set_icon(icon_name or "warning.png")
            self._apply_warning_style()
        elif secili_ton == "success":
            self._set_icon(icon_name or "onaylandi.png")
            self._apply_success_style()
        else:
            self._set_icon(icon_name)
            self._apply_info_style()

        if callable(callback):
            self._show_action_button(
                text=button_text or self._m("continue", "Devam Et"),
                callback=callback,
                tone=secili_ton,
            )
        else:
            self._hide_action_button()

    def clear_action(self) -> None:
        self._hide_action_button()

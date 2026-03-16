# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paneli.py

ROL:
- Android'de tüm dosya erişimi durumunu kullanıcıya göstermek
- Gerekirse kullanıcıyı ilgili ayar ekranına yönlendirmek

MİMARİ:
- Kendi görünümünü kendi çizer
- Root sadece ekrana ekler
- Android özel izin servisi ile konuşur

SURUM: 1
TARIH: 2026-03-16
IMZA: FY.
"""

from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.utils import platform

from app.ui.icon_toolbar import IconToolbar
from app.ui.iconlu_baslik import IconluBaslik
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY


class TumDosyaErisimPaneli(BoxLayout):
    def __init__(self, on_status_changed=None, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(116),
            spacing=dp(8),
            **kwargs,
        )

        self.on_status_changed = on_status_changed

        self.header = None
        self.info_label = None
        self.toolbar = None

        self._build_ui()
        self.refresh_status()

    def _debug(self, message: str) -> None:
        try:
            print("[TUM_DOSYA_ERISIM]", str(message))
        except Exception:
            pass

    def _build_ui(self) -> None:
        self.header = IconluBaslik(
            text="Tüm Dosya Erişimi",
            icon_name="folder_open.png",
            height_dp=30,
            font_size="15sp",
            color=TEXT_PRIMARY,
        )
        self.add_widget(self.header)

        self.info_label = Label(
            text="Durum kontrol ediliyor...",
            size_hint_y=None,
            height=dp(24),
            color=TEXT_MUTED,
            font_size="12sp",
            halign="left",
            valign="middle",
        )
        self.info_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
        self.add_widget(self.info_label)

        self.toolbar = IconToolbar(
            spacing_dp=16,
            padding_dp=4,
        )

        self.toolbar.add_tool(
            icon_name="refresh.png",
            text="Kontrol",
            on_release=self._handle_refresh,
            icon_size_dp=32,
            text_size="10sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.toolbar.add_tool(
            icon_name="settings.png",
            text="İzin Ver",
            on_release=self._handle_open_settings,
            icon_size_dp=32,
            text_size="10sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.add_widget(self.toolbar)

    def _set_info(self, text: str) -> None:
        try:
            self.info_label.text = str(text or "")
        except Exception:
            pass

    def refresh_status(self) -> None:
        if platform != "android":
            self._set_info("Android dışında tüm dosya erişimi kullanılmaz.")
            return

        try:
            from app.services.android_ozel_izin_servisi import (
                tum_dosya_erisim_izni_var_mi,
            )

            durum = bool(tum_dosya_erisim_izni_var_mi())

            if durum:
                self._set_info("Tüm dosya erişimi açık.")
            else:
                self._set_info(
                    "Tüm dosya erişimi kapalı. Belgeler için erişim sınırlı olabilir."
                )

            if self.on_status_changed:
                self.on_status_changed(durum)

            self._debug(f"Tüm dosya erişimi durumu: {durum}")

        except Exception as exc:
            self._set_info(f"İzin durumu okunamadı: {exc}")
            self._debug(f"İzin durumu okunamadı: {exc}")

    def _handle_refresh(self, *_args) -> None:
        self.refresh_status()

    def _handle_open_settings(self, *_args) -> None:
        if platform != "android":
            self._set_info("Bu ayar yalnızca Android'de kullanılabilir.")
            return

        try:
            from app.services.android_ozel_izin_servisi import (
                tum_dosya_erisim_ayarlari_ac,
            )

            tum_dosya_erisim_ayarlari_ac()
            self._set_info(
                "Ayar ekranı açıldı. İzin verdikten sonra geri dönüp Kontrol'e bas."
            )
        except Exception as exc:
            self._set_info(f"Ayar ekranı açılamadı: {exc}")
            self._debug(f"Ayar ekranı açılamadı: {exc}")
# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/panel/panel.py

ROL:
- Tüm dosya erişim panelini göstermek
- Menü ikonunu sunmak
- Ana menü ve yedek popup akışını başlatmak

MİMARİ:
- Alt modülleri doğrudan import etmez
- TumDosyaErisimYoneticisi üzerinden erişir
- Panel yalnızca UI davranışını yönetir

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 3
TARIH: 2026-03-22
IMZA: FY.
"""

from __future__ import annotations

from kivy.metrics import dp

from app.ui.kart import Kart


class TumDosyaErisimPaneli(Kart):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            padding=(dp(10), dp(10)),
            bg=(0.08, 0.11, 0.16, 1),
            border=(0.18, 0.21, 0.27, 1),
            radius=12,
            **kwargs,
        )

        self.menu_icon = None
        self._menu_anim = None

        self._build_ui()
        self._start_menu_glow()

    # =========================================================
    # YONETICI
    # =========================================================
    def _yonetici(self):
        from app.ui.tum_dosya_erisim_paketi import TumDosyaErisimYoneticisi
        return TumDosyaErisimYoneticisi()

    # =========================================================
    # DEBUG
    # =========================================================
    def _debug(self, message: str) -> None:
        try:
            print("[TUM_DOSYA_ERISIM]", str(message))
        except Exception:
            pass

    # =========================================================
    # UI
    # =========================================================
    def _build_ui(self):
        try:
            IconSinifi = self._yonetici().tiklanabilir_icon_sinifi()
            self.menu_icon = IconSinifi(
                source="app/assets/icons/menu.png",
                size_hint=(None, None),
                size=(dp(36), dp(36)),
                opacity=1,
                allow_stretch=True,
                keep_ratio=True,
            )
        except Exception:
            from kivy.uix.label import Label

            self.menu_icon = Label(
                text="≡",
                size_hint=(None, None),
                size=(dp(36), dp(36)),
            )

        try:
            self.menu_icon.bind(on_release=self._open_main_menu)
        except Exception:
            pass

        self.add_widget(self.menu_icon)

    # =========================================================
    # GLOW
    # =========================================================
    def _start_menu_glow(self) -> None:
        try:
            self._menu_anim = self._yonetici().start_icon_glow(
                self.menu_icon,
                36,
                40,
                0.60,
            )
        except Exception:
            self._menu_anim = None

    # =========================================================
    # ACTIONS
    # =========================================================
    def _open_main_menu(self, *_args):
        try:
            self._yonetici().open_main_menu(
                open_backups_popup=lambda: self._open_backups_popup(),
            )
        except Exception as exc:
            self._debug(f"ana menü açılamadı: {exc}")
            self._yonetici().show_simple_popup(
                title_text="Menü Hatası",
                body_text=f"Menü açılamadı:\n{exc}",
                icon_name="warning.png",
                auto_close_seconds=1.8,
                compact=True,
            )

    def _open_backups_popup(self):
        try:
            self._yonetici().open_backups_popup(debug=self._debug)
        except Exception as exc:
            self._debug(f"yedek popup açılamadı: {exc}")
            self._yonetici().show_simple_popup(
                title_text="Yedek Hatası",
                body_text=f"Yedek ekranı açılamadı:\n{exc}",
                icon_name="warning.png",
                auto_close_seconds=1.8,
                compact=True,
            )

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/panel.py

SURUM: 1
"""

from __future__ import annotations

from kivy.metrics import dp

from app.ui.kart import Kart
from app.ui.tum_dosya_erisim_paketi.bilesenler import TiklanabilirIcon, start_icon_glow
from app.ui.tum_dosya_erisim_paketi.durum_mantigi import erisim_durumu_getir
from app.ui.tum_dosya_erisim_paketi.basit_popup import show_simple_popup
from app.ui.tum_dosya_erisim_paketi.menu_popup import open_main_menu
from app.ui.tum_dosya_erisim_paketi.erisim_popup import open_access_popup
from app.ui.tum_dosya_erisim_paketi.yedekler_popup import open_backups_popup


class TumDosyaErisimPaneli(Kart):
    def __init__(self, on_status_changed=None, **kwargs):
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

        self.on_status_changed = on_status_changed
        self.menu_icon = None
        self._last_status = None
        self._menu_anim = None

        self._build_ui()
        self.refresh_status()
        self._start_menu_glow()

    def _debug(self, message: str) -> None:
        try:
            print("[TUM_DOSYA_ERISIM]", str(message))
        except Exception:
            pass

    def _build_ui(self):
        self.menu_icon = TiklanabilirIcon(
            source="app/assets/icons/menu.png",
            size_hint=(None, None),
            size=(dp(36), dp(36)),
            opacity=1,
            allow_stretch=True,
            keep_ratio=True,
        )
        self.menu_icon.bind(on_release=self._open_main_menu)
        self.add_widget(self.menu_icon)

    def refresh_status(self):
        onceki = self._last_status
        self._last_status = erisim_durumu_getir(debug=self._debug)

        try:
            if self.on_status_changed and onceki != self._last_status:
                self.on_status_changed(bool(self._last_status))
        except Exception:
            pass

    def _start_menu_glow(self) -> None:
        try:
            self._menu_anim = start_icon_glow(self.menu_icon, 36, 40, 0.60)
        except Exception:
            self._menu_anim = None

    def _open_main_menu(self, *_args):
        try:
            self.refresh_status()
            open_main_menu(
                open_access_popup=lambda: self._open_access_popup(),
                open_backups_popup=lambda: self._open_backups_popup(),
            )
        except Exception as exc:
            self._debug(f"ana menü açılamadı: {exc}")
            show_simple_popup("Menü Hatası", f"Menü açılamadı:\n{exc}")

    def _open_access_popup(self):
        try:
            self.refresh_status()
            open_access_popup(
                status_value=self._last_status,
                debug=self._debug,
            )
        except Exception as exc:
            self._debug(f"erişim popup açılamadı: {exc}")
            show_simple_popup("Erişim Hatası", f"Erişim ekranı açılamadı:\n{exc}")

    def _open_backups_popup(self):
        try:
            open_backups_popup(debug=self._debug)
        except Exception as exc:
            self._debug(f"yedek popup açılamadı: {exc}")
            show_simple_popup("Yedek Hatası", f"Yedek ekranı açılamadı:\n{exc}")
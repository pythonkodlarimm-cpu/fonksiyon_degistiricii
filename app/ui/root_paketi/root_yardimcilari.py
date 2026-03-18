# -*- coding: utf-8 -*-
from __future__ import annotations

import traceback

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.utils import platform


class RootYardimcilariMixin:
    def _debug(self, message: str) -> None:
        try:
            print("[ROOT]", str(message))
        except Exception:
            pass

    def _post_build_refresh(self, _dt) -> None:
        try:
            if self.file_access_panel is not None:
                self.file_access_panel.refresh_status()
        except Exception as exc:
            self._debug(f"post build refresh hatası: {exc}")

    def _resolve_app_version(self) -> str:
        if platform == "android":
            try:
                from jnius import autoclass, cast  # type: ignore

                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                current_activity = cast("android.app.Activity", PythonActivity.mActivity)

                if current_activity is not None:
                    package_info = current_activity.getPackageManager().getPackageInfo(
                        current_activity.getPackageName(),
                        0,
                    )
                    version_name = str(getattr(package_info, "versionName", "") or "").strip()
                    if version_name:
                        return version_name
            except Exception:
                pass

        try:
            from app import __version__ as app_version  # type: ignore

            temiz = str(app_version or "").strip()
            if temiz:
                return temiz
        except Exception:
            pass

        return "GELISTIRME"

    def _build_version_card(self):
        from app.ui.kart import Kart

        kart = Kart(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(28),
            padding=(dp(10), dp(4), dp(10), dp(4)),
            bg=(0.07, 0.09, 0.13, 1),
            border=(0.16, 0.19, 0.25, 1),
            radius=12,
        )

        kart.add_widget(Label(size_hint_x=1))

        self.version_label = Label(
            text=f"Sürüm: {self.app_version_text}",
            size_hint_x=None,
            width=dp(132),
            font_size="11sp",
            color=(0.72, 0.72, 0.76, 1),
            halign="right",
            valign="middle",
        )
        self.version_label.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        kart.add_widget(self.version_label)

        return kart

    def _build_fallback_error_ui(self, hata_metni: str) -> BoxLayout:
        root = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(12),
            size_hint=(1, 1),
        )

        baslik = Label(
            text="RootWidget başlatılamadı",
            size_hint_y=None,
            height=dp(42),
            bold=True,
            halign="center",
            valign="middle",
            color=(1, 0.9, 0.9, 1),
        )
        baslik.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        root.add_widget(baslik)

        mesaj = Label(
            text=hata_metni,
            halign="left",
            valign="top",
            color=(1, 0.85, 0.85, 1),
        )
        mesaj.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))
        root.add_widget(mesaj)

        return root

    def _setup_optional_toast_layer(self) -> None:
        if not self._use_global_toast_overlay:
            self.toast_layer = None
            self._debug("global toast overlay kapalı: editor içi bildirimler kullanılacak")
            return

        try:
            from app.ui.gecici_bildirim import GeciciBildirimKatmani

            self.toast_layer = GeciciBildirimKatmani()
            self.add_widget(self.toast_layer)

            try:
                self._get_gecici_bildirim_servisi().register_layer(self.toast_layer)
            except Exception as exc:
                self._debug(f"toast layer register hatası: {exc}")
        except Exception as exc:
            self.toast_layer = None
            self._debug(f"toast layer kurulamadı: {exc}")

    def _clear_state(self) -> None:
        self.current_file_path = ""
        self.current_session = None
        self.items = []
        self.selected_item = None
        self._pending_update_payload = None

        try:
            if self.dosya_secici is not None:
                self.dosya_secici.clear_selection()
        except Exception:
            pass

        try:
            if self.function_list is not None:
                self.function_list.clear_all()
        except Exception:
            pass

        try:
            if self.editor is not None:
                self.editor.clear_all()
        except Exception:
            pass

    def _clear_view_only(self) -> None:
        self.items = []
        self.selected_item = None
        self._pending_update_payload = None

        try:
            if self.function_list is not None:
                self.function_list.clear_all()
        except Exception:
            pass

        try:
            if self.editor is not None:
                self.editor.clear_all()
        except Exception:
            pass

    def _reset_selection_only(self) -> None:
        self.selected_item = None

        try:
            if self.function_list is not None:
                self.function_list.selected_item = None
                self.function_list.clear_selection()
                self.function_list.clear_new_preview()
                self.function_list.set_selected_preview("")
        except Exception:
            pass

        try:
            if self.editor is not None:
                self.editor.clear_selection()
                self.editor.set_new_code_text("")
        except Exception:
            pass

    def _safe_backup_text(self) -> str:
        try:
            belge_oturumu = self._get_belge_oturumu()
            metin = str(belge_oturumu["son_yedek_yolu"](self.current_session) or "").strip()
            if metin:
                return metin
        except Exception:
            pass
        return "yedek_bilinmiyor"

    def _current_document_name(self) -> str:
        try:
            if self.current_session is None:
                return ""
            belge_oturumu = self._get_belge_oturumu()
            return str(belge_oturumu["oturum_display_name"](self.current_session) or "").strip()
        except Exception:
            return ""
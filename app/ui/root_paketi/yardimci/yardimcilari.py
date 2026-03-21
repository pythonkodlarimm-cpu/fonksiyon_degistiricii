# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/yardimci/yardimcilari.py

ROL:
- Root katmanındaki yardımcı ve ortak akışları toplamak
- Uygulama sürüm bilgisini çözmek
- Fallback hata ekranı üretmek
- Toast layer kurulumunu yönetmek
- State temizleme ve belge yardımcılarını sağlamak
- Hata detaylarını dosya yolu, fonksiyon ve satır bilgisiyle biçimlendirmek
- Hata metnini kopyalanabilir popup olarak gösterebilmek

MİMARİ:
- SADECE yeni yöneticiler kullanılır
- Eski helper/dict/fallback yapı yoktur
- UI davranışını korur
- Sistem ve belge yöneticileri services yöneticisi üzerinden çalışır
- Root paketinin alt yardımcı modülüdür

API UYUMLULUK:
- API 35 uyumlu
- Android ve masaüstü ortamlarında güvenli çalışır
- Android bridge çağrıları güvenli fallback ile korunur

SURUM: 5
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations

import traceback

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

    def _services(self):
        return self._get_services_yoneticisi()

    def _sistem(self):
        return self._services().sistem_yoneticisi()

    def _belge(self):
        return self._services().belge_yoneticisi()

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
                    version_name = str(
                        getattr(package_info, "versionName", "") or ""
                    ).strip()
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

        try:
            core = self._get_core_yoneticisi()
            temiz = str(core.tam_surum() or "").strip()
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
        self.version_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", size)
        )
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
        mesaj.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
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
                self._sistem().register_bildirim_layer(self.toast_layer)
            except Exception as exc:
                self._debug(f"toast layer register hatası: {exc}")
        except Exception as exc:
            self.toast_layer = None
            self._debug(f"toast layer kurulamadı: {exc}")

    def _format_exception_details(self, exc: Exception, title: str = "") -> str:
        exc_type = type(exc).__name__
        dosya = "bilinmiyor"
        fonksiyon = "bilinmiyor"
        satir = "bilinmiyor"
        kaynak_satir = ""

        try:
            tb_list = traceback.extract_tb(exc.__traceback__)
            if tb_list:
                son = tb_list[-1]
                dosya = str(getattr(son, "filename", "bilinmiyor") or "bilinmiyor")
                fonksiyon = str(getattr(son, "name", "bilinmiyor") or "bilinmiyor")
                satir = str(getattr(son, "lineno", "bilinmiyor") or "bilinmiyor")
                kaynak_satir = str(getattr(son, "line", "") or "").strip()
        except Exception:
            pass

        baslik = str(title or "Hata").strip()
        detay = str(exc or "").strip() or "Ayrıntı alınamadı."

        parcalar = [
            f"BASLIK:\n{baslik}",
            f"HATA TÜRÜ:\n{exc_type}",
            f"DOSYA:\n{dosya}",
            f"FONKSİYON:\n{fonksiyon}",
            f"SATIR:\n{satir}",
        ]

        if kaynak_satir:
            parcalar.append(f"KAYNAK SATIR:\n{kaynak_satir}")

        parcalar.append(f"DETAY:\n{detay}")

        try:
            tam_traceback = traceback.format_exc().strip()
            if tam_traceback and tam_traceback != "NoneType: None":
                parcalar.append(f"TRACEBACK:\n{tam_traceback}")
        except Exception:
            pass

        return "\n\n".join(parcalar)

    def _show_detailed_error_popup(self, title: str, exc: Exception) -> None:
        mesaj = self._format_exception_details(exc, title=title)

        try:
            if self.toast_layer is not None:
                self.toast_layer.show(
                    text=mesaj,
                    icon_name="error",
                    title=str(title or "Hata"),
                    duration=3.0,
                )
                return
        except Exception as popup_exc:
            self._debug(f"detailed error popup gösterilemedi: {popup_exc}")

        try:
            self.set_status_error(str(exc))
        except Exception:
            pass

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
            if self.current_session is None:
                return "yedek_bilinmiyor"

            metin = str(
                self._belge().son_yedek_yolu(self.current_session) or ""
            ).strip()
            if metin:
                return metin
        except Exception:
            pass

        return "yedek_bilinmiyor"

    def _current_document_name(self) -> str:
        try:
            if self.current_session is None:
                return ""

            return str(
                self._belge().oturum_display_name(self.current_session) or ""
            ).strip()
        except Exception:
            return ""
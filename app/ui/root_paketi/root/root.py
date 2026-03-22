# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root.py

ROL:
- Uygulamanın ana root widget'ı
- Dosya seçme, fonksiyon tarama, seçim, güncelleme ve geri yükleme akışını yönetir
- UI katmanını çekirdek servislerle bağlar
- Global overlay toast kullanımını opsiyonel tutar
- Tarama sonrası kullanıcıyı fonksiyon listesine yönlendirir
- Fonksiyon seçimi sonrası kullanıcıyı editör alanına yönlendirir
- Android tarafında AdMob banner başlatma akışını güvenli ve gecikmeli biçimde tetikler
- Tarama loading / success overlay entegrasyonunu yönetir
- Uygulama arka plan / geri dönüş durum kaydını ve geri yüklemesini yürütür
- Oturum geri yükleme bilgisini geçici olarak gösterir ve otomatik temizler

MİMARİ:
- Editor paneli editor_paketi/yoneticisi.py üzerinden oluşturulur
- Tüm dosya erişim paneli tum_dosya_erisim_paketi/yoneticisi.py üzerinden oluşturulur
- Fonksiyon listesi fonksiyon_listesi_paketi/yoneticisi.py üzerinden oluşturulur
- Tarama göstergesi tarama_gostergesi_paketi/yoneticisi.py üzerinden oluşturulur
- Reklam işlemleri sadece ServicesYoneticisi üzerinden yürütülür
- Uygulama durumu ServicesYoneticisi -> SistemYoneticisi -> ayar_servisi zinciriyle tutulur
- Root mixin yapısı alt paket klasörlerinden yüklenir
- Eski alias dosyaları kullanılmaz

SURUM: 53
TARIH: 2026-03-22
IMZA: FY.
"""

from __future__ import annotations

import traceback

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform

from app.services.yoneticisi import ServicesYoneticisi
from app.ui.root_paketi.akisi_dosya.dosya_akisi import RootDosyaAkisiMixin
from app.ui.root_paketi.akisi_geri_yukleme.geri_yukleme_akisi import (
    RootGeriYuklemeAkisiMixin,
)
from app.ui.root_paketi.akisi_guncelleme.guncelleme_akisi import (
    RootGuncellemeAkisiMixin,
)
from app.ui.root_paketi.akisi_secim.secim_akisi import RootSecimAkisiMixin
from app.ui.root_paketi.bagimlilik.lazy_imports import RootLazyImportsMixin
from app.ui.root_paketi.durum.status import RootStatusMixin
from app.ui.root_paketi.kaydirma.scroll import RootScrollMixin
from app.ui.root_paketi.yardimci.yardimcilari import RootYardimcilariMixin


class RootWidget(
    FloatLayout,
    RootLazyImportsMixin,
    RootStatusMixin,
    RootScrollMixin,
    RootDosyaAkisiMixin,
    RootSecimAkisiMixin,
    RootGuncellemeAkisiMixin,
    RootGeriYuklemeAkisiMixin,
    RootYardimcilariMixin,
):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.services = ServicesYoneticisi()

        self.main_root = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(8),
            size_hint=(1, 1),
        )
        self.add_widget(self.main_root)

        self.current_file_path = ""
        self.current_session = None
        self.items = []
        self.selected_item = None

        self.scroll = None
        self.main_column = None
        self.file_access_panel = None
        self.dosya_secici = None
        self.function_list = None
        self.editor = None
        self.status = None
        self.version_wrap = None
        self.version_label = None
        self.bottom_bar = None
        self.toast_layer = None
        self.tarama_loading_overlay = None
        self.tarama_success_overlay = None
        self.app_version_text = self._resolve_app_version()

        self._use_global_toast_overlay = False
        self._banner_started = False
        self._banner_retry_count = 0
        self._banner_retry_max = 4
        self._scan_in_progress = False
        self._resume_restore_scheduled = False
        self._memory_app_state = {}
        self._restore_status_reset_event = None

        try:
            self._build_ui()
            self.set_status_info("Hazır.", "onaylandi.png")
            Clock.schedule_once(self._post_build_refresh, 0.08)
            Clock.schedule_once(self._try_start_banner, 0.35)
            Clock.schedule_once(
                lambda *_: self._auto_restore_saved_state_on_start(),
                0.60,
            )
        except Exception:
            hata = traceback.format_exc()
            print(hata)
            self.clear_widgets()
            self.add_widget(self._build_fallback_error_ui(hata))

    def _build_ui(self) -> None:
        from app.ui.dosya_secici import DosyaSecici
        from app.ui.durum_cubugu import DurumCubugu
        from app.ui.editor_paketi import EditorYoneticisi
        from app.ui.fonksiyon_listesi_paketi import FonksiyonListesiYoneticisi
        from app.ui.tarama_gostergesi_paketi import TaramaGostergesiYoneticisi
        from app.ui.tum_dosya_erisim_paketi import TumDosyaErisimYoneticisi

        editor_yoneticisi = EditorYoneticisi()
        tum_dosya_erisim_yoneticisi = TumDosyaErisimYoneticisi()
        fonksiyon_listesi_yoneticisi = FonksiyonListesiYoneticisi()
        tarama_gostergesi_yoneticisi = TaramaGostergesiYoneticisi()

        self.scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8),
            scroll_type=["bars", "content"],
        )

        self.main_column = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            padding=(0, 0, 0, dp(8)),
        )
        self.main_column.bind(minimum_height=self.main_column.setter("height"))

        self.file_access_panel = tum_dosya_erisim_yoneticisi.panel_olustur(
            on_status_changed=self._on_file_access_status_changed,
        )
        self.file_access_panel.size_hint_y = None
        self.main_column.add_widget(self.file_access_panel)

        self.dosya_secici = DosyaSecici(
            on_scan=self.scan_file,
            on_refresh=self.refresh_file,
        )
        self.dosya_secici.size_hint_y = None
        self.main_column.add_widget(self.dosya_secici)

        self.function_list = fonksiyon_listesi_yoneticisi.panel_olustur(
            on_select=self.select_item,
            on_error=lambda exc, title="", detailed_text="": self.set_status_error(
                str(exc or "Fonksiyon listesi hatası"),
                detailed_text=(
                    str(detailed_text or "").strip()
                    or self._format_exception_details(
                        exc,
                        title=title or "Fonksiyon Listesi Hatası",
                    )
                ),
                popup_title=title or "Fonksiyon Listesi Hatası",
            ),
        )
        self.function_list.size_hint_y = None
        self.function_list.height = dp(760)
        self.main_column.add_widget(self.function_list)

        self.editor = editor_yoneticisi.panel_olustur(
            on_update=self.update_selected_function,
            on_restore=self.geri_yukle_secili_belge,
        )
        self.editor.size_hint_y = None
        self.editor.height = dp(900)
        self.main_column.add_widget(self.editor)

        self.scroll.add_widget(self.main_column)
        self.main_root.add_widget(self.scroll)

        self.bottom_bar = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(4),
            padding=(0, dp(2), 0, 0),
        )

        self.status = DurumCubugu()
        self.status.size_hint_y = None
        self.bottom_bar.add_widget(self.status)

        self.version_wrap = self._build_version_card()
        self.bottom_bar.add_widget(self.version_wrap)

        self.bottom_bar.height = (
            int(self.status.height) + int(self.version_wrap.height) + int(dp(4))
        )
        self.main_root.add_widget(self.bottom_bar)

        self._setup_optional_toast_layer()

        try:
            self.tarama_loading_overlay = (
                tarama_gostergesi_yoneticisi.loading_overlay_olustur()
            )
            self.add_widget(self.tarama_loading_overlay)
        except Exception as exc:
            self.tarama_loading_overlay = None
            print(f"[ROOT] Tarama loading overlay oluşturulamadı: {exc}")

        try:
            self.tarama_success_overlay = (
                tarama_gostergesi_yoneticisi.success_overlay_olustur()
            )
            self.add_widget(self.tarama_success_overlay)
        except Exception as exc:
            self.tarama_success_overlay = None
            print(f"[ROOT] Tarama success overlay oluşturulamadı: {exc}")

    def _try_start_banner(self, *_args) -> None:
        print("[ROOT] _try_start_banner çağrıldı.")

        if self._banner_started:
            print("[ROOT] Banner zaten başlatılmış, tekrar denenmeyecek.")
            return

        if platform != "android":
            print(f"[ROOT] Banner başlatılmadı. Platform android değil: {platform}")
            return

        if self._banner_retry_count >= self._banner_retry_max:
            print(
                f"[ROOT] Banner başlatma deneme limiti doldu: "
                f"{self._banner_retry_count}/{self._banner_retry_max}"
            )
            return

        self._banner_retry_count += 1
        print(
            f"[ROOT] Banner başlatma denemesi: "
            f"{self._banner_retry_count}/{self._banner_retry_max}"
        )

        try:
            print(
                "[ROOT] ServicesYoneticisi üzerinden "
                "banner_goster_gecikmeli çağrılıyor..."
            )
            sonuc = self.services.banner_goster_gecikmeli(delay=1.5)

            if sonuc is True:
                self._banner_started = True
                print(
                    "[ROOT] AdMob banner başlatma planlandı/basarılı kabul edildi. "
                    f"Mod={self.services.reklam_modu_etiketi()}"
                )
                return

            print("[ROOT] Banner yöneticisi True dönmedi. Tekrar denenecek.")
            self._schedule_banner_retry(2.0)

        except Exception:
            print("[ROOT] AdMob banner services yöneticisi üzerinden başlatılamadı.")
            print(traceback.format_exc())
            self._schedule_banner_retry(2.0)

    def _schedule_banner_retry(self, delay: float = 2.0) -> None:
        if self._banner_started:
            return

        if self._banner_retry_count >= self._banner_retry_max:
            print(
                f"[ROOT] Retry planlanmadı. Limit dolu: "
                f"{self._banner_retry_count}/{self._banner_retry_max}"
            )
            return

        print(f"[ROOT] Banner tekrar denemesi planlandı. {delay} sn sonra.")
        Clock.schedule_once(self._try_start_banner, delay)

    def _editor_text_al(self) -> str:
        try:
            if self.editor is None:
                return ""

            for method_name in ("get_text", "metni_al", "icerik_al", "kod_al"):
                method = getattr(self.editor, method_name, None)
                if callable(method):
                    value = method()
                    return str(value or "")

            for attr_name in ("text", "metin", "content", "icerik", "code"):
                if hasattr(self.editor, attr_name):
                    value = getattr(self.editor, attr_name)
                    if isinstance(value, str):
                        return value

            editor_input = getattr(self.editor, "editor_input", None)
            if editor_input is not None and hasattr(editor_input, "text"):
                return str(editor_input.text or "")
        except Exception:
            pass

        return ""

    def _editor_text_yaz(self, text: str) -> None:
        temiz = str(text or "")

        try:
            if self.editor is None:
                return

            for method_name in ("set_text", "metni_yaz", "icerik_yaz", "kod_yaz"):
                method = getattr(self.editor, method_name, None)
                if callable(method):
                    method(temiz)
                    return

            editor_input = getattr(self.editor, "editor_input", None)
            if editor_input is not None and hasattr(editor_input, "text"):
                editor_input.text = temiz
                return

            for attr_name in ("text", "metin", "content", "icerik", "code"):
                if hasattr(self.editor, attr_name):
                    setattr(self.editor, attr_name, temiz)
                    return
        except Exception:
            pass

    def _selected_item_identity(self) -> str:
        try:
            if self.selected_item is None:
                return ""

            for attr_name in (
                "identity",
                "full_path",
                "dotted_path",
                "path",
                "name",
            ):
                value = getattr(self.selected_item, attr_name, None)
                if value:
                    return str(value)
        except Exception:
            pass

        return ""

    def _find_item_by_identity_value(self, identity: str):
        temiz = str(identity or "").strip()
        if not temiz:
            return None

        for item in list(self.items or []):
            try:
                for attr_name in (
                    "identity",
                    "full_path",
                    "dotted_path",
                    "path",
                    "name",
                ):
                    value = getattr(item, attr_name, None)
                    if str(value or "").strip() == temiz:
                        return item
            except Exception:
                continue

        return None

    def _collect_app_state(self) -> dict:
        state = {
            "current_file_path": str(self.current_file_path or ""),
            "selected_item_identity": self._selected_item_identity(),
            "editor_text": self._editor_text_al(),
            "scroll_y": None,
        }

        try:
            if self.scroll is not None:
                state["scroll_y"] = float(self.scroll.scroll_y)
        except Exception:
            state["scroll_y"] = None

        return state

    def _sistem(self):
        return self.services.sistem_yoneticisi()

    def _save_app_state_to_settings(self, state: dict) -> None:
        try:
            self._sistem().set_app_state(state if isinstance(state, dict) else {})
        except Exception:
            print("[ROOT] App state settings kaydı başarısız.")
            print(traceback.format_exc())

    def _load_app_state_from_settings(self) -> dict:
        try:
            state = self._sistem().get_app_state(default={})
            return state if isinstance(state, dict) else {}
        except Exception:
            print("[ROOT] App state settings okuma başarısız.")
            print(traceback.format_exc())
            return {}

    def _show_temporary_restore_status(
        self,
        message: str,
        icon_name: str = "onaylandi.png",
        duration: float = 3.5,
    ) -> None:
        try:
            if self._restore_status_reset_event is not None:
                self._restore_status_reset_event.cancel()
        except Exception:
            pass
        self._restore_status_reset_event = None

        try:
            self.set_status_info(str(message or "Oturum geri yüklendi."), icon_name)
        except Exception:
            return

        def _reset_status(*_args):
            self._restore_status_reset_event = None
            try:
                self.set_status_info("Hazır.", "onaylandi.png")
            except Exception:
                pass

        try:
            self._restore_status_reset_event = Clock.schedule_once(
                _reset_status,
                float(duration),
            )
        except Exception:
            pass

    def uygulama_durumu_kaydet(self) -> None:
        try:
            state = self._collect_app_state()
            self._memory_app_state = dict(state)
            self._save_app_state_to_settings(state)
            print("[ROOT] Uygulama durumu kaydedildi.")
        except Exception:
            print("[ROOT] Uygulama durumu kaydedilemedi.")
            print(traceback.format_exc())

    def _apply_saved_state(self, state: dict) -> None:
        if not isinstance(state, dict) or not state:
            return

        current_file_path = str(state.get("current_file_path", "") or "").strip()
        selected_item_identity = str(
            state.get("selected_item_identity", "") or ""
        ).strip()
        editor_text = str(state.get("editor_text", "") or "")
        scroll_y = state.get("scroll_y", None)

        try:
            if current_file_path and self.dosya_secici is not None:
                self.dosya_secici.set_path(current_file_path)
        except Exception:
            pass

        try:
            if current_file_path and self.current_file_path != current_file_path:
                self.current_file_path = current_file_path
        except Exception:
            pass

        try:
            if current_file_path and not self.items:
                try:
                    self._reload_items_from_current_file()
                except Exception:
                    pass
        except Exception:
            pass

        try:
            if selected_item_identity:
                bulunan = self._find_item_by_identity_value(selected_item_identity)
                if bulunan is not None:
                    self.selected_item = bulunan
        except Exception:
            pass

        try:
            if editor_text:
                self._editor_text_yaz(editor_text)
        except Exception:
            pass

        try:
            if scroll_y is not None and self.scroll is not None:
                self.scroll.scroll_y = float(scroll_y)
        except Exception:
            pass

    def uygulama_durumu_geri_yukle(self) -> None:
        try:
            state = {}
            if isinstance(self._memory_app_state, dict) and self._memory_app_state:
                state = dict(self._memory_app_state)

            if not state:
                state = self._load_app_state_from_settings()

            if not state:
                print("[ROOT] Geri yüklenecek app state bulunamadı.")
                return

            if self._resume_restore_scheduled:
                return

            self._resume_restore_scheduled = True

            def _restore(*_args):
                self._resume_restore_scheduled = False
                try:
                    self._apply_saved_state(state)
                    self._show_temporary_restore_status(
                        "Oturum geri yüklendi.",
                        "onaylandi.png",
                        3.5,
                    )
                    print("[ROOT] Uygulama durumu geri yüklendi.")
                except Exception:
                    print("[ROOT] Uygulama durumu geri yüklenemedi.")
                    print(traceback.format_exc())

            Clock.schedule_once(_restore, 0.10)

        except Exception:
            print("[ROOT] uygulama_durumu_geri_yukle çağrısı başarısız.")
            print(traceback.format_exc())

    def _auto_restore_saved_state_on_start(self) -> None:
        try:
            state = self._load_app_state_from_settings()
            if not state:
                return

            current_file_path = str(state.get("current_file_path", "") or "").strip()
            editor_text = str(state.get("editor_text", "") or "")

            if not current_file_path and not editor_text:
                return

            self._apply_saved_state(state)
            self._show_temporary_restore_status(
                "Önceki oturum geri yüklendi.",
                "onaylandi.png",
                3.5,
            )
            print("[ROOT] Başlangıçta kayıtlı app state uygulandı.")
        except Exception:
            print("[ROOT] Başlangıç app state geri yükleme başarısız.")
            print(traceback.format_exc())

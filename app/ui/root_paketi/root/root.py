# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root.py

ROL:
- Uygulamanın ana root widget'ıdır
- Alt root_akisi modüllerini birleştirerek tek bir çalışma yüzeyi sunar
- Dosya seçme, fonksiyon tarama, seçim, güncelleme ve geri yükleme akışlarını orkestre eder
- UI katmanını servis katmanı ile bağlar
- Banner, geçiş reklamı, geçici RAM state restore ve dil yenileme akışlarını başlatır
- Modüler mixin mimarisinin birleşim noktasıdır
- Root içindeki oluşturulan UI bileşenlerine ortak ServicesYoneticisi instance'ını güvenli biçimde bağlar

MİMARİ:
- Dosya/Seçim/Güncelleme/Geri yükleme eski root_paketi mixin'leri korunur
- Yeni root_akisi modülleri parçalı sorumluluk yaklaşımıyla eklenmiştir
- UI kurulumu, banner, tarama geçişi, editor state, geçici status, dil akışı ve RAM state akışları
  alt modüllerden gelir
- Root sadece üst orkestrasyon ve kalan bağlayıcı metodları içerir
- Lazy import sistemi alt paketlerde __init__.py ve yonetici.py üzerinden korunur
- Tek ServicesYoneticisi instance'ı root içinde oluşturulur ve alt UI bileşenlerine enjekte edilir
- Reklam akışında mevcut davranış korunur; sadece görünürlük ve bağlama tarafı güvenli hale getirilir
- Dil akışı RootDilAkisiMixin ile birlikte çalışır ve root callback zinciri korunur

NOTLAR:
- Disk tabanlı app state restore kullanılmaz
- Uygulama state yalnızca aynı process içindeki RAM bellekte tutulur
- Android dışı platformlarda banner / interstitial akışları güvenli biçimde pas geçilir
- Root method adları mevcut sistemle geriye uyumlu tutulmuştur
- Reklam görünürlüğü için mevcut başlangıç akışı korunur; yalnızca fail-soft wrapper ve
  ortak services bağlama desteği güçlendirilmiştir
- Dil değişiminde hem doğrudan hem de schedule_once tabanlı tekrar refresh uygulanır

SURUM: 70
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import traceback
from threading import Thread

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from app.services import ServicesYoneticisi
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
from .root_akisi.app_state_kaydet_geri_yukle import (
    RootAppStateKaydetGeriYukleMixin,
)
from .root_akisi.banner_akisi import RootBannerAkisiMixin
from .root_akisi.dil_akisi import RootDilAkisiMixin
from .root_akisi.dil_yardimcilari import RootDilYardimcilariMixin
from .root_akisi.editor_state import RootEditorStateMixin
from .root_akisi.gecici_status import RootGeciciStatusMixin
from .root_akisi.gecis_reklami_on_yukleme import (
    RootGecisReklamiOnYuklemeMixin,
)
from .root_akisi.sistem_ve_app_state import RootSistemVeAppStateMixin
from .root_akisi.tarama_gecis_ve_liste_acma import (
    RootTaramaGecisVeListeAcmaMixin,
)
from .root_akisi.ui_kurulumu import RootUiKurulumuMixin


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
    RootDilAkisiMixin,
    RootDilYardimcilariMixin,
    RootEditorStateMixin,
    RootSistemVeAppStateMixin,
    RootGeciciStatusMixin,
    RootGecisReklamiOnYuklemeMixin,
    RootBannerAkisiMixin,
    RootTaramaGecisVeListeAcmaMixin,
    RootUiKurulumuMixin,
    RootAppStateKaydetGeriYukleMixin,
):
    """
    Uygulamanın ana root widget'ı.

    Alt modüllerden gelen akışları tek yerde birleştirir.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.services = ServicesYoneticisi()

        try:
            self.services.aktif_dili_ayardan_yukle(default="tr")
        except Exception:
            pass

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

        self._pending_scan_result = None
        self._pending_scan_item_count = 0
        self._pending_scan_display_name = ""
        self._pending_scan_ready = False
        self._scan_transition_busy = False

        self._update_cta_visible = False
        self._update_state: dict = {}
        self._update_check_in_progress = False

        try:
            self._build_ui()
            self._bind_services_to_ui()
            self._full_language_refresh()
            self.set_status_info(self._m("app_ready", "Hazır."), "onaylandi.png")
            Clock.schedule_once(self._post_build_refresh, 0.08)
            Clock.schedule_once(self._rebinding_ui_services_after_layout, 0.12)
            Clock.schedule_once(self._try_start_banner, 0.35)
            Clock.schedule_once(self._try_preload_interstitial, 0.80)
            Clock.schedule_once(self._check_update_from_endpoint, 1.20)
        except Exception:
            hata = traceback.format_exc()
            print(hata)
            self.clear_widgets()
            self.add_widget(self._build_fallback_error_ui(hata))

    # =========================================================
    # UI <-> SERVICES BAGLAMA
    # =========================================================
    def _bind_service_to_widget(self, widget) -> bool:
        """
        Verilen widget üzerinde services alanı varsa root'taki ortak
        ServicesYoneticisi instance'ını bağlar.

        Not:
        - Widget services alanı expose etmiyorsa sessizce geçilir
        - Mevcut davranışı bozmamak için zorlayıcı yapı kullanılmaz

        Args:
            widget: Services bağlanacak hedef widget

        Returns:
            bool: Başarılı bağlandıysa True
        """
        if widget is None:
            return False

        try:
            mevcut = getattr(widget, "services", None)
            if mevcut is self.services:
                return True
        except Exception:
            pass

        try:
            if hasattr(widget, "services"):
                setattr(widget, "services", self.services)
                return True
        except Exception:
            pass

        try:
            setter = getattr(widget, "set_services", None)
            if callable(setter):
                setter(self.services)
                return True
        except Exception:
            pass

        return False

    def _bind_services_to_ui(self) -> None:
        """
        Root içindeki ana UI bileşenlerine ortak services instance'ını bağlar.
        """
        try:
            self._bind_service_to_widget(self.file_access_panel)
        except Exception:
            pass

        try:
            self._bind_service_to_widget(self.dosya_secici)
        except Exception:
            pass

        try:
            self._bind_service_to_widget(self.function_list)
        except Exception:
            pass

        try:
            self._bind_service_to_widget(self.editor)
        except Exception:
            pass

        try:
            self._bind_service_to_widget(self.status)
        except Exception:
            pass

        try:
            self._bind_service_to_widget(self.version_wrap)
        except Exception:
            pass

        try:
            self._bind_service_to_widget(self.bottom_bar)
        except Exception:
            pass

        try:
            self._bind_service_to_widget(self.main_root)
        except Exception:
            pass

        try:
            self._bind_service_to_widget(self.main_column)
        except Exception:
            pass

        try:
            self._bind_service_to_widget(self.scroll)
        except Exception:
            pass

    def _rebinding_ui_services_after_layout(self, *_args) -> None:
        """
        UI layout kurulduktan kısa süre sonra services bağını tekrar doğrular.
        """
        try:
            self._bind_services_to_ui()
        except Exception:
            pass

    # =========================================================
    # INTERSTITIAL WRAPPER
    # =========================================================
    def _try_preload_interstitial(self, *_args) -> None:
        """
        Geçiş reklamı preload akışını fail-soft şekilde başlatır.
        """
        try:
            self._preload_interstitial()
        except Exception:
            print("[ROOT] _try_preload_interstitial başarısız.")
            print(traceback.format_exc())

    # =========================================================
    # LANGUAGE CALLBACK
    # =========================================================
    def _on_language_changed(self, code: str = "") -> None:
        """
        Dil değişimi callback akışını yönetir.

        Args:
            code: Yeni dil kodu.
        """
        temiz_kod = str(code or "").strip()

        if temiz_kod:
            try:
                self.services.dil_degistir(temiz_kod)
            except Exception:
                try:
                    self.services.set_language(temiz_kod)
                except Exception:
                    pass

        try:
            self._bind_services_to_ui()
        except Exception:
            pass

        try:
            clear_translation_cache = getattr(self, "_clear_translation_cache", None)
            if callable(clear_translation_cache):
                clear_translation_cache()
        except Exception:
            pass

        try:
            self._full_language_refresh()
        except Exception:
            pass

        try:
            mesaj = self._m("language_updated", "Dil güncellendi.")
        except Exception:
            mesaj = "Dil güncellendi."

        try:
            self.set_status_success(str(mesaj or "Dil güncellendi."))
        except Exception:
            pass

        try:
            self._clear_update_cta()
        except Exception:
            pass

        try:
            Clock.schedule_once(lambda *_: self._bind_services_to_ui(), 0.01)
            Clock.schedule_once(
                lambda *_: (
                    callable(getattr(self, "_clear_translation_cache", None))
                    and self._clear_translation_cache()
                ),
                0.015,
            )
            Clock.schedule_once(lambda *_: self._full_language_refresh(), 0.02)
            Clock.schedule_once(lambda *_: self._full_language_refresh(), 0.10)
            Clock.schedule_once(lambda *_: self._full_language_refresh(), 0.20)
        except Exception:
            pass

        try:
            Clock.schedule_once(self._check_update_from_endpoint, 0.20)
        except Exception:
            pass

        try:
            Clock.schedule_once(self._ensure_banner_visibility, 0.30)
            Clock.schedule_once(self._ensure_banner_visibility, 1.00)
        except Exception:
            pass

    # =========================================================
    # UPDATE CTA / VERSION CHECK
    # =========================================================
    def _current_app_version(self) -> str:
        """
        Mevcut uygulama sürüm metnini döndürür.

        Returns:
            str
        """
        try:
            return str(self.app_version_text or "").strip()
        except Exception:
            return ""

    def _check_update_from_endpoint(self, *_args) -> None:
        """
        Services katmanı üzerinden uzak sürüm kontrolünü başlatır.
        """
        if self._pending_scan_ready:
            return

        if self._update_check_in_progress:
            return

        try:
            if not self.services.guncelleme_kontrol_aktif_mi():
                return
        except Exception:
            return

        mevcut_surum = self._current_app_version()
        if not mevcut_surum:
            return

        self._update_check_in_progress = True

        def _worker():
            try:
                result = self.services.guncelleme_durumu_hesapla(mevcut_surum)
            except Exception:
                result = {}
            Clock.schedule_once(lambda *_: self._apply_update_check_result(result), 0)

        try:
            Thread(target=_worker, daemon=True).start()
        except Exception:
            self._update_check_in_progress = False

    def _apply_update_check_result(self, result: dict) -> None:
        """
        Güncelleme kontrol sonucunu root state ve status CTA'ya uygular.

        Args:
            result: Services katmanından gelen sürüm kontrol çıktısı.
        """
        self._update_check_in_progress = False

        try:
            self._update_state = dict(result or {})
        except Exception:
            self._update_state = {}

        if self._pending_scan_ready:
            return

        update_available = bool(self._update_state.get("update_available", False))
        unsupported_version = bool(self._update_state.get("unsupported_version", False))
        force_update = bool(self._update_state.get("force_update", False))

        if not update_available and not unsupported_version:
            self._clear_update_cta()
            return

        if force_update or unsupported_version:
            self._show_update_cta(force=True)
            return

        self._show_update_cta(force=False)

    def _show_update_cta(self, force: bool = False) -> None:
        """
        Status üzerinde güncelleme CTA aksiyonu gösterir.

        Args:
            force: Zorunlu güncelleme durumu.
        """
        if self._pending_scan_ready:
            return

        mesaj = str(
            self._update_state.get("message", "")
            or self._m("new_version_available", "Yeni sürüm mevcut.")
        ).strip()

        if force and not mesaj:
            mesaj = self._m("new_version_required", "Yeni sürüm gerekli.")

        try:
            if self.status is not None and hasattr(self.status, "set_action"):
                self.status.set_action(
                    text=mesaj
                    or self._m("new_version_available", "Yeni sürüm mevcut."),
                    button_text=self.services.guncelleme_buton_metni(),
                    callback=self._open_play_store_for_update,
                    icon_name="warning.png",
                    tone="warning",
                )
                self._update_cta_visible = True
                print("[ROOT] Güncelleme CTA gösterildi.")
        except Exception:
            print("[ROOT] Güncelleme CTA gösterilemedi.")
            print(traceback.format_exc())

    def _clear_update_cta(self) -> None:
        """
        Status üzerindeki güncelleme CTA aksiyonunu temizler.
        """
        self._update_cta_visible = False
        try:
            if (
                self.status is not None
                and hasattr(self.status, "clear_action")
                and not self._pending_scan_ready
            ):
                self.status.clear_action()
        except Exception:
            pass

    def _open_play_store_for_update(self) -> None:
        """
        Play Store güncelleme sayfasını açmayı dener.
        """
        try:
            ok = self.services.play_store_sayfasini_ac(
                package_name=self.services.play_store_package_name()
            )
            if ok:
                print("[ROOT] Play Store güncelleme sayfası açıldı.")
                return

            self.set_status_warning(
                self._m("play_store_open_failed", "Play Store açılamadı.")
            )
        except Exception:
            print("[ROOT] Play Store açma akışı başarısız.")
            print(traceback.format_exc())
            self.set_status_warning(
                self._m("play_store_open_failed", "Play Store açılamadı.")
)

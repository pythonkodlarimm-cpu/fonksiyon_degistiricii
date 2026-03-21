# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root.py

ROL:
- Uygulamanın ana root widget'ı
- Dosya seçme, fonksiyon tarama, seçim, güncelleme ve geri yükleme akışını yönetir
- UI katmanını çekirdek servislerle bağlar
- Fonksiyon güncellemede replace stratejisi karar akışını yönetir
- Global overlay toast kullanımını opsiyonel tutar
- Tarama sonrası kullanıcıyı fonksiyon listesine yönlendirir
- Fonksiyon seçimi sonrası kullanıcıyı editör alanına yönlendirir
- Android tarafında AdMob banner başlatma akışını güvenli biçimde tetikler
- Tarama loading / success overlay entegrasyonunu yönetir

MİMARİ:
- Editor paneli editor_paketi/yoneticisi.py üzerinden oluşturulur
- Tüm dosya erişim paneli tum_dosya_erisim_paketi/yoneticisi.py üzerinden oluşturulur
- Fonksiyon listesi fonksiyon_listesi_paketi/yoneticisi.py üzerinden oluşturulur
- Tarama göstergesi tarama_gostergesi_paketi/yoneticisi.py üzerinden oluşturulur
- Root mixin yapısı alt paket klasörlerinden yüklenir
- Eski alias dosyaları kullanılmaz

SURUM: 45
TARIH: 2026-03-20
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

        self._pending_update_payload = None
        self._replace_karar_servisi = None

        self._use_global_toast_overlay = False
        self._banner_started = False
        self._scan_in_progress = False

        try:
            self._build_ui()
            self.set_status_info("Hazır.", "onaylandi.png")
            Clock.schedule_once(self._post_build_refresh, 0.08)
            Clock.schedule_once(self._try_start_banner, 0.35)
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
        from app.ui.tum_dosya_erisim_paketi import TumDosyaErisimYoneticisi
        from app.ui.tarama_gostergesi_paketi import TaramaGostergesiYoneticisi

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

        # =====================================================
        # TARAMA GÖSTERGELERİ
        # FloatLayout root üstüne eklenir; main_root içine konmaz
        # Böylece tüm ekranı kaplayan overlay gibi davranır.
        # =====================================================
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
        if self._banner_started:
            return

        if platform != "android":
            return

        try:
            reklam_yoneticisi = self._get_reklam_yoneticisi()
            reklam_yoneticisi.banner_goster()
            self._banner_started = True
            print("[ROOT] AdMob banner başlatıldı.")
        except Exception as exc:
            print(f"[ROOT] AdMob banner başlatılamadı: {exc}")
# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root.py

ROL:
- Uygulamanın ana root widget'ı
- Dosya seçme, fonksiyon tarama, seçim, güncelleme ve geri yükleme akışını yönetir
- UI katmanını çekirdek servislerle bağlar
- Fonksiyon güncellemede replace stratejisi karar akışını yönetir
- Global overlay toast kullanımını opsiyonel tutar
- Tarama sonrası kullanıcıyı fonksiyon listesine yönlendirir
- Fonksiyon seçimi sonrası kullanıcıyı editör alanına yönlendirir
- Android tarafında AdMob banner başlatma akışını güvenli biçimde tetikler
- Büyük ekranlı cihazlarda adaptif yerleşim uygular

SURUM: 41
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

import traceback

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform

from app.ui.root_paketi.root_dosya_akisi import RootDosyaAkisiMixin
from app.ui.root_paketi.root_geri_yukleme_akisi import RootGeriYuklemeAkisiMixin
from app.ui.root_paketi.root_guncelleme_akisi import RootGuncellemeAkisiMixin
from app.ui.root_paketi.root_lazy_imports import RootLazyImportsMixin
from app.ui.root_paketi.root_scroll import RootScrollMixin
from app.ui.root_paketi.root_secim_akisi import RootSecimAkisiMixin
from app.ui.root_paketi.root_status import RootStatusMixin
from app.ui.root_paketi.root_yardimcilari import RootYardimcilariMixin


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
        self.app_version_text = self._resolve_app_version()

        self.content_wrap = None
        self._responsive_trigger = None
        self._pending_update_payload = None
        self._replace_karar_servisi = None

        self._use_global_toast_overlay = False
        self._banner_started = False

        try:
            self._build_ui()
            self.set_status_info("Hazır.", "onaylandi.png")
            Clock.schedule_once(self._post_build_refresh, 0.08)
            Clock.schedule_once(self._try_start_banner, 0.35)
            Clock.schedule_once(self._apply_responsive_layout, 0.05)

            self.bind(size=self._schedule_responsive_layout)
            Window.bind(size=self._schedule_responsive_layout)
        except Exception:
            hata = traceback.format_exc()
            print(hata)
            self.clear_widgets()
            self.add_widget(self._build_fallback_error_ui(hata))

    def _build_ui(self) -> None:
        from app.ui.dosya_secici import DosyaSecici
        from app.ui.durum_cubugu import DurumCubugu
        from app.ui.editor_paneli import EditorPaneli
        from app.ui.fonksiyon_listesi import FonksiyonListesi
        from app.ui.tum_dosya_erisim_paneli import TumDosyaErisimPaneli

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

        self.file_access_panel = TumDosyaErisimPaneli(
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

        self.content_wrap = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
        )
        self.content_wrap.bind(minimum_height=self.content_wrap.setter("height"))

        self.function_list = FonksiyonListesi(
            on_select=self.select_item,
        )

        self.editor = EditorPaneli(
            on_update=self.update_selected_function,
            on_restore=self.geri_yukle_secili_belge,
        )

        self.content_wrap.add_widget(self.function_list)
        self.content_wrap.add_widget(self.editor)

        self.main_column.add_widget(self.content_wrap)

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

    def _window_width(self) -> float:
        try:
            return float(Window.width or 0)
        except Exception:
            return 0.0

    def _window_height(self) -> float:
        try:
            return float(Window.height or 0)
        except Exception:
            return 0.0

    def _is_large_screen(self) -> bool:
        try:
            return self._window_width() >= dp(900)
        except Exception:
            return False

    def _schedule_responsive_layout(self, *_args) -> None:
        try:
            if self._responsive_trigger is not None:
                self._responsive_trigger.cancel()
        except Exception:
            pass

        self._responsive_trigger = Clock.schedule_once(self._apply_responsive_layout, 0)

    def _apply_responsive_layout(self, *_args) -> None:
        if self.content_wrap is None or self.function_list is None or self.editor is None:
            return

        buyuk_ekran = self._is_large_screen()

        try:
            pencere_h = max(dp(720), self._window_height())
        except Exception:
            pencere_h = dp(720)

        alt_bar_h = 0
        try:
            if self.bottom_bar is not None:
                alt_bar_h = float(self.bottom_bar.height or 0)
        except Exception:
            alt_bar_h = 0

        if buyuk_ekran:
            ortak_yukseklik = max(
                dp(760),
                pencere_h - alt_bar_h - dp(170),
            )

            self.content_wrap.orientation = "horizontal"
            self.content_wrap.spacing = dp(10)
            self.content_wrap.size_hint_y = None
            self.content_wrap.height = ortak_yukseklik

            self.function_list.size_hint_x = 0.42
            self.function_list.size_hint_y = 1
            self.function_list.height = ortak_yukseklik

            self.editor.size_hint_x = 0.58
            self.editor.size_hint_y = 1
            self.editor.height = ortak_yukseklik
        else:
            self.content_wrap.orientation = "vertical"
            self.content_wrap.spacing = dp(10)
            self.content_wrap.size_hint_y = None

            self.function_list.size_hint_x = 1
            self.function_list.size_hint_y = None
            self.function_list.height = dp(760)

            self.editor.size_hint_x = 1
            self.editor.size_hint_y = None
            self.editor.height = dp(900)

            self.content_wrap.height = self.function_list.height + self.editor.height + dp(10)

        try:
            self.main_column.height = self.main_column.minimum_height
        except Exception:
            pass

    def _try_start_banner(self, *_args) -> None:
        if self._banner_started:
            return

        if platform != "android":
            return

        try:
            from app.services.admob_banner import show_banner

            show_banner()
            self._banner_started = True
            print("[ROOT] AdMob banner başlatıldı.")
        except Exception as exc:
            print(f"[ROOT] AdMob banner başlatılamadı: {exc}")

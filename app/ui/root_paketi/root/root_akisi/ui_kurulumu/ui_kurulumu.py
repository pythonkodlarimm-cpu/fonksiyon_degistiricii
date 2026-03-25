# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/ui_kurulumu/ui_kurulumu.py

ROL:
- Root katmanındaki ana UI kurulum akışını tek modülde toplar
- Dosya seçici, durum çubuğu, editör, fonksiyon listesi ve erişim paneli gibi
  ana bileşenlerin oluşturulmasını yönetir
- Tarama loading/success overlay katmanlarını güvenli biçimde ekler
- UI bileşenlerini runtime sırasında lazy resolve eder ve cache içinde tutar
- Root içindeki _build_ui akışını sade, modüler ve tekrar kullanılabilir hale getirir

MİMARİ:
- Bu modül mixin mantığıyla çalışır
- Import-level lazy import yerine runtime lazy resolve + cache uygulanır
- Widget sınıfları ve yönetici sınıfları ihtiyaç anında import edilir
- İlk başarılı çözümleme sonrası class referansları cache içinde tutulur
- Fail-soft yaklaşım uygulanır; bir bileşen hata verirse root tamamen çökmeden
  mümkün olan yerlerde güvenli fallback uygulanır
- Root nesnesinde self.main_root, self.services gibi temel alanların bulunması beklenir

BEKLENEN ROOT ALANLARI:
- self.main_root
- self.services

OLUSTURULAN ROOT ALANLARI:
- self.scroll
- self.main_column
- self.file_access_panel
- self.dosya_secici
- self.function_list
- self.editor
- self.status
- self.version_wrap
- self.bottom_bar
- self.tarama_loading_overlay
- self.tarama_success_overlay

BEKLENEN ROOT METODLARI:
- self.scan_file(...)
- self.refresh_file(...)
- self.select_item(...)
- self.update_selected_function(...)
- self.geri_yukle_secili_belge(...)
- self._on_language_changed(...)
- self._on_file_access_status_changed(...)
- self.set_status_error(...)
- self._m(...)
- self._format_exception_details(...)
- self._build_version_card(...)
- self._setup_optional_toast_layer(...)

NOTLAR:
- UI kurulumunda yöneticiler ve widget sınıfları doğrudan üstte import edilmez
- Tüm kritik resolve işlemleri cache desteklidir
- Tarama overlay katmanları oluşturulamazsa root çalışmaya devam eder
- Bu modül sadece kurulum yapar; iş mantığı başka akış modüllerindedir

SURUM: 1
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import traceback

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView


class RootUiKurulumuMixin:
    """
    Root katmanındaki UI kurulum davranışlarını sağlayan mixin.
    """

    # =========================================================
    # CACHE
    # =========================================================
    def _ensure_ui_kurulumu_cache(self) -> None:
        """
        UI kurulumu için yardımcı cache alanlarını hazırlar.
        """
        try:
            if not hasattr(self, "_ui_kurulumu_cache"):
                self._ui_kurulumu_cache = {}
        except Exception:
            pass

    def _ui_kurulumu_cache_temizle(self) -> None:
        """
        UI kurulumu cache alanlarını temizler.
        """
        try:
            self._ui_kurulumu_cache = {}
        except Exception:
            pass

    def _ui_cache_get(self, key: str, default=None):
        """
        Cache içinden güvenli biçimde değer okur.
        """
        try:
            self._ensure_ui_kurulumu_cache()
            return self._ui_kurulumu_cache.get(key, default)
        except Exception:
            return default

    def _ui_cache_set(self, key: str, value) -> None:
        """
        Cache içine güvenli biçimde değer yazar.
        """
        try:
            self._ensure_ui_kurulumu_cache()
            self._ui_kurulumu_cache[key] = value
        except Exception:
            pass

    # =========================================================
    # INTERNAL HELPERS
    # =========================================================
    def _safe_getattr(self, name: str, default=None):
        """
        Root üzerinde güvenli getattr çağrısı yapar.
        """
        try:
            return getattr(self, name, default)
        except Exception:
            return default

    def _resolve_root_method(self, method_name: str):
        """
        Root üzerindeki callable metodu lazy resolve eder ve cache'ler.

        Args:
            method_name: Çözümlenecek metod adı.

        Returns:
            callable | None
        """
        cache_key = None

        try:
            cache_key = f"root_method::{id(self)}::{method_name}"
            cached = self._ui_cache_get(cache_key, None)
            if cached is not None:
                return cached
        except Exception:
            cache_key = None

        bulunan = None
        try:
            method = getattr(self, method_name, None)
            if callable(method):
                bulunan = method
        except Exception:
            bulunan = None

        try:
            if cache_key is not None and bulunan is not None:
                self._ui_cache_set(cache_key, bulunan)
        except Exception:
            pass

        return bulunan

    def _resolve_import(self, import_path: str, attr_name: str):
        """
        Verilen import yolundan hedef attribute'u lazy import ile çözer ve cache'ler.

        Args:
            import_path: Modül import yolu.
            attr_name: Modül içindeki hedef sınıf / nesne adı.

        Returns:
            object | None
        """
        cache_key = f"import::{import_path}::{attr_name}"

        try:
            cached = self._ui_cache_get(cache_key, None)
            if cached is not None:
                return cached
        except Exception:
            pass

        try:
            module = __import__(import_path, fromlist=[attr_name])
            value = getattr(module, attr_name, None)
            if value is not None:
                self._ui_cache_set(cache_key, value)
            return value
        except Exception:
            print(
                "[ROOT_UI_KURULUMU] Import çözümlenemedi: "
                f"{import_path}.{attr_name}"
            )
            print(traceback.format_exc())
            return None

    def _new_instance(self, import_path: str, attr_name: str, *args, **kwargs):
        """
        Lazy resolve edilen sınıftan örnek oluşturmaya çalışır.

        Args:
            import_path: Modül import yolu.
            attr_name: Sınıf adı.
            *args: Constructor argümanları.
            **kwargs: Constructor keyword argümanları.

        Returns:
            object | None
        """
        cls = self._resolve_import(import_path, attr_name)
        if cls is None:
            return None

        try:
            return cls(*args, **kwargs)
        except Exception:
            print(
                "[ROOT_UI_KURULUMU] Örnek oluşturulamadı: "
                f"{import_path}.{attr_name}"
            )
            print(traceback.format_exc())
            return None

    def _root_call(self, method_name: str, *args, **kwargs):
        """
        Root üzerindeki metodu güvenli biçimde çağırır.

        Returns:
            tuple[bool, Any]
        """
        try:
            method = self._resolve_root_method(method_name)
            if callable(method):
                return True, method(*args, **kwargs)
        except Exception:
            pass
        return False, None

    # =========================================================
    # CLASS / MANAGER RESOLVE
    # =========================================================
    def _get_dosya_secici_class(self):
        return self._resolve_import("app.ui.dosya_secici", "DosyaSecici")

    def _get_durum_cubugu_class(self):
        return self._resolve_import("app.ui.durum_cubugu", "DurumCubugu")

    def _get_editor_yoneticisi_class(self):
        return self._resolve_import("app.ui.editor_paketi", "EditorYoneticisi")

    def _get_fonksiyon_listesi_yoneticisi_class(self):
        return self._resolve_import(
            "app.ui.fonksiyon_listesi_paketi",
            "FonksiyonListesiYoneticisi",
        )

    def _get_tarama_gostergesi_yoneticisi_class(self):
        return self._resolve_import(
            "app.ui.tarama_gostergesi_paketi",
            "TaramaGostergesiYoneticisi",
        )

    def _get_tum_dosya_erisim_yoneticisi_class(self):
        return self._resolve_import(
            "app.ui.tum_dosya_erisim_paketi",
            "TumDosyaErisimYoneticisi",
        )

    # =========================================================
    # COMPONENT BUILDERS
    # =========================================================
    def _build_scroll_and_main_column(self) -> None:
        """
        Scroll alanı ve ana dikey kolon yapısını kurar.
        """
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

    def _build_file_access_panel(self, tum_dosya_erisim_yoneticisi) -> None:
        """
        Tüm dosya erişim panelini oluşturur.
        """
        panel = tum_dosya_erisim_yoneticisi.panel_olustur(
            services=self._safe_getattr("services", None),
            on_language_changed=self._safe_getattr("_on_language_changed", None),
            on_status_changed=self._safe_getattr(
                "_on_file_access_status_changed",
                None,
            ),
        )
        self.file_access_panel = panel
        self.file_access_panel.size_hint_y = None
        self.main_column.add_widget(self.file_access_panel)

    def _build_dosya_secici(self, dosya_secici_class) -> None:
        """
        Dosya seçici widget'ını oluşturur.
        """
        self.dosya_secici = dosya_secici_class(
            on_scan=self._safe_getattr("scan_file", None),
            on_refresh=self._safe_getattr("refresh_file", None),
            services=self._safe_getattr("services", None),
        )
        self.dosya_secici.size_hint_y = None
        self.main_column.add_widget(self.dosya_secici)

    def _build_function_list(self, fonksiyon_listesi_yoneticisi) -> None:
        """
        Fonksiyon listesi panelini oluşturur.
        """

        def _on_error(exc, title="", detailed_text=""):
            hata_metin = str(
                exc
                or self._root_call(
                    "_m",
                    "function_list_error",
                    "Fonksiyon listesi hatası",
                )[1]
                or "Fonksiyon listesi hatası"
            )

            detay = str(detailed_text or "").strip()
            if not detay:
                _, formatted = self._root_call(
                    "_format_exception_details",
                    exc,
                    title=title
                    or self._root_call(
                        "_m",
                        "function_list_error_title",
                        "Fonksiyon Listesi Hatası",
                    )[1]
                    or "Fonksiyon Listesi Hatası",
                )
                detay = str(formatted or "")

            popup_title = (
                title
                or self._root_call(
                    "_m",
                    "function_list_error_title",
                    "Fonksiyon Listesi Hatası",
                )[1]
                or "Fonksiyon Listesi Hatası"
            )

            self._root_call(
                "set_status_error",
                hata_metin,
                detailed_text=detay,
                popup_title=popup_title,
            )

        self.function_list = fonksiyon_listesi_yoneticisi.panel_olustur(
            services=self._safe_getattr("services", None),
            on_select=self._safe_getattr("select_item", None),
            on_error=_on_error,
        )
        self.function_list.size_hint_y = None
        self.function_list.height = dp(760)
        self.main_column.add_widget(self.function_list)

    def _build_editor(self, editor_yoneticisi) -> None:
        """
        Editör panelini oluşturur.
        """
        self.editor = editor_yoneticisi.panel_olustur(
            services=self._safe_getattr("services", None),
            on_update=self._safe_getattr("update_selected_function", None),
            on_restore=self._safe_getattr("geri_yukle_secili_belge", None),
        )
        self.editor.size_hint_y = None
        self.editor.height = dp(900)
        self.main_column.add_widget(self.editor)

    def _build_bottom_bar(self, durum_cubugu_class) -> None:
        """
        Alt durum çubuğu ve sürüm kartını oluşturur.
        """
        self.bottom_bar = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(4),
            padding=(0, dp(2), 0, 0),
        )

        self.status = durum_cubugu_class(services=self._safe_getattr("services", None))
        self.status.size_hint_y = None
        self.bottom_bar.add_widget(self.status)

        _, version_wrap = self._root_call("_build_version_card")
        self.version_wrap = version_wrap
        if self.version_wrap is not None:
            self.bottom_bar.add_widget(self.version_wrap)

        try:
            self.bottom_bar.height = (
                int(getattr(self.status, "height", 0) or 0)
                + int(getattr(self.version_wrap, "height", 0) or 0)
                + int(dp(4))
            )
        except Exception:
            pass

    def _build_tarama_overlayleri(self, tarama_gostergesi_yoneticisi) -> None:
        """
        Tarama loading ve success overlay katmanlarını oluşturur.
        """
        try:
            self.tarama_loading_overlay = (
                tarama_gostergesi_yoneticisi.loading_overlay_olustur()
            )
            if self.tarama_loading_overlay is not None:
                self.add_widget(self.tarama_loading_overlay)
        except Exception as exc:
            self.tarama_loading_overlay = None
            print(f"[ROOT] Tarama loading overlay oluşturulamadı: {exc}")

        try:
            self.tarama_success_overlay = (
                tarama_gostergesi_yoneticisi.success_overlay_olustur()
            )
            if self.tarama_success_overlay is not None:
                self.add_widget(self.tarama_success_overlay)
        except Exception as exc:
            self.tarama_success_overlay = None
            print(f"[ROOT] Tarama success overlay oluşturulamadı: {exc}")

    # =========================================================
    # MAIN UI BUILD
    # =========================================================
    def _build_ui(self) -> None:
        """
        Root içindeki ana UI ağacını kurar.

        Akış:
        - Lazy resolve ile gerekli sınıfları/yöneticileri yükler
        - Scroll ve ana kolon yapısını oluşturur
        - Üst panelleri ve editörü ekler
        - Alt durum çubuğunu ekler
        - Opsiyonel toast katmanını kurar
        - Tarama overlay katmanlarını ekler
        """
        dosya_secici_class = self._get_dosya_secici_class()
        durum_cubugu_class = self._get_durum_cubugu_class()

        editor_yoneticisi = self._new_instance(
            "app.ui.editor_paketi",
            "EditorYoneticisi",
        )
        tum_dosya_erisim_yoneticisi = self._new_instance(
            "app.ui.tum_dosya_erisim_paketi",
            "TumDosyaErisimYoneticisi",
        )
        fonksiyon_listesi_yoneticisi = self._new_instance(
            "app.ui.fonksiyon_listesi_paketi",
            "FonksiyonListesiYoneticisi",
        )
        tarama_gostergesi_yoneticisi = self._new_instance(
            "app.ui.tarama_gostergesi_paketi",
            "TaramaGostergesiYoneticisi",
        )

        if dosya_secici_class is None:
            raise RuntimeError("DosyaSecici sınıfı yüklenemedi.")
        if durum_cubugu_class is None:
            raise RuntimeError("DurumCubugu sınıfı yüklenemedi.")
        if editor_yoneticisi is None:
            raise RuntimeError("EditorYoneticisi oluşturulamadı.")
        if tum_dosya_erisim_yoneticisi is None:
            raise RuntimeError("TumDosyaErisimYoneticisi oluşturulamadı.")
        if fonksiyon_listesi_yoneticisi is None:
            raise RuntimeError("FonksiyonListesiYoneticisi oluşturulamadı.")
        if tarama_gostergesi_yoneticisi is None:
            raise RuntimeError("TaramaGostergesiYoneticisi oluşturulamadı.")

        self._build_scroll_and_main_column()
        self._build_file_access_panel(tum_dosya_erisim_yoneticisi)
        self._build_dosya_secici(dosya_secici_class)
        self._build_function_list(fonksiyon_listesi_yoneticisi)
        self._build_editor(editor_yoneticisi)

        self.scroll.add_widget(self.main_column)
        self.main_root.add_widget(self.scroll)

        self._build_bottom_bar(durum_cubugu_class)
        self.main_root.add_widget(self.bottom_bar)

        try:
            self._root_call("_setup_optional_toast_layer")
        except Exception:
            pass

        self._build_tarama_overlayleri(tarama_gostergesi_yoneticisi)
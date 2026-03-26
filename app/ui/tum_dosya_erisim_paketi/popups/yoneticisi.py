# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/popups/yoneticisi.py

ROL:
- Tüm dosya erişim paketi popup katmanına tek giriş noktası sağlamak
- Popup modüllerini merkezileştirmek
- Üst katmanın popup dosyalarının iç detaylarını bilmesini engellemek
- Menü popup üzerinden dil seçimi akışına gerekli servis ve callback bilgisini iletmek
- Popup katmanında services bağımlılığını kontrollü biçimde aşağı aktarmak
- Lazy import ve cache ile popup erişim maliyetini azaltmak

MİMARİ:
- Lazy import kullanır
- Popup modüllerine doğrudan değil, bu yönetici üzerinden erişilir
- Üst katman sadece bu yöneticiyi bilir
- Menü popup açılışında servis ve dil callback bağımlılıkları bu katmandan geçirilir
- Basit popup, onay popup, indirme sonuç popup, yedek görüntüleme popup
  ve yedekler popup çağrılarında services parametresi aşağı aktarılabilir
- Hardcoded kullanıcı metni minimumda tutulur ve override edilebilir
- Modül ve sınıf referansları cache içinde tutulur
- Android / AAB / masaüstü çalışma düzeninde aynı erişim mantığını korur

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 7
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import traceback


class TumDosyaErisimPopupsYoneticisi:
    def __init__(self) -> None:
        self._modul_cache: dict[str, object] = {}
        self._sinif_cache: dict[str, object] = {}

    # =========================================================
    # INTERNAL
    # =========================================================
    def cache_temizle(self) -> None:
        """
        Popup yöneticisi içindeki modül ve sınıf cache'lerini temizler.
        """
        try:
            self._modul_cache = {}
        except Exception:
            pass

        try:
            self._sinif_cache = {}
        except Exception:
            pass

    def _debug(self, message: str) -> None:
        try:
            print(f"[TUM_DOSYA_ERISIM_POPUPS] {message}")
        except Exception:
            pass

    def _modul_yukle(self, modul_yolu: str):
        """
        Hedef modülü lazy import + cache ile yükler.
        """
        try:
            cached = self._modul_cache.get(modul_yolu)
            if cached is not None:
                return cached
        except Exception:
            pass

        try:
            modul = __import__(modul_yolu, fromlist=["*"])
            self._modul_cache[modul_yolu] = modul
            return modul
        except Exception:
            self._debug(f"Modül yüklenemedi: {modul_yolu}")
            self._debug(traceback.format_exc())
            return None

    def _modul_attr(self, modul_yolu: str, attr_adi: str):
        """
        Modül içinden callable veya sınıf niteliği döndürür.
        """
        modul = self._modul_yukle(modul_yolu)
        if modul is None:
            return None

        try:
            return getattr(modul, attr_adi, None)
        except Exception:
            self._debug(f"Attribute alınamadı: {modul_yolu}.{attr_adi}")
            self._debug(traceback.format_exc())
            return None

    def _sinif_getir(self, modul_yolu: str, sinif_adi: str):
        """
        Sınıfı lazy import + cache ile döndürür.
        """
        cache_key = f"{modul_yolu}::{sinif_adi}"

        try:
            cached = self._sinif_cache.get(cache_key)
            if cached is not None:
                return cached
        except Exception:
            pass

        sinif = self._modul_attr(modul_yolu, sinif_adi)
        if sinif is None:
            return None

        try:
            self._sinif_cache[cache_key] = sinif
        except Exception:
            pass

        return sinif

    # =========================================================
    # SIMPLE / BASIC
    # =========================================================
    def show_simple_popup(
        self,
        title_text: str,
        body_text: str,
        icon_name: str = "onaylandi.png",
        auto_close_seconds: float | None = 1.8,
        compact: bool = True,
        services=None,
    ):
        fn = self._modul_attr(
            "app.ui.tum_dosya_erisim_paketi.popups.basit_popup",
            "show_simple_popup",
        )
        if not callable(fn):
            return None

        return fn(
            title_text=title_text,
            body_text=body_text,
            icon_name=icon_name,
            auto_close_seconds=auto_close_seconds,
            compact=compact,
            services=services,
        )

    # =========================================================
    # MENU
    # =========================================================
    def open_main_menu(
        self,
        open_backups_popup,
        on_language_changed=None,
        services=None,
    ):
        fn = self._modul_attr(
            "app.ui.tum_dosya_erisim_paketi.popups.menu_popup",
            "open_main_menu",
        )
        if not callable(fn):
            return None

        return fn(
            open_backups_popup=open_backups_popup,
            on_language_changed=on_language_changed,
            services=services,
        )

    # =========================================================
    # CONFIRM
    # =========================================================
    def show_confirm_popup(
        self,
        title_text: str,
        body_text: str,
        on_confirm,
        confirm_icon: str = "delete.png",
        services=None,
    ):
        fn = self._modul_attr(
            "app.ui.tum_dosya_erisim_paketi.popups.onay_popup",
            "show_confirm_popup",
        )
        if not callable(fn):
            return None

        return fn(
            title_text=title_text,
            body_text=body_text,
            on_confirm=on_confirm,
            confirm_icon=confirm_icon,
            services=services,
        )

    # =========================================================
    # DOWNLOAD RESULT
    # =========================================================
    def show_download_result_popup(
        self,
        saved_path,
        selected_by_user: bool = False,
        services=None,
    ):
        fn = self._modul_attr(
            "app.ui.tum_dosya_erisim_paketi.popups.indirme_sonuc_popup",
            "show_download_result_popup",
        )
        if not callable(fn):
            return None

        return fn(
            saved_path=saved_path,
            selected_by_user=selected_by_user,
            services=services,
        )

    # =========================================================
    # DELETE STATUS
    # =========================================================
    def silme_durum_popup_sinifi(self):
        return self._sinif_getir(
            "app.ui.tum_dosya_erisim_paketi.popups.silme_durum_popup",
            "SilmeDurumPopup",
        )

    def silme_durum_popup_olustur(
        self,
        title_text: str = "",
        body_text: str = "",
        success_text: str = "",
        icon_name: str = "onaylandi.png",
        services=None,
    ):
        sinif = self.silme_durum_popup_sinifi()
        if sinif is None:
            return None

        return sinif(
            title_text=title_text,
            body_text=body_text,
            success_text=success_text,
            icon_name=icon_name,
            services=services,
        )

    # =========================================================
    # BACKUP VIEW
    # =========================================================
    def open_backup_view_popup(self, yedek, services=None):
        fn = self._modul_attr(
            "app.ui.tum_dosya_erisim_paketi.popups.yedek_goruntuleme_popup",
            "open_backup_view_popup",
        )
        if not callable(fn):
            return None

        return fn(
            yedek=yedek,
            services=services,
        )

    # =========================================================
    # BACKUPS LIST
    # =========================================================
    def open_backups_popup(self, debug=None, services=None):
        fn = self._modul_attr(
            "app.ui.tum_dosya_erisim_paketi.popups.yedekler_popup",
            "open_backups_popup",
        )
        if not callable(fn):
            return None

        return fn(
            debug=debug,
            services=services,
                    )

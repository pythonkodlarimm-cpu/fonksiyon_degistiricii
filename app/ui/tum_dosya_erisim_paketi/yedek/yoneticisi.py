# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/yedek/yoneticisi.py

ROL:
- Tüm dosya erişim paketi içindeki yedek UI akışlarına tek giriş noktası sağlamak
- Yedek satırı, indirme işlemi ve dosya yolu açma akışını merkezileştirmek
- Üst katmanın alt modül detaylarını bilmesini engellemek
- Lazy import ve cache ile tekrar eden erişim maliyetini azaltmak
- Services akışının popup ve yedek alt katmanlarına kontrollü aktarımına uyum sağlamak

MİMARİ:
- Lazy import kullanır
- UI katmanı bu alt modüllere doğrudan değil, bu yönetici üzerinden erişir
- Yedekle ilgili tekrar kullanılabilir akışlar burada toplanır
- Modül ve fonksiyon referansları cache içinde tutulur
- Android / AAB / masaüstü çalışma düzeninde aynı erişim mantığını korur
- Mevcut public API korunur

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 2
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import traceback


class TumDosyaErisimYedekYoneticisi:
    def __init__(self) -> None:
        self._modul_cache: dict[str, object] = {}
        self._callable_cache: dict[str, object] = {}

    # =========================================================
    # INTERNAL
    # =========================================================
    def cache_temizle(self) -> None:
        """
        Yönetici içindeki modül ve callable cache'lerini temizler.
        """
        try:
            self._modul_cache = {}
        except Exception:
            pass

        try:
            self._callable_cache = {}
        except Exception:
            pass

    def _debug(self, message: str) -> None:
        try:
            print(f"[TUM_DOSYA_ERISIM_YEDEK] {message}")
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

    def _callable_getir(self, modul_yolu: str, ad: str):
        """
        Modül içinden callable attribute döndürür.
        """
        cache_key = f"{modul_yolu}::{ad}"

        try:
            cached = self._callable_cache.get(cache_key)
            if callable(cached):
                return cached
        except Exception:
            pass

        modul = self._modul_yukle(modul_yolu)
        if modul is None:
            return None

        try:
            obj = getattr(modul, ad, None)
            if callable(obj):
                self._callable_cache[cache_key] = obj
                return obj
        except Exception:
            self._debug(f"Callable alınamadı: {modul_yolu}.{ad}")
            self._debug(traceback.format_exc())

        return None

    # =========================================================
    # BACKUP ROW
    # =========================================================
    def yedek_satiri_olustur(self, yedek, on_view, on_download, on_delete):
        fn = self._callable_getir(
            "app.ui.tum_dosya_erisim_paketi.yedek.yedek_satiri",
            "build_backup_row",
        )
        if not callable(fn):
            return None

        return fn(
            yedek=yedek,
            on_view=on_view,
            on_download=on_download,
            on_delete=on_delete,
        )

    # =========================================================
    # DOWNLOAD ACTION
    # =========================================================
    def yedek_indirme_islemi_baslat(
        self,
        debug,
        yedek,
        hedef_klasor=None,
    ):
        fn = self._callable_getir(
            "app.ui.tum_dosya_erisim_paketi.yedek.yedek_indirme_islemi",
            "backup_download_action",
        )
        if not callable(fn):
            raise RuntimeError("backup_download_action callable bulunamadı.")

        return fn(
            debug=debug,
            yedek=yedek,
            hedef_klasor=hedef_klasor,
        )

    # =========================================================
    # FILE MANAGER OPEN
    # =========================================================
    def dosya_yolu_ac(self, path_value, debug=None) -> bool:
        fn = self._callable_getir(
            "app.ui.tum_dosya_erisim_paketi.yedek.dosya_yolu_acici",
            "open_path_in_file_manager",
        )
        if not callable(fn):
            return False

        try:
            return bool(
                fn(
                    path_value=path_value,
                    debug=debug,
                )
            )
        except Exception:
            self._debug("Dosya yolu açma işlemi başarısız.")
            self._debug(traceback.format_exc())
            return False

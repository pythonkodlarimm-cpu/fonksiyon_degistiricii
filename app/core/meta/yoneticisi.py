# -*- coding: utf-8 -*-
"""
DOSYA: app/core/meta/yoneticisi.py

ROL:
- Uygulama metadata katmanına tek giriş noktası sağlar
- Sabitler modülünü dış katmandan tamamen izole eder
- Uygulama adı, paket adı, sürüm ve açıklama bilgilerini merkezileştirir
- Android sürüm bilgilerini tek ve güvenli bir noktadan sunar

MİMARİ:
- Lazy import kullanır (ilk kullanımda yüklenir)
- Modül referansı cache içinde tutulur (performans optimizasyonu)
- Üst katman sabitler.py dosyasını doğrudan bilmez
- Core, UI ve uygulama başlangıcı bu yöneticiyi kullanmalıdır
- Deterministic davranır, runtime yan etkisi yoktur

BAĞIMLILIKLAR:
- app/core/meta/sabitler.py

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- APK/AAB build süreçleri ile uyumludur

SURUM: 3
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations

from types import ModuleType


class MetaYoneticisi:
    """
    Uygulama metadata erişim yöneticisi.
    """

    def __init__(self) -> None:
        self._modul_cache: ModuleType | None = None

    # =========================================================
    # INTERNAL
    # =========================================================
    def _modul(self) -> ModuleType:
        """
        Sabitler modülünü lazy load eder ve cache'ler.
        """
        if self._modul_cache is None:
            from app.core.meta import sabitler
            self._modul_cache = sabitler

        return self._modul_cache

    # =========================================================
    # TEMEL META
    # =========================================================
    def uygulama_adi(self) -> str:
        return self._modul().UYGULAMA_ADI

    def paket_adi(self) -> str:
        return self._modul().PAKET_ADI

    def tarih(self) -> str:
        return self._modul().TARIH

    def imza(self) -> str:
        return self._modul().IMZA

    def aciklama(self) -> str:
        return self._modul().ACIKLAMA

    # =========================================================
    # SURUM
    # =========================================================
    def surum_adi(self) -> str:
        return self._modul().SURUM_ADI

    def surum_kodu(self) -> int:
        return self._modul().SURUM_KODU

    def build_numarasi(self) -> int:
        return self._modul().BUILD_NUMARASI

    def tam_surum(self) -> str:
        return self._modul().get_tam_surum()

    # =========================================================
    # ANDROID
    # =========================================================
    def apk_surum_adi(self) -> str:
        return self._modul().get_apk_surum_adi()

    def apk_surum_kodu(self) -> int:
        return self._modul().get_apk_surum_kodu()

    # =========================================================
    # ETIKET / META
    # =========================================================
    def uygulama_etiketi(self) -> str:
        return self._modul().get_uygulama_etiketi()

    def meta_bilgisi(self) -> dict[str, str | int]:
        return self._modul().get_meta_bilgisi()
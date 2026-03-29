# -*- coding: utf-8 -*-
"""
DOSYA: app/core/meta/yoneticisi.py

ROL:
- Uygulama metadata katmanına tek giriş noktası sağlar
- Sabitler modülünü dış katmandan tamamen izole eder
- Uygulama adı, paket adı, sürüm ve açıklama bilgilerini merkezileştirir
- Android sürüm bilgilerini tek ve güvenli bir noktadan sunar
- APK içinden okunan gerçek sürüm bilgilerini facade üzerinden erişilebilir kılar

MİMARİ:
- Lazy import kullanır (ilk kullanımda yüklenir)
- Modül referansı cache içinde tutulur
- Üst katman sabitler.py dosyasını doğrudan bilmez
- Core, UI ve uygulama başlangıcı bu yöneticiyi kullanmalıdır
- Deterministic davranır
- Runtime yan etkisi yoktur
- Type güvenliği nettir
- Geriye uyumluluk katmanı içermez

BAĞIMLILIKLAR:
- app/core/meta/sabitler.py

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- APK/AAB build süreçleri ile uyumludur

SURUM: 4
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from types import ModuleType


class MetaYoneticisi:
    """
    Uygulama metadata erişim yöneticisi.
    """

    __slots__ = ("_modul_cache",)

    def __init__(self) -> None:
        self._modul_cache: ModuleType | None = None

    # =========================================================
    # INTERNAL
    # =========================================================
    def _modul(self) -> ModuleType:
        """
        Sabitler modülünü lazy load eder ve cache'ler.
        """
        modul = self._modul_cache
        if modul is None:
            from app.core.meta import sabitler

            modul = sabitler
            self._modul_cache = modul

        return modul

    # =========================================================
    # TEMEL META
    # =========================================================
    def uygulama_adi(self) -> str:
        return str(self._modul().UYGULAMA_ADI)

    def paket_adi(self) -> str:
        return str(self._modul().PAKET_ADI)

    def tarih(self) -> str:
        return str(self._modul().TARIH)

    def imza(self) -> str:
        return str(self._modul().IMZA)

    def aciklama(self) -> str:
        return str(self._modul().ACIKLAMA)

    # =========================================================
    # SURUM
    # =========================================================
    def surum_adi(self) -> str:
        return str(self._modul().SURUM_ADI)

    def surum_kodu(self) -> int:
        return int(self._modul().SURUM_KODU)

    def build_numarasi(self) -> int:
        return int(self._modul().BUILD_NUMARASI)

    def tam_surum(self) -> str:
        return str(self._modul().get_tam_surum())

    # =========================================================
    # APK / ANDROID SURUM
    # =========================================================
    def apk_surum_adi(self) -> str:
        """
        Kurulu APK içinden okunan sürüm adını döndürür.
        """
        return str(self._modul().get_apk_surum_adi())

    def apk_surum_kodu(self) -> int:
        """
        Kurulu APK içinden okunan sürüm kodunu döndürür.
        """
        return int(self._modul().get_apk_surum_kodu())

    def apk_tam_surum(self) -> str:
        """
        APK sürüm adı ve kodunu tek metin olarak döndürür.
        """
        modul = self._modul()

        if hasattr(modul, "get_apk_tam_surum"):
            return str(modul.get_apk_tam_surum())

        surum_adi = str(modul.get_apk_surum_adi())
        surum_kodu = int(modul.get_apk_surum_kodu())
        return f"{surum_adi} ({surum_kodu})"

    def apk_surum_bilgisi(self) -> dict[str, str | int]:
        """
        APK sürüm bilgisini normalize edilmiş sözlük olarak döndürür.
        """
        modul = self._modul()

        if hasattr(modul, "get_apk_surum_bilgisi"):
            bilgi = modul.get_apk_surum_bilgisi()
            return {
                "version_name": str(bilgi.get("version_name", "")),
                "version_code": int(bilgi.get("version_code", 0)),
                "full": str(bilgi.get("full", "")),
            }

        version_name = str(modul.get_apk_surum_adi())
        version_code = int(modul.get_apk_surum_kodu())
        return {
            "version_name": version_name,
            "version_code": version_code,
            "full": f"{version_name} ({version_code})",
        }

    # =========================================================
    # ETIKET / META
    # =========================================================
    def uygulama_etiketi(self) -> str:
        return str(self._modul().get_uygulama_etiketi())

    def meta_bilgisi(self) -> dict[str, str | int]:
        return dict(self._modul().get_meta_bilgisi())

    def meta_ve_apk_bilgisi(self) -> dict[str, str | int]:
        """
        Statik meta ve kurulu APK sürüm bilgisini tek yapıda döndürür.
        """
        meta = dict(self.meta_bilgisi())
        apk = self.apk_surum_bilgisi()

        meta["apk_version_name"] = apk["version_name"]
        meta["apk_version_code"] = apk["version_code"]
        meta["apk_full_version"] = apk["full"]

        return meta

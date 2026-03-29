# -*- coding: utf-8 -*-
"""
DOSYA: app/services/apk_surumu_servisi.py

ROL:
- APK sürüm bilgisini servis katmanından sunar
- Core meta katmanından gelen bilgiyi normalize eder
- UI katmanına sade ve güvenli veri sağlar
- Android / non-android farkını soyutlar
- Pydroid3 / geliştirme ortamı ile gerçek APK ortamını ayırt eder
- UI için gösterilecek doğru sürüm metnini üretir

MİMARİ:
- Core.meta() üzerinden veri çeker
- UI bu servisi kullanır (core'a direkt gitmez)
- Fail-soft davranır (asla crash vermez)
- Deterministic çalışır
- Veri formatı standarttır
- Geriye uyumluluk katmanı içermez
- Sıfır belirsizlik hedeflenir

SURUM: 2
TARIH: 2026-03-29
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

from kivy.utils import platform


class ApkSurumuServisi:
    """
    APK sürüm bilgisi servis katmanı.
    """

    __slots__ = ("_core",)

    def __init__(self, core) -> None:
        self._core = core

    # =========================================================
    # INTERNAL
    # =========================================================
    def _meta(self):
        """
        Core meta yöneticisini getirir.
        """
        try:
            return self._core.meta()
        except Exception:
            return None

    @staticmethod
    def _safe_str(value: Any, default: str = "") -> str:
        try:
            text = str(value)
            return text if text is not None else default
        except Exception:
            return default

    @staticmethod
    def _safe_int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except Exception:
            return default

    # =========================================================
    # ORTAM TESPITI
    # =========================================================
    def apk_ortaminda_mi(self) -> bool:
        """
        Uygulamanın gerçek paketlenmiş APK/AAB ortamında çalışıp çalışmadığını döndürür.

        Not:
        - Pydroid3 geliştirme ortamı APK ortamı sayılmaz.
        - Android dışı tüm platformlar False döner.
        """
        if platform != "android":
            return False

        try:
            from jnius import autoclass

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity
            if activity is None:
                return False

            package_name = self._safe_str(
                activity.getPackageName(),
                "",
            ).strip().lower()

            if not package_name:
                return False

            if "ru.iiec.pydroid3" in package_name:
                return False

            return True
        except Exception:
            return False

    # =========================================================
    # GELISTIRME SURUMU
    # =========================================================
    def gelistirme_surum_adi(self) -> str:
        """
        Geliştirme ortamında gösterilecek statik sürüm adını döndürür.
        """
        try:
            meta = self._meta()
            if meta is None:
                return "0.0.0"
            return self._safe_str(meta.surum_adi(), "0.0.0")
        except Exception:
            return "0.0.0"

    def gelistirme_surum_kodu(self) -> int:
        """
        Geliştirme ortamında gösterilecek statik sürüm kodunu döndürür.
        """
        try:
            meta = self._meta()
            if meta is None:
                return 0
            return self._safe_int(meta.surum_kodu(), 0)
        except Exception:
            return 0

    def gelistirme_tam_surum(self) -> str:
        """
        Geliştirme ortamında gösterilecek tam sürümü döndürür.
        """
        try:
            meta = self._meta()
            if meta is None:
                return "0.0.0 (0)"
            return self._safe_str(meta.tam_surum(), "0.0.0 (0)")
        except Exception:
            return "0.0.0 (0)"

    # =========================================================
    # APK SURUM
    # =========================================================
    def apk_surum_adi(self) -> str:
        """
        APK versionName döndürür.
        """
        try:
            meta = self._meta()
            if meta is None:
                return "0.0.0"
            return self._safe_str(meta.apk_surum_adi(), "0.0.0")
        except Exception:
            return "0.0.0"

    def apk_surum_kodu(self) -> int:
        """
        APK versionCode döndürür.
        """
        try:
            meta = self._meta()
            if meta is None:
                return 0
            return self._safe_int(meta.apk_surum_kodu(), 0)
        except Exception:
            return 0

    def apk_tam_surum(self) -> str:
        """
        APK tam sürüm (örn: 0.1.25 (25))
        """
        try:
            meta = self._meta()
            if meta is None:
                return "0.0.0 (0)"
            return self._safe_str(meta.apk_tam_surum(), "0.0.0 (0)")
        except Exception:
            return "0.0.0 (0)"

    def apk_surum_bilgisi(self) -> dict[str, str | int]:
        """
        Normalize edilmiş APK sürüm bilgisi döndürür.
        """
        try:
            meta = self._meta()
            if meta is None:
                return {
                    "version_name": "0.0.0",
                    "version_code": 0,
                    "full": "0.0.0 (0)",
                }

            veri = meta.apk_surum_bilgisi()

            return {
                "version_name": self._safe_str(
                    veri.get("version_name"),
                    "0.0.0",
                ),
                "version_code": self._safe_int(
                    veri.get("version_code"),
                    0,
                ),
                "full": self._safe_str(
                    veri.get("full"),
                    "0.0.0 (0)",
                ),
            }

        except Exception:
            return {
                "version_name": "0.0.0",
                "version_code": 0,
                "full": "0.0.0 (0)",
            }

    # =========================================================
    # GOSTERILECEK SURUM
    # =========================================================
    def goruntulenecek_surum_adi(self) -> str:
        """
        UI üzerinde gösterilecek doğru sürüm adını döndürür.

        Kural:
        - Gerçek APK ortamında: APK sürüm adı
        - Geliştirme ortamında: statik geliştirme sürüm adı
        """
        if self.apk_ortaminda_mi():
            return self.apk_surum_adi()

        return self.gelistirme_surum_adi()

    def goruntulenecek_surum_kodu(self) -> int:
        """
        UI üzerinde gösterilecek doğru sürüm kodunu döndürür.
        """
        if self.apk_ortaminda_mi():
            return self.apk_surum_kodu()

        return self.gelistirme_surum_kodu()

    def goruntulenecek_tam_surum(self) -> str:
        """
        UI üzerinde gösterilecek doğru tam sürüm metnini döndürür.
        """
        if self.apk_ortaminda_mi():
            return self.apk_tam_surum()

        return self.gelistirme_tam_surum()

    def goruntulenecek_surum_bilgisi(self) -> dict[str, str | int]:
        """
        UI üzerinde gösterilecek normalize sürüm bilgisini döndürür.
        """
        if self.apk_ortaminda_mi():
            return self.apk_surum_bilgisi()

        return {
            "version_name": self.gelistirme_surum_adi(),
            "version_code": self.gelistirme_surum_kodu(),
            "full": self.gelistirme_tam_surum(),
        }

    # =========================================================
    # UI HELPERS
    # =========================================================
    def surum_etiketi(self, label: str = "Sürüm") -> str:
        """
        UI için hazır metin döndürür.

        Örn:
        - APK ortamı: "Sürüm: 0.1.25"
        - Geliştirme: "Sürüm: 0.1.25 [DEV]"
        """
        try:
            version = self.goruntulenecek_surum_adi()

            if self.apk_ortaminda_mi():
                return f"{label}: {version}"

            return f"{label}: {version} [DEV]"
        except Exception:
            return f"{label}: 0.0.0"

    def goruntulenecek_surum_metni(self, label: str = "Sürüm") -> str:
        """
        UI üzerinde doğrudan gösterilecek sürüm metnini döndürür.
        """
        return self.surum_etiketi(label=label)
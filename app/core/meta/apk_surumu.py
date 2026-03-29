# -*- coding: utf-8 -*-
"""
DOSYA: app/core/meta/apk_surumu.py

ROL:
- Android üzerinde kurulu uygulamanın gerçek APK/AAB sürüm bilgisini okur
- versionName ve versionCode bilgisini güvenli biçimde döndürür
- Android dışı ortamlarda güvenli fallback sağlar
- Meta katmanı ile uyumlu normalize çıktı üretir

MİMARİ:
- Android'de PackageManager kullanır
- Fail-soft davranır
- Deterministik fallback döndürür
- UI ve service katmanına sade veri sağlar
- Sabitler/meta yöneticisi ile uyumlu anahtar seti kullanır

API UYUMLULUK:
- Android API 35 uyumludur
- AndroidX uyumludur
- Pydroid3 / masaüstü / test ortamlarında güvenli fallback verir

SURUM: 2
TARIH: 2026-03-29
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

from kivy.utils import platform


# =========================================================
# INTERNAL
# =========================================================
def _safe_str(value: Any, default: str = "") -> str:
    """
    Değeri güvenli biçimde str'e çevirir.
    """
    try:
        metin = str(value)
        return metin if metin else default
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    """
    Değeri güvenli biçimde int'e çevirir.
    """
    try:
        return int(value)
    except Exception:
        return default


def _fallback_surumu() -> dict[str, str | int]:
    """
    Android dışı veya hata durumundaki güvenli fallback.
    """
    if platform == "android":
        version_name = "0.0.0"
    else:
        version_name = "0.0.0 [DEV]"

    version_code = 0

    return {
        "version_name": version_name,
        "version_code": version_code,
        "full": f"{version_name} ({version_code})",
        "label": f"FY. v{version_name}",
    }


# =========================================================
# PUBLIC API
# =========================================================
def apk_surumu_getir() -> dict[str, str | int]:
    """
    Kurulu uygulamanın sürüm bilgisini döndürür.

    Dönüş:
    {
        "version_name": str,
        "version_code": int,
        "full": str,
        "label": str,
    }
    """
    if platform != "android":
        return _fallback_surumu()

    try:
        from jnius import autoclass

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = PythonActivity.mActivity

        if activity is None:
            return _fallback_surumu()

        package_name = activity.getPackageName()
        package_manager = activity.getPackageManager()
        package_info = package_manager.getPackageInfo(package_name, 0)

        version_name = _safe_str(getattr(package_info, "versionName", None), "0.0.0")

        version_code = 0

        try:
            version_code = _safe_int(package_info.getLongVersionCode(), 0)
        except Exception:
            version_code = _safe_int(getattr(package_info, "versionCode", 0), 0)

        return {
            "version_name": version_name,
            "version_code": version_code,
            "full": f"{version_name} ({version_code})",
            "label": f"FY. v{version_name}",
        }

    except Exception:
        return _fallback_surumu()

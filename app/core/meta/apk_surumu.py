# -*- coding: utf-8 -*-
"""
DOSYA: app/core/meta/apk_surumu.py

ROL:
- Android üzerinde kurulu APK sürüm bilgisini okur
- versionName ve versionCode bilgisini güvenli biçimde döndürür
- Android dışı ortamlarda güvenli fallback sağlar

SURUM: 1
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from kivy.utils import platform


def apk_surumu_getir() -> dict[str, str | int]:
    """
    Kurulu uygulamanın sürüm bilgisini döndürür.

    Dönüş:
    {
        "version_name": str,
        "version_code": int,
        "full": str,
    }
    """
    if platform != "android":
        return {
            "version_name": "0.0.0",
            "version_code": 0,
            "full": "0.0.0 (0)",
        }

    try:
        from jnius import autoclass

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = PythonActivity.mActivity

        if activity is None:
            raise RuntimeError("Android activity yok.")

        package_name = activity.getPackageName()
        package_manager = activity.getPackageManager()
        package_info = package_manager.getPackageInfo(package_name, 0)

        try:
            version_name = str(package_info.versionName or "0.0.0")
        except Exception:
            version_name = "0.0.0"

        try:
            version_code = int(package_info.versionCode)
        except Exception:
            version_code = 0

        return {
            "version_name": version_name,
            "version_code": version_code,
            "full": f"{version_name} ({version_code})",
        }

    except Exception:
        return {
            "version_name": "0.0.0",
            "version_code": 0,
            "full": "0.0.0 (0)",
        }
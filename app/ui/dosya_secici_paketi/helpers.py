# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/helpers.py

ROL:
- Dosya seçici için varsayılan başlangıç klasörünü belirlemek

API 34 UYUMLULUK NOTU:
- Android 13/14 tarafında dış depolama erişimi daha kısıtlı olabilir
- Bu yüzden mümkünse önce uygulamanın erişebildiği güvenli klasörler tercih edilir
- Dış depolama klasörleri fallback olarak korunur
"""

from __future__ import annotations

from pathlib import Path

from kivy.utils import platform


def varsayilan_baslangic_klasoru() -> Path:
    """
    Dosya seçici için varsayılan başlangıç klasörünü döndürür.

    Öncelik:
    - Android'de mümkünse uygulamanın erişebildiği güvenli alanlar
    - sonra yaygın dış depolama yolları
    - en son home / cwd
    """
    adaylar: list[Path] = []

    if platform == "android":
        try:
            from app.services.android_uri_servisi import get_app_files_dir

            app_files = get_app_files_dir()
            if app_files.exists() and app_files.is_dir():
                adaylar.append(app_files)
        except Exception:
            pass

        adaylar.extend(
            [
                Path("/storage/emulated/0"),
                Path("/sdcard"),
            ]
        )

    adaylar.extend(
        [
            Path.home(),
            Path.cwd(),
        ]
    )

    for aday in adaylar:
        try:
            if aday.exists() and aday.is_dir():
                return aday.resolve()
        except Exception:
            pass

    try:
        return Path.cwd().resolve()
    except Exception:
        return Path(".")
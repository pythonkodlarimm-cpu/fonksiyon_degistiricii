# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/icon_yardimci.py
ROL:
- UI katmanında ikon dosya yollarını merkezi olarak üretir
- Proje farklı yerden çalıştırılsa da doğru assets klasörünü bulmaya çalışır
- Hatalı yazılmış 'assest' klasörü için de fallback içerir
"""

from __future__ import annotations

from pathlib import Path


def ui_dir() -> Path:
    """
    Bu dosyanın bulunduğu ui klasörünü döndürür.
    """
    return Path(__file__).resolve().parent


def app_dir() -> Path:
    """
    ui klasörünün bir üstündeki app klasörünü döndürür.
    """
    return ui_dir().parent


def project_dir() -> Path:
    """
    app klasörünün bir üstündeki proje kökünü döndürür.
    """
    return app_dir().parent


def assets_icons_dir() -> Path:
    """
    Kanonik ikon klasörü.
    """
    return app_dir() / "assets" / "icons"


def icon_path(icon_name: str) -> str:
    """
    Verilen ikon adı için dosya yolunu döndürür.
    Bulunamazsa boş string döner.

    Arama sırası:
    1) app/assets/icons
    2) app/assest/icons   (eski/yanlış yazım fallback)
    3) proje_koku/app/assets/icons
    4) proje_koku/app/assest/icons
    """
    ad = str(icon_name or "").strip()
    if not ad:
        return ""

    adaylar = [
        app_dir() / "assets" / "icons" / ad,
        app_dir() / "assest" / "icons" / ad,
        project_dir() / "app" / "assets" / "icons" / ad,
        project_dir() / "app" / "assest" / "icons" / ad,
    ]

    for yol in adaylar:
        try:
            if yol.is_file():
                return str(yol)
        except Exception:
            pass

    return ""
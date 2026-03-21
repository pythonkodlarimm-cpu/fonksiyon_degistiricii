# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/icon_yardimci.py
ROL:
- UI katmanında ikon dosya yollarını merkezi olarak üretir
- Proje farklı yerden çalıştırılsa da doğru assets klasörünü bulmaya çalışır
- Hatalı yazılmış 'assest' klasörü için de fallback içerir
- Android / APK içinde olabildiğince güvenli yol çözümü yapar

NOT:
- Bu modül yalnızca dosya yolu üretir.
- Build aşamasında ikonların APK içine gerçekten dahil edilmesi gerekir.
"""

from __future__ import annotations

from pathlib import Path


def _safe_resolve(path: Path) -> Path:
    """
    Android / farklı çalışma ortamlarında resolve() patlarsa
    ham absolute path benzeri karşılığı döndür.
    """
    try:
        return path.resolve()
    except Exception:
        try:
            return path.absolute()
        except Exception:
            return path


def _normalize_icon_name(icon_name: str) -> str:
    """
    İkon adını güvenli hale getirir.
    Sadece relatif dosya adı / alt yol mantığında kullanılır.
    """
    ad = str(icon_name or "").strip()
    if not ad:
        return ""

    ad = ad.replace("\\", "/")

    while ad.startswith("/"):
        ad = ad[1:]

    return ad


def ui_dir() -> Path:
    """
    Bu dosyanın bulunduğu ui klasörünü döndürür.
    """
    return _safe_resolve(Path(__file__).parent)


def app_dir() -> Path:
    """
    ui klasörünün bir üstündeki app klasörünü döndürür.
    """
    return _safe_resolve(ui_dir().parent)


def project_dir() -> Path:
    """
    app klasörünün bir üstündeki proje kökünü döndürür.
    """
    return _safe_resolve(app_dir().parent)


def assets_icons_dir() -> Path:
    """
    Kanonik ikon klasörü.
    """
    return _safe_resolve(app_dir() / "assets" / "icons")


def _icon_search_roots() -> list[Path]:
    """
    İkon aramak için kullanılacak kök klasörler.

    Arama mantığı:
    1) app/assets/icons
    2) app/assest/icons
    3) proje_koku/app/assets/icons
    4) proje_koku/app/assest/icons
    5) proje_koku/assets/icons
    6) proje_koku/assest/icons
    """
    roots = [
        app_dir() / "assets" / "icons",
        app_dir() / "assest" / "icons",
        project_dir() / "app" / "assets" / "icons",
        project_dir() / "app" / "assest" / "icons",
        project_dir() / "assets" / "icons",
        project_dir() / "assest" / "icons",
    ]

    out = []
    gorulen = set()

    for root in roots:
        try:
            temiz = _safe_resolve(root)
            key = str(temiz)
            if key not in gorulen:
                gorulen.add(key)
                out.append(temiz)
        except Exception:
            pass

    return out


def icon_path(icon_name: str) -> str:
    """
    Verilen ikon adı için dosya yolunu döndürür.
    Bulunamazsa boş string döner.

    Destek:
    - app/assets/icons
    - app/assest/icons
    - proje_koku/app/assets/icons
    - proje_koku/app/assest/icons
    - proje_koku/assets/icons
    - proje_koku/assest/icons
    """
    ad = _normalize_icon_name(icon_name)
    if not ad:
        return ""

    for kok in _icon_search_roots():
        try:
            yol = kok / ad
            if yol.is_file():
                return str(yol)
        except Exception:
            pass

    return ""
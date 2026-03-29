# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ortak/ikonlar.py

ROL:
- Uygulamadaki icon dosyalarının güvenli çözümlemesini sağlar
- Mevcut icon toolbar yapısına uyumlu çalışır
- Eksik icon durumunda güvenli fallback döndürür

MİMARİ:
- Tek kaynaklı icon çözümleme
- app/assets/icons klasörünü hedef alır
- Deterministik davranır
- Geriye uyumluluk katmanı içermez

SURUM: 2
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final


# app/ui/ortak/ikonlar.py -> app/
_APP_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
_ICON_ROOT: Final[Path] = _APP_ROOT / "assets" / "icons"


def ikon_kok_dizini() -> Path:
    """
    Icon kök dizinini döndürür.
    """
    return _ICON_ROOT


def ikon_yolu(dosya_adi: str, fallback: str = "") -> str:
    """
    İstenen icon dosyasının tam yolunu döndürür.
    """
    raw = str(dosya_adi or "").strip()
    if not raw:
        return _fallback_yolu(fallback)

    path_obj = _ICON_ROOT / raw
    if path_obj.exists() and path_obj.is_file():
        return str(path_obj)

    return _fallback_yolu(fallback)


def toolbar_ikonu(dosya_adi: str) -> str:
    """
    Toolbar icon seti için net çözümleme fonksiyonu.
    """
    return ikon_yolu(dosya_adi)


def icon_mevcut_mu(dosya_adi: str) -> bool:
    """
    Icon dosyası mevcut mu?
    """
    raw = str(dosya_adi or "").strip()
    if not raw:
        return False

    path_obj = _ICON_ROOT / raw
    return path_obj.exists() and path_obj.is_file()


def _fallback_yolu(fallback: str) -> str:
    raw = str(fallback or "").strip()
    if not raw:
        return ""

    fallback_path = Path(raw)
    if fallback_path.exists() and fallback_path.is_file():
        return str(fallback_path.resolve())

    return ""
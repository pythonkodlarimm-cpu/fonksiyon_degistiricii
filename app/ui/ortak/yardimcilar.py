# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ortak/yardimcilar.py

ROL:
- UI katmanında ortak küçük yardımcı fonksiyonları sağlar

SURUM: 1
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations


def guvenli_yazi(value) -> str:
    """
    UI'de gösterilecek metni güvenli string'e çevirir.
    """
    try:
        return str(value if value is not None else "")
    except Exception:
        return ""


def kisalt_yol(path: str, max_len: int = 56) -> str:
    """
    Uzun dosya yolunu UI için kısaltır.
    """
    raw = guvenli_yazi(path).strip()

    if len(raw) <= max_len:
        return raw

    keep = max(10, max_len // 2 - 2)
    return f"{raw[:keep]}...{raw[-keep:]}"
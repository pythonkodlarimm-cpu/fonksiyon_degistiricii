# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/gelistirici_mod/yardimci.py
"""

from __future__ import annotations

from pathlib import Path


def dev_mode_aktif_mi() -> bool:
    try:
        from app.config import DEV_MODE
    except Exception:
        return False

    if isinstance(DEV_MODE, bool):
        return DEV_MODE

    return str(DEV_MODE or "").strip().lower() in (
        "1",
        "true",
        "evet",
        "on",
        "aktif",
    )


def test_yolu_gecerli_mi(path: str) -> bool:
    temiz = str(path or "").strip()
    if not temiz:
        return False

    try:
        yol = Path(temiz)
        return yol.exists() and yol.is_file()
    except Exception:
        return False


def test_dosya_adi(path: str) -> str:
    try:
        return Path(str(path or "").strip()).name
    except Exception:
        return ""


def test_mime_type_bul(path: str) -> str:
    temiz = str(path or "").strip().lower()
    if temiz.endswith(".py"):
        return "text/x-python"
    return ""
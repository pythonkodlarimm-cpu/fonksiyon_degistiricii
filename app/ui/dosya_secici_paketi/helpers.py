# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/helpers.py

ROL:
- Ortak küçük yardımcı fonksiyonlar
"""

from __future__ import annotations

from pathlib import Path

from kivy.utils import platform


def is_android_platform() -> bool:
    return platform == "android"


def debug_log(prefix: str, message: str) -> None:
    try:
        print(f"[{prefix}] {message}")
    except Exception:
        pass


def varsayilan_baslangic_klasoru() -> Path:
    adaylar = [
        Path.home(),
        Path.cwd(),
    ]

    for aday in adaylar:
        try:
            if aday.exists() and aday.is_dir():
                return aday.resolve()
        except Exception:
            pass

    return Path.cwd().resolve()
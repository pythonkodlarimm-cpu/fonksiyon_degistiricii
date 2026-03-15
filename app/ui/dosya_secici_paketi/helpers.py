# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def varsayilan_baslangic_klasoru() -> Path:
    adaylar = [
        Path("/storage/emulated/0"),
        Path("/sdcard"),
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
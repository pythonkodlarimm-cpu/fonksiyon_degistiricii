# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_geri_yukleme/__init__.py
"""

from __future__ import annotations

from typing import Any

__all__ = ["RootGeriYuklemeAkisiYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "RootGeriYuklemeAkisiYoneticisi":
        from app.ui.root_paketi.akisi_geri_yukleme.yoneticisi import (
            RootGeriYuklemeAkisiYoneticisi,
        )
        return RootGeriYuklemeAkisiYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

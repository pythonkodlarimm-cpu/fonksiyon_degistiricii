# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_guncelleme/__init__.py
"""

from __future__ import annotations

from typing import Any

__all__ = ["RootGuncellemeAkisiYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "RootGuncellemeAkisiYoneticisi":
        from app.ui.root_paketi.akisi_guncelleme.yoneticisi import (
            RootGuncellemeAkisiYoneticisi,
        )
        return RootGuncellemeAkisiYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

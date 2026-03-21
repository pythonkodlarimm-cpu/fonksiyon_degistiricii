# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_dosya/__init__.py
"""

from __future__ import annotations

from typing import Any

__all__ = ["RootDosyaAkisiYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "RootDosyaAkisiYoneticisi":
        from app.ui.root_paketi.akisi_dosya.yoneticisi import RootDosyaAkisiYoneticisi
        return RootDosyaAkisiYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_secim/__init__.py
"""

from __future__ import annotations

from typing import Any

__all__ = ["RootSecimAkisiYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "RootSecimAkisiYoneticisi":
        from app.ui.root_paketi.akisi_secim.yoneticisi import RootSecimAkisiYoneticisi
        return RootSecimAkisiYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

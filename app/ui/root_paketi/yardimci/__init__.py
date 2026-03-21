# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/yardimci/__init__.py
"""

from __future__ import annotations

from typing import Any

__all__ = ["RootYardimciYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "RootYardimciYoneticisi":
        from app.ui.root_paketi.yardimci.yoneticisi import RootYardimciYoneticisi
        return RootYardimciYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

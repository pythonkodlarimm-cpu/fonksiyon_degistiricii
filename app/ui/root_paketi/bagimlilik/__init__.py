# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/bagimlilik/__init__.py
"""

from __future__ import annotations

from typing import Any

__all__ = ["RootBagimlilikYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "RootBagimlilikYoneticisi":
        from app.ui.root_paketi.bagimlilik.yoneticisi import RootBagimlilikYoneticisi
        return RootBagimlilikYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/durum/__init__.py
"""

from __future__ import annotations

from typing import Any

__all__ = ["RootDurumYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "RootDurumYoneticisi":
        from app.ui.root_paketi.durum.yoneticisi import RootDurumYoneticisi
        return RootDurumYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

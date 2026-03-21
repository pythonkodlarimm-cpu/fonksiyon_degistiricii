# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/__init__.py
"""

from __future__ import annotations

from typing import Any

__all__ = ["RootWidgetYoneticisi", "RootWidget"]


def __getattr__(name: str) -> Any:
    if name == "RootWidgetYoneticisi":
        from app.ui.root_paketi.root.yoneticisi import RootWidgetYoneticisi
        return RootWidgetYoneticisi

    if name == "RootWidget":
        from app.ui.root_paketi.root.root import RootWidget
        return RootWidget

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/__init__.py

ROL:
- root_paketi için dışa açık API sağlar
- RootPaketiYoneticisi ve RootWidget erişimini tek noktadan verir
- Lazy import ile bağımlılıkları geciktirir

SURUM: 1
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "RootPaketiYoneticisi",
    "RootWidget",
]


def __getattr__(name: str) -> Any:
    if name == "RootPaketiYoneticisi":
        from app.ui.root_paketi.yoneticisi import RootPaketiYoneticisi
        return RootPaketiYoneticisi

    if name == "RootWidget":
        from app.ui.root_paketi.root.root import RootWidget
        return RootWidget

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

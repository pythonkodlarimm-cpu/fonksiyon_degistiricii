# -*- coding: utf-8 -*-
"""
DOSYA: app/services/guncelleme/__init__.py

ROL:
- Güncelleme yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder
- Güncelleme katmanını dış dünyaya kontrollü şekilde açar

SURUM: 1
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["GuncellemeYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "GuncellemeYoneticisi":
        from app.services.guncelleme.yoneticisi import GuncellemeYoneticisi
        return GuncellemeYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

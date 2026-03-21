# -*- coding: utf-8 -*-
"""
DOSYA: app/services/android/__init__.py

ROL:
- Android klasörü yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini azaltır

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["AndroidYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "AndroidYoneticisi":
        from app.services.android.yoneticisi import AndroidYoneticisi
        return AndroidYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

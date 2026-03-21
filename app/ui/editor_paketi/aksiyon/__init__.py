# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/aksiyon/__init__.py

ROL:
- Aksiyon yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["AksiyonYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "AksiyonYoneticisi":
        from app.ui.editor_paketi.aksiyon.yoneticisi import AksiyonYoneticisi
        return AksiyonYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

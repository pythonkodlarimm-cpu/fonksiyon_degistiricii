# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/pickers/__init__.py

ROL:
- Picker yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["PickerYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "PickerYoneticisi":
        from app.ui.dosya_secici_paketi.pickers.yoneticisi import PickerYoneticisi
        return PickerYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

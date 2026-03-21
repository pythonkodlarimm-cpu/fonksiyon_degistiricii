# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/bildirim/__init__.py

ROL:
- Bildirim yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["BildirimYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "BildirimYoneticisi":
        from app.ui.editor_paketi.bildirim.yoneticisi import BildirimYoneticisi
        return BildirimYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

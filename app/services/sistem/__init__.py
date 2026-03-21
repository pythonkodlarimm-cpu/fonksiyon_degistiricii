# -*- coding: utf-8 -*-
"""
DOSYA: app/services/sistem/__init__.py

ROL:
- Sistem yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder
- Sistem katmanını dış dünyaya kontrollü şekilde açar

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["SistemYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "SistemYoneticisi":
        from app.services.sistem.yoneticisi import SistemYoneticisi
        return SistemYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

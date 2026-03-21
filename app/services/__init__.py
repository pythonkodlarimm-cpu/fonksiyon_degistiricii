# -*- coding: utf-8 -*-
"""
DOSYA: app/services/__init__.py

ROL:
- ServicesYoneticisi için lazy import giriş noktası sağlar
- Import maliyetini azaltır
- Circular import riskini düşürür

SURUM: 1
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["ServicesYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "ServicesYoneticisi":
        from app.services.yoneticisi import ServicesYoneticisi
        return ServicesYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

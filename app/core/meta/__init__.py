# -*- coding: utf-8 -*-
"""
DOSYA: app/core/meta/__init__.py

ROL:
- MetaYoneticisi için lazy import giriş noktası sağlar
- Import maliyetini azaltır
- Circular import riskini düşürür

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["MetaYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "MetaYoneticisi":
        from app.core.meta.yoneticisi import MetaYoneticisi
        return MetaYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

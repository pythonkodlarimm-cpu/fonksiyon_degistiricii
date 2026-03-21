# -*- coding: utf-8 -*-
"""
DOSYA: app/services/dosya/__init__.py

ROL:
- Dosya yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder
- Dosya katmanını dış dünyaya kontrollü şekilde açar

MİMARİ:
- Sadece DosyaYoneticisi dışarı açılır
- Alt servis (servisi.py) doğrudan erişilmez
- Lazy import kullanılır

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["DosyaYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "DosyaYoneticisi":
        from app.services.dosya.yoneticisi import DosyaYoneticisi
        return DosyaYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

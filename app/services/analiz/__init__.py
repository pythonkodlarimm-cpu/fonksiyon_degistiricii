# -*- coding: utf-8 -*-
"""
DOSYA: app/services/analiz/__init__.py

ROL:
- Analiz yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder
- Analiz katmanını dış dünyaya kontrollü şekilde açar

MİMARİ:
- Sadece AnalizYoneticisi dışarı açılır
- Alt servisler doğrudan export edilmez
- Lazy import kullanılır

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["AnalizYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "AnalizYoneticisi":
        from app.services.analiz.yoneticisi import AnalizYoneticisi
        return AnalizYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

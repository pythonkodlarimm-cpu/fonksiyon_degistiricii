# -*- coding: utf-8 -*-
"""
DOSYA: app/services/reklam/__init__.py

ROL:
- Reklam yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder
- Reklam katmanını dış dünyaya kontrollü şekilde açar

MİMARİ:
- Sadece ReklamYoneticisi dışarı açılır
- Alt servisler doğrudan export edilmez
- Lazy import kullanılır

SURUM: 4
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["ReklamYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "ReklamYoneticisi":
        from app.services.reklam.yoneticisi import ReklamYoneticisi
        return ReklamYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

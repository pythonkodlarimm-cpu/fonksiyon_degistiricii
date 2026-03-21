# -*- coding: utf-8 -*-
"""
DOSYA: app/services/belge/__init__.py

ROL:
- Belge yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder
- Belge katmanını dış dünyaya kontrollü şekilde açar

MİMARİ:
- Sadece BelgeYoneticisi dışarı açılır
- Alt servisler doğrudan import edilmez
- Lazy import kullanılır

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["BelgeYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "BelgeYoneticisi":
        from app.services.belge.yoneticisi import BelgeYoneticisi
        return BelgeYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

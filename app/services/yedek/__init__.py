# -*- coding: utf-8 -*-
"""
DOSYA: app/services/yedek/__init__.py

ROL:
- Yedek yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder
- Yedek katmanını dış dünyaya kontrollü şekilde açar

MİMARİ:
- Sadece YedekYoneticisi dışarı açılır
- Alt servisler doğrudan export edilmez
- Lazy import kullanılır

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["YedekYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "YedekYoneticisi":
        from app.services.yedek.yoneticisi import YedekYoneticisi
        return YedekYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

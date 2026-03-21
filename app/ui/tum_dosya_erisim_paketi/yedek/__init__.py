# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/yedek/__init__.py

ROL:
- Yedek yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["TumDosyaErisimYedekYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "TumDosyaErisimYedekYoneticisi":
        from app.ui.tum_dosya_erisim_paketi.yedek.yoneticisi import (
            TumDosyaErisimYedekYoneticisi,
        )
        return TumDosyaErisimYedekYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

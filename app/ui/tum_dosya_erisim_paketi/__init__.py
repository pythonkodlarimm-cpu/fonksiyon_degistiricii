# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/__init__.py

ROL:
- Paket için tek giriş noktası sağlar
- TumDosyaErisimYoneticisi'ne lazy erişim sunar
- Import maliyetini azaltır
- Circular import riskini engeller

KULLANIM:
from app.ui.tum_dosya_erisim_paketi import TumDosyaErisimYoneticisi

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations
from typing import Any

__all__ = ["TumDosyaErisimYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "TumDosyaErisimYoneticisi":
        from app.ui.tum_dosya_erisim_paketi.yoneticisi import (
            TumDosyaErisimYoneticisi,
        )
        return TumDosyaErisimYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/popups/__init__.py

ROL:
- Popup yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder
- Popup katmanını dış dünyaya tek kapıdan açar

MİMARİ:
- Lazy import kullanır
- Alt modül detaylarını gizler
- Üst katman sadece bu paket üzerinden erişim sağlar
- Genişletilebilir yapıdadır (ileride yeni popup yöneticileri eklenebilir)

KULLANIM:
from app.ui.tum_dosya_erisim_paketi.popups import TumDosyaErisimPopupsYoneticisi

SURUM: 3
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "TumDosyaErisimPopupsYoneticisi",
]


def __getattr__(name: str) -> Any:
    if name == "TumDosyaErisimPopupsYoneticisi":
        from app.ui.tum_dosya_erisim_paketi.popups.yoneticisi import (
            TumDosyaErisimPopupsYoneticisi,
        )
        return TumDosyaErisimPopupsYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

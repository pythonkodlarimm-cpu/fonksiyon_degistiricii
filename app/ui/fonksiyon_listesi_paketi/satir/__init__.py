# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/satir/__init__.py

ROL:
- Satır yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder
- Satır alt paketini dış dünyaya yalnızca yönetici üzerinden açar

MİMARİ:
- Doğrudan FonksiyonSatiri sınıfı dışa açılmaz
- Erişim sadece yoneticisi.py üzerinden sağlanır
- Lazy import ile gereksiz erken yükleme önlenir

KULLANIM:
from app.ui.fonksiyon_listesi_paketi.satir import SatirYoneticisi

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur

SURUM: 2
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["SatirYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "SatirYoneticisi":
        from app.ui.fonksiyon_listesi_paketi.satir.yoneticisi import SatirYoneticisi
        return SatirYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

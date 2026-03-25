# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/__init__.py

ROL:
- Fonksiyon listesi paketine lazy erişim sağlar
- FonksiyonListesiYoneticisi sınıfını dışa açar
- Import yükünü azaltır
- Circular import riskini minimize eder
- Paket dışı katmanların iç modül yollarını bilmeden yöneticiye erişmesini sağlar

MİMARİ:
- Paket dışına sadece yönetici açılır
- Alt modüller doğrudan erişime kapalıdır
- Lazy import ile performans optimize edilir

KULLANIM:
from app.ui.fonksiyon_listesi_paketi import FonksiyonListesiYoneticisi

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur

SURUM: 3
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["FonksiyonListesiYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "FonksiyonListesiYoneticisi":
        from app.ui.fonksiyon_listesi_paketi.yoneticisi import (
            FonksiyonListesiYoneticisi,
        )
        return FonksiyonListesiYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

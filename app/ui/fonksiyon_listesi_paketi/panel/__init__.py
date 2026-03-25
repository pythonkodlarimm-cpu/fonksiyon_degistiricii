# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/panel/__init__.py

ROL:
- Panel yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder
- Panel alt paketini dış dünyaya yalnızca yönetici üzerinden açar

MİMARİ:
- Doğrudan FonksiyonListesi sınıfı dışa açılmaz
- Erişim sadece yoneticisi.py üzerinden sağlanır
- Lazy import ile gereksiz erken yükleme önlenir

KULLANIM:
from app.ui.fonksiyon_listesi_paketi.panel import PanelYoneticisi

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur

SURUM: 2
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["PanelYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "PanelYoneticisi":
        from app.ui.fonksiyon_listesi_paketi.panel.yoneticisi import PanelYoneticisi
        return PanelYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

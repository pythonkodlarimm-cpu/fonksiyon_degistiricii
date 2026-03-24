# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dil_paketi/popup/__init__.py

ROL:
- Dil popup katmanına lazy erişim sağlar
- Sadece DilPopupYoneticisi sınıfını dışa açar
- Import yükünü azaltır
- Alt popup modülünü kontrollü biçimde sunar
- Popup sınıfına doğrudan erişimi kapatır

MİMARİ:
- Popup alt paketinin dışa açılan yüzüdür
- Lazy import ile gereksiz erken yüklemeyi önler
- Circular import riskini azaltmaya yardımcı olur
- Alt modüller doğrudan import edilmez, __getattr__ üzerinden yüklenir
- Üst katman sadece yönetici üzerinden popup açar

KULLANIM:
from app.ui.dil_paketi.popup import DilPopupYoneticisi

API UYUMLULUK:
- Android ve masaüstü ile uyumludur
- Platform bağımsızdır

SURUM: 4
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "DilPopupYoneticisi",
]


def __getattr__(name: str) -> Any:
    if name == "DilPopupYoneticisi":
        from app.ui.dil_paketi.popup.yoneticisi import DilPopupYoneticisi
        return DilPopupYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

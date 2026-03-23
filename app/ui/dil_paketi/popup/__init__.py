# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dil_paketi/popup/__init__.py

ROL:
- Dil popup katmanına lazy erişim sağlar
- DilSecimPopup sınıfını dışa açar
- Import yükünü azaltır
- Alt popup modülünü kontrollü biçimde sunar

MİMARİ:
- Popup alt paketinin dışa açılan yüzüdür
- Lazy import ile gereksiz erken yüklemeyi önler
- Circular import riskini azaltmaya yardımcı olur

API UYUMLULUK:
- Android ve masaüstü ile uyumludur
- Platform bağımsızdır

SURUM: 1
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["DilSecimPopup"]


def __getattr__(name: str) -> Any:
    if name == "DilSecimPopup":
        from app.ui.dil_paketi.popup.dil_secim_popup import DilSecimPopup
        return DilSecimPopup

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

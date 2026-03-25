# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/popup/__init__.py

ROL:
- Popup yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder
- Üst katmanın popup yöneticisine tek noktadan erişmesini sağlar

MİMARİ:
- __getattr__ ile lazy import yapılır
- PopupYoneticisi dış dünyaya açılan tek sınıftır
- Alt modüller doğrudan import edilmez

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur

SURUM: 2
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["PopupYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "PopupYoneticisi":
        from app.ui.editor_paketi.popup.yoneticisi import PopupYoneticisi
        return PopupYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

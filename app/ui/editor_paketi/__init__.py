# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/__init__.py

ROL:
- Editor yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder
- Editor paketini dış dünyaya kontrollü şekilde açar
- Üst katmanın yalnızca EditorYoneticisi üzerinden erişmesini garanti eder

MİMARİ:
- __getattr__ ile lazy import yapılır
- Paket dışına yalnızca EditorYoneticisi açılır
- Alt modüller doğrudan import edilmez

KULLANIM:
from app.ui.editor_paketi import EditorYoneticisi

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur

SURUM: 3
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["EditorYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "EditorYoneticisi":
        from app.ui.editor_paketi.yoneticisi import EditorYoneticisi
        return EditorYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/__init__.py

ROL:
- Editor yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder
- Editor paketini dış dünyaya kontrollü şekilde açar

SURUM: 1
TARIH: 2026-03-19
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

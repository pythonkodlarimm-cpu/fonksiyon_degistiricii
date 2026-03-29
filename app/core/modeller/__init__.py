# -*- coding: utf-8 -*-
"""
DOSYA: app/core/modeller/__init__.py

ROL:
- Model katmanı için public giriş noktası sağlar
- FunctionItem ve ModellerYoneticisi sınıflarını lazy olarak dışa açar
- Üst katmanın alt modül yapısını bilmesini engeller

MİMARİ:
- Lazy import kullanır (__getattr__)
- Import maliyetini minimize eder
- Circular import riskini azaltır
- Sadece __all__ içinde tanımlı API dışarı açılır

PUBLIC API:
- FunctionItem
- ModellerYoneticisi

BAĞIMLILIKLAR:
- app/core/modeller/modeller.py
- app/core/modeller/yoneticisi.py

SURUM: 2
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "FunctionItem",
    "ModellerYoneticisi",
]


def __getattr__(name: str) -> Any:
    """
    Lazy import resolver.

    İstenen attribute ilk erişimde ilgili modülden yüklenir.
    """

    if name == "FunctionItem":
        from app.core.modeller.modeller import FunctionItem
        return FunctionItem

    if name == "ModellerYoneticisi":
        from app.core.modeller.yoneticisi import ModellerYoneticisi
        return ModellerYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    """
    IDE ve introspection için görünür API listesi.
    """
    return sorted(__all__)

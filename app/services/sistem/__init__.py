# -*- coding: utf-8 -*-
"""
DOSYA: app/services/sistem/__init__.py

ROL:
- Sistem yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder
- Sistem katmanını dış dünyaya kontrollü şekilde açar
- Dil, ayar, app state ve bildirim servislerini tek kapıdan sunar

MİMARİ:
- Sistem katmanının dışa açılan yüzüdür
- Alt modül yapısını gizler
- Lazy import ile yalnızca ihtiyaç anında yükleme yapar
- ServicesYoneticisi ile birlikte çalışacak şekilde tasarlanmıştır

UYUMLULUK:
- Android ve masaüstü ile uyumlu
- Platform bağımsızdır

SURUM: 2
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["SistemYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "SistemYoneticisi":
        from app.services.sistem.yoneticisi import SistemYoneticisi
        return SistemYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

# -*- coding: utf-8 -*-
"""
DOSYA: app/services/sistem/__init__.py

ROL:
- Sistem yöneticisine lazy erişim sağlar
- Import yükünü azaltır
- Circular import riskini minimize eder
- Sistem katmanını dış dünyaya kontrollü şekilde açar
- Dil, ayar, app state, geçici bildirim ve premium servislerini tek kapıdan sunar
- diller/ klasöründen otomatik dil algılayan sistem yapısına dış erişim noktası sağlar

MİMARİ:
- Sistem katmanının dışa açılan yüzüdür
- Alt modül yapısını gizler
- Lazy import ile yalnızca ihtiyaç anında yükleme yapar
- ServicesYoneticisi ile birlikte çalışacak şekilde tasarlanmıştır
- Dış katman sadece SistemYoneticisi sınıfını bilir

UYUMLULUK:
- Android ve masaüstü ile uyumlu
- Platform bağımsızdır

SURUM: 3
TARIH: 2026-03-24
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

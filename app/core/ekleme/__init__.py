# -*- coding: utf-8 -*-
"""
DOSYA: app/core/ekleme/__init__.py

ROL:
- ekleme paketinin dışa açılan API yüzü
- Sadece EklemeYoneticisi export edilir
- Lazy import ile yükleme geciktirilir

MİMARİ:
- Strict API (__all__)
- Lazy import (__getattr__)
- Internal cache (tekrar import yok)
- Deterministik davranış

SURUM: 1
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations

from typing import Any, Final

__all__: Final[list[str]] = [
    "EklemeYoneticisi",
]

__lazy_cache: dict[str, Any] = {}


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(
            f"{__name__!r} modülünde '{name}' export edilmemiş."
        )

    cached = __lazy_cache.get(name)
    if cached is not None:
        return cached

    if name == "EklemeYoneticisi":
        from app.core.ekleme.yoneticisi import EklemeYoneticisi
        __lazy_cache[name] = EklemeYoneticisi
        return EklemeYoneticisi

    raise AttributeError(
        f"{__name__!r} modülünde '{name}' çözümlenemedi."
    )


def __dir__() -> list[str]:
    return sorted(__all__)

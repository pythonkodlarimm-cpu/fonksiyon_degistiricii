# -*- coding: utf-8 -*-
"""
DOSYA: app/core/dil/__init__.py

ROL:
- Dil paketi için tek giriş noktası sağlar
- DilYoneticisi sınıfını lazy import ile yükler

MİMARİ:
- Strict API (__all__)
- Lazy import (__getattr__)
- Type-safe cache
- Deterministik davranış
- Tek çözümleme (cache sonrası tekrar import yok)
- Geriye uyumluluk katmanı içermez

SURUM: 1
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Final, Type

__all__: Final[tuple[str, ...]] = (
    "DilYoneticisi",
)

# Type-safe cache
__lazy_cache: dict[str, Type[object]] = {}


def __getattr__(name: str) -> Type[object]:
    """
    Lazy attribute resolver (strict + deterministic).
    """

    if name != "DilYoneticisi":
        raise AttributeError(
            f"{__name__!r} modülünde '{name}' export edilmemiş."
        )

    cached = __lazy_cache.get(name)
    if cached is not None:
        return cached

    from app.core.dil.yoneticisi import DilYoneticisi

    __lazy_cache[name] = DilYoneticisi
    return DilYoneticisi


def __dir__() -> list[str]:
    """
    IDE / autocomplete desteği.
    """
    return list(__all__)

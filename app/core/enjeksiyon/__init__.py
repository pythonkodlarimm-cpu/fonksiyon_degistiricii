# -*- coding: utf-8 -*-
"""
DOSYA: app/core/enjeksiyon/__init__.py

ROL:
- EnjeksiyonYoneticisi için lazy import giriş noktası
- Import maliyetini azaltır
- Net ve deterministik API sağlar

MİMARİ:
- Tek export (strict API)
- Lazy load + kesin cache
- Type güvenli cache yapısı
- Sıfır fallback / belirsizlik

SURUM: 2
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations

from typing import Type

__all__ = ["EnjeksiyonYoneticisi"]

# =========================================================
# STRICT CACHE
# =========================================================
_cache: dict[str, Type] = {}


# =========================================================
# LAZY RESOLVE
# =========================================================
def __getattr__(name: str) -> Type:
    """
    Sadece izin verilen export'u çözer.
    """

    if name == "EnjeksiyonYoneticisi":
        if name not in _cache:
            from app.core.enjeksiyon.yoneticisi import EnjeksiyonYoneticisi
            _cache[name] = EnjeksiyonYoneticisi

        return _cache[name]

    raise AttributeError(
        f"{__name__!r} modülünde '{name}' export edilmemiş."
    )


# =========================================================
# IDE DESTEK
# =========================================================
def __dir__() -> list[str]:
    return __all__

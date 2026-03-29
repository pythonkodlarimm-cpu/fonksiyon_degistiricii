# -*- coding: utf-8 -*-
"""
DOSYA: app/core/parca_degistirme/__init__.py

ROL:
- ParcaDegistirmeYoneticisi için lazy import giriş noktası sağlar
- Import maliyetini azaltır
- Paket dışına kontrollü yüzey sunar

MİMARİ:
- Tek export mantığı
- Lazy çözümleme
- Net API

SURUM: 1
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations

from typing import Type

__all__ = ["ParcaDegistirmeYoneticisi"]

_cache: dict[str, Type] = {}


def __getattr__(name: str) -> Type:
    if name == "ParcaDegistirmeYoneticisi":
        if name not in _cache:
            from app.core.parca_degistirme.yoneticisi import ParcaDegistirmeYoneticisi

            _cache[name] = ParcaDegistirmeYoneticisi

        return _cache[name]

    raise AttributeError(f"{__name__!r} modülünde '{name}' export edilmemiş.")


def __dir__() -> list[str]:
    return __all__

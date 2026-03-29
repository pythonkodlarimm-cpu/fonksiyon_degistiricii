# -*- coding: utf-8 -*-
"""
DOSYA: app/services/reklam/__init__.py

ROL:
- Reklam katmanı için tek giriş noktası sağlar
- ReklamYoneticisi sınıfına lazy erişim sağlar
- Reklam katmanını dış dünyaya kontrollü şekilde açar

MİMARİ:
- Strict API (__all__)
- Lazy import (__getattr__)
- Type-safe cache
- Deterministik davranış
- Tek çözümleme (cache sonrası tekrar import yok)
- Geriye uyumluluk katmanı içermez
- Sıfır fallback / sürpriz davranış

NOT:
- Sadece ReklamYoneticisi dışarı açılır
- Alt servisler doğrudan export edilmez

SURUM: 6
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Final, Type


__all__: Final[tuple[str, ...]] = (
    "ReklamYoneticisi",
)

__lazy_cache: dict[str, Type[object]] = {}


def __getattr__(name: str) -> Type[object]:
    """
    Lazy attribute resolver (strict + deterministic).
    """
    if name != "ReklamYoneticisi":
        raise AttributeError(
            f"{__name__!r} modülünde '{name}' export edilmemiş."
        )

    cached = __lazy_cache.get(name)
    if cached is not None:
        return cached

    from app.services.reklam.yoneticisi import ReklamYoneticisi

    __lazy_cache[name] = ReklamYoneticisi
    return ReklamYoneticisi


def __dir__() -> list[str]:
    """
    IDE / autocomplete desteği.
    """
    return list(__all__)

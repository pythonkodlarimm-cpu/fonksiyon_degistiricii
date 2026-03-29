# -*- coding: utf-8 -*-
"""
DOSYA: app/services/android/__init__.py

ROL:
- Android servis katmanı için tek giriş noktası sağlar
- AndroidYoneticisi sınıfına lazy erişim sağlar
- Android servis katmanını dış dünyaya kontrollü şekilde açar

MİMARİ:
- Strict API (__all__)
- Lazy import (__getattr__)
- Type-safe cache
- Deterministik davranış
- Tek çözümleme (cache sonrası tekrar import yok)
- Geriye uyumluluk katmanı içermez
- Sıfır fallback / sürpriz davranış

NOT:
- Sadece AndroidYoneticisi dışarı açılır
- Alt servisler doğrudan export edilmez

SURUM: 2
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Final, Type


__all__: Final[tuple[str, ...]] = (
    "AndroidYoneticisi",
)

__lazy_cache: dict[str, Type[object]] = {}


def __getattr__(name: str) -> Type[object]:
    """
    Lazy attribute resolver (strict + deterministic).
    """
    if name != "AndroidYoneticisi":
        raise AttributeError(
            f"{__name__!r} modülünde '{name}' export edilmemiş."
        )

    cached = __lazy_cache.get(name)
    if cached is not None:
        return cached

    from app.services.android.yoneticisi import AndroidYoneticisi

    __lazy_cache[name] = AndroidYoneticisi
    return AndroidYoneticisi


def __dir__() -> list[str]:
    """
    IDE / autocomplete desteği.
    """
    return list(__all__)

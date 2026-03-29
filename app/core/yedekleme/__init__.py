# -*- coding: utf-8 -*-
"""
DOSYA: app/core/yedekleme/__init__.py

ROL:
- Yedekleme paketi için tek giriş noktası sağlar
- YedeklemeYoneticisi sınıfını lazy import ile yükler

MİMARİ:
- Strict API (__all__)
- Lazy import (__getattr__)
- Internal cache (tek çözümleme, tekrar import yok)
- Deterministik davranış
- Type güvenliği yüksek (net cache tipi)

NOT:
- Geriye uyumluluk katmanı içermez
- Sadece izinli export'lar erişilebilir
- Sıfır fallback / sürpriz davranış

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur

SURUM: 2
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Final, Type


__all__: Final[tuple[str, ...]] = (
    "YedeklemeYoneticisi",
)

# strict typed cache
__lazy_cache: dict[str, Type[object]] = {}


def __getattr__(name: str) -> Type[object]:
    """
    Lazy attribute resolver (strict + deterministic).
    """

    if name != "YedeklemeYoneticisi":
        raise AttributeError(
            f"{__name__!r} modülünde '{name}' export edilmemiş."
        )

    cached = __lazy_cache.get(name)
    if cached is not None:
        return cached

    from app.core.yedekleme.yoneticisi import YedeklemeYoneticisi

    __lazy_cache[name] = YedeklemeYoneticisi
    return YedeklemeYoneticisi


def __dir__() -> list[str]:
    """
    IDE / autocomplete desteği.
    """
    return ["YedeklemeYoneticisi"]

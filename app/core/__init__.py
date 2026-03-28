# -*- coding: utf-8 -*-
"""
DOSYA: app/core/__init__.py

ROL:
- Core katmanı için tek giriş noktası sağlar
- CoreYoneticisi sınıfını lazy import ile yükler

MİMARİ:
- Strict API (__all__)
- Lazy import (__getattr__)
- Internal cache (tekrar import yok)
- Deterministik davranış

NOT:
- Geriye uyumluluk yok
- Sadece izinli export'lar erişilebilir

SURUM: 3
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations

from typing import Final


__all__: Final[tuple[str, ...]] = (
    "CoreYoneticisi",
)

__lazy_cache: dict[str, object] = {}


def __getattr__(name: str) -> object:
    """
    Lazy attribute resolver.
    """
    if name not in __all__:
        raise AttributeError(
            f"{__name__!r} modülünde '{name}' export edilmemiş."
        )

    if name in __lazy_cache:
        return __lazy_cache[name]

    if name == "CoreYoneticisi":
        from app.core.yoneticisi import CoreYoneticisi

        __lazy_cache[name] = CoreYoneticisi
        return CoreYoneticisi

    raise AttributeError(
        f"{__name__!r} modülünde '{name}' çözümlenemedi."
    )


def __dir__() -> list[str]:
    """
    IDE / autocomplete desteği.
    """
    return sorted(__all__)

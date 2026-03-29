# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ekranlar/__init__.py

ROL:
- UI ekranları için merkezi ve kontrollü giriş noktası sağlar
- Ana ekran gibi üst seviye UI bileşenlerini dışarı açar
- Lazy import ile gereksiz yüklemeleri engeller

MİMARİ:
- Strict API (__all__)
- Lazy import (__getattr__)
- Type-safe cache
- Deterministik davranış
- Geriye uyumluluk katmanı içermez

SURUM: 2
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Final, TypeAlias

_ModulTipi: TypeAlias = object

__all__: Final[tuple[str, ...]] = (
    "AnaEkran",
)

__lazy_cache: dict[str, _ModulTipi] = {}


def __getattr__(name: str) -> _ModulTipi:
    cached = __lazy_cache.get(name)
    if cached is not None:
        return cached

    if name == "AnaEkran":
        from app.ui.ekranlar.ana_ekran import AnaEkran

        __lazy_cache[name] = AnaEkran
        return AnaEkran

    raise AttributeError(
        f"{__name__!r} paketinde '{name}' export edilmemiş."
    )


def __dir__() -> list[str]:
    return list(__all__)

# -*- coding: utf-8 -*-
"""
DOSYA: app/core/dil_ekle/__init__.py

ROL:
- Dil geliştirici modülünün public API yüzeyini tanımlar
- Sadece yoneticisi.py üzerinden erişim sağlar
- Alt modül detaylarını dışarı kapatır

MİMARİ:
- Strict API (__all__)
- Lazy import kullanır
- Sadece facade export edilir
- Core detayları dışarı sızdırılmaz
- Deterministik ve sade yapı

SURUM: 5
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Any, Final

__all__: Final[tuple[str, ...]] = (
    "DilGelistiriciYonetici",
)

_LAZY_CACHE: dict[str, Any] = {}


def _import_yonetici():
    from app.core.dil_ekle.yoneticisi import DilGelistiriciYonetici

    return DilGelistiriciYonetici


def __getattr__(ad: str) -> Any:
    mevcut = _LAZY_CACHE.get(ad)
    if mevcut is not None:
        return mevcut

    if ad == "DilGelistiriciYonetici":
        nesne = _import_yonetici()
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {ad!r}")

    _LAZY_CACHE[ad] = nesne
    return nesne


def __dir__() -> list[str]:
    return sorted(set(globals().keys()) | set(__all__))

# -*- coding: utf-8 -*-
"""
DOSYA: app/core/degistirme/__init__.py

ROL:
- degistirme paketinin dışa açılan API yüzünü tanımlar
- Sadece DegistirmeYoneticisi sınıfını export eder
- Lazy import ile modül yüklenmesini geciktirir

MİMARİ:
- Strict API (yalnızca __all__)
- Lazy import (__getattr__)
- Internal cache (tekrar import yok)
- Core dışı katmanlar alt modülleri bilmez

BAĞIMLILIKLAR:
- app/core/degistirme/yoneticisi.py

SURUM: 2
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations

from typing import Any, Final


__all__: Final[list[str]] = [
    "DegistirmeYoneticisi",
]

# Lazy cache (type-safe)
__lazy_cache: dict[str, Any] = {}


def __getattr__(name: str) -> Any:
    """
    Lazy attribute resolver.
    """

    if name not in __all__:
        raise AttributeError(
            f"{__name__!r} modülünde '{name}' export edilmemiş."
        )

    cached = __lazy_cache.get(name)
    if cached is not None:
        return cached

    if name == "DegistirmeYoneticisi":
        from app.core.degistirme.yoneticisi import DegistirmeYoneticisi

        __lazy_cache[name] = DegistirmeYoneticisi
        return DegistirmeYoneticisi

    # teorik olarak buraya düşmez
    raise AttributeError(
        f"{__name__!r} modülünde '{name}' çözümlenemedi."
    )


def __dir__() -> list[str]:
    """
    IDE / autocomplete desteği.
    """
    return sorted(__all__)

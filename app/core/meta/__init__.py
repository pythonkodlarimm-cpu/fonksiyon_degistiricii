# -*- coding: utf-8 -*-
"""
DOSYA: app/core/meta/__init__.py

ROL:
- Meta paketinin dışa açılan API yüzünü tanımlar
- MetaYoneticisi sınıfını lazy import ile sağlar
- Import maliyetini azaltır ve başlangıç performansını iyileştirir
- İç modül yapısını dış dünyadan gizler

MİMARİ:
- Sadece izin verilen export'lar erişilebilir
- __getattr__ ile lazy çözümleme yapılır
- İlk erişimden sonra cache kullanılır
- Circular import riskini minimize eder

BAĞIMLILIKLAR:
- app/core/meta/yoneticisi.py

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur

SURUM: 2
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

__all__ = ["MetaYoneticisi"]

# Lazy import cache
__lazy_cache: dict[str, Any] = {}


def __getattr__(name: str) -> Any:
    """
    Lazy attribute resolver.
    """
    if name not in __all__:
        raise AttributeError(
            f"{__name__!r} modülünde '{name}' adında export yok."
        )

    if name in __lazy_cache:
        return __lazy_cache[name]

    if name == "MetaYoneticisi":
        from app.core.meta.yoneticisi import MetaYoneticisi
        __lazy_cache[name] = MetaYoneticisi
        return MetaYoneticisi

    # Teorik fallback (asla buraya düşmemeli)
    raise AttributeError(
        f"{__name__!r} modülünde '{name}' çözümlenemedi."
    )


def __dir__() -> list[str]:
    """
    IDE ve autocomplete desteği için export listesi döner.
    """
    return list(__all__)

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ortak/__init__.py

ROL:
- UI ortak katmanı için tek giriş noktası sağlar
- Ortak modülleri kontrollü şekilde dışarı açar
- Lazy import ile gereksiz yüklenmeleri engeller

MİMARİ:
- Ortak katman tek merkezden erişilir
- Modüller doğrudan import edilmez (lazy erişim)
- UI performansını ve açılış süresini iyileştirir
- Geriye uyumluluk katmanı içermez

SURUM: 2
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

import importlib
from typing import Final, Any


__all__: Final[tuple[str, ...]] = (
    "guard",
    "renkler",
    "boyutlar",
    "stiller",
    "ikonlar",
    "yardimcilar",
)


# ---------------------------------------------------------
# LAZY IMPORT MEKANIZMASI
# ---------------------------------------------------------
def __getattr__(name: str) -> Any:
    """
    Ortak modülleri lazy import ile yükler.

    Args:
        name: İstenen modül adı.

    Returns:
        Modül objesi.

    Raises:
        AttributeError: Geçersiz modül adı.
    """
    if name in __all__:
        return importlib.import_module(f"{__name__}.{name}")

    raise AttributeError(f"{__name__!r} içinde {name!r} bulunamadı.")


def __dir__() -> list[str]:
    """
    IDE ve introspection desteği için görünür üyeleri döndürür.
    """
    return sorted(list(globals().keys()) + list(__all__))

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/popup/__init__.py

ROL:
- Popup bileşenleri için merkezi giriş noktası sağlar
- Tüm popup fonksiyonlarını lazy import ile yükler
- Tek noktadan erişim sağlar

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

_NesneTipi: TypeAlias = object

__all__: Final[tuple[str, ...]] = (
    "dosya_sec",
    "dil_sec_popup",
)

__lazy_cache: dict[str, _NesneTipi] = {}


def __getattr__(name: str) -> _NesneTipi:
    cached = __lazy_cache.get(name)
    if cached is not None:
        return cached

    if name == "dosya_sec":
        from app.ui.popup.dosya_sec_popup import dosya_sec

        __lazy_cache[name] = dosya_sec
        return dosya_sec

    if name == "dil_sec_popup":
        from app.ui.popup.dil_sec_popup import dil_sec_popup

        __lazy_cache[name] = dil_sec_popup
        return dil_sec_popup

    raise AttributeError(
        f"{__name__!r} paketinde '{name}' export edilmemiş."
    )


def __dir__() -> list[str]:
    return list(__all__)

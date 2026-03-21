# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

__all__ = ["SatirYoneticisi", "FonksiyonSatiri"]


def __getattr__(name: str) -> Any:
    if name == "SatirYoneticisi":
        from app.ui.fonksiyon_listesi_paketi.satir.yoneticisi import SatirYoneticisi
        return SatirYoneticisi

    if name == "FonksiyonSatiri":
        from app.ui.fonksiyon_listesi_paketi.satir.satir import FonksiyonSatiri
        return FonksiyonSatiri

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

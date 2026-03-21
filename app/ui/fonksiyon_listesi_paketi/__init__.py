# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

__all__ = ["FonksiyonListesiYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "FonksiyonListesiYoneticisi":
        from app.ui.fonksiyon_listesi_paketi.yoneticisi import FonksiyonListesiYoneticisi
        return FonksiyonListesiYoneticisi
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

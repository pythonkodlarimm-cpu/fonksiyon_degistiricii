# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

__all__ = ["PanelYoneticisi", "FonksiyonListesi"]


def __getattr__(name: str) -> Any:
    if name == "PanelYoneticisi":
        from app.ui.fonksiyon_listesi_paketi.panel.yoneticisi import PanelYoneticisi
        return PanelYoneticisi

    if name == "FonksiyonListesi":
        from app.ui.fonksiyon_listesi_paketi.panel.panel import FonksiyonListesi
        return FonksiyonListesi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

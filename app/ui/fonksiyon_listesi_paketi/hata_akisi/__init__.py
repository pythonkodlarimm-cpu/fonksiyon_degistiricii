# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

__all__ = ["HataAkisiYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "HataAkisiYoneticisi":
        from app.ui.fonksiyon_listesi_paketi.hata_akisi.yoneticisi import (
            HataAkisiYoneticisi,
        )
        return HataAkisiYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

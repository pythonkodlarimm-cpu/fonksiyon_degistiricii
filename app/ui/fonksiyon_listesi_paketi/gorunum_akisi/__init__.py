# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

__all__ = ["GorunumAkisiYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "GorunumAkisiYoneticisi":
        from app.ui.fonksiyon_listesi_paketi.gorunum_akisi.yoneticisi import (
            GorunumAkisiYoneticisi,
        )
        return GorunumAkisiYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

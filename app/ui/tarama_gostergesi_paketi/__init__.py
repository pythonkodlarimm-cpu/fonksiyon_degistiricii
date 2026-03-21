# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

__all__ = ["TaramaGostergesiYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "TaramaGostergesiYoneticisi":
        from app.ui.tarama_gostergesi_paketi.yoneticisi import TaramaGostergesiYoneticisi
        return TaramaGostergesiYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

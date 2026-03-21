# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Any

__all__ = ["DegistirmeYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "DegistirmeYoneticisi":
        from app.core.degistirme.yoneticisi import DegistirmeYoneticisi
        return DegistirmeYoneticisi
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

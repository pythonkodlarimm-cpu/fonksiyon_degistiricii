# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

__all__ = ["FunctionItem", "ModellerYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "FunctionItem":
        from app.core.modeller.modeller import FunctionItem
        return FunctionItem

    if name == "ModellerYoneticisi":
        from app.core.modeller.yoneticisi import ModellerYoneticisi
        return ModellerYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

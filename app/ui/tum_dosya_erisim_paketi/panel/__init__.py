# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

__all__ = ["TumDosyaErisimPanelYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "TumDosyaErisimPanelYoneticisi":
        from app.ui.tum_dosya_erisim_paketi.panel.yoneticisi import (
            TumDosyaErisimPanelYoneticisi,
        )
        return TumDosyaErisimPanelYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

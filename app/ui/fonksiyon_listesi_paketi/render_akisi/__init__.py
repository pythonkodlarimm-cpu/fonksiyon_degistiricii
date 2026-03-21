# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

__all__ = ["RenderAkisiYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "RenderAkisiYoneticisi":
        from app.ui.fonksiyon_listesi_paketi.render_akisi.yoneticisi import (
            RenderAkisiYoneticisi,
        )
        return RenderAkisiYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

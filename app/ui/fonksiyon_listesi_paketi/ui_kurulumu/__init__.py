# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

__all__ = ["UiKurulumuYoneticisi"]


def __getattr__(name: str) -> Any:
    if name == "UiKurulumuYoneticisi":
        from app.ui.fonksiyon_listesi_paketi.ui_kurulumu.yoneticisi import (
            UiKurulumuYoneticisi,
        )
        return UiKurulumuYoneticisi

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)

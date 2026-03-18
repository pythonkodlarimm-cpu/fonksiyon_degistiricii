# -*- coding: utf-8 -*-

__all__ = ["TumDosyaErisimPaneli"]


def __getattr__(name):
    if name == "TumDosyaErisimPaneli":
        from app.ui.tum_dosya_erisim_paketi.panel import TumDosyaErisimPaneli
        return TumDosyaErisimPaneli
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

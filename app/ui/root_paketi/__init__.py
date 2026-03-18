# -*- coding: utf-8 -*-

__all__ = ["RootWidget"]


def __getattr__(name):
    if name == "RootWidget":
        from app.ui.root_paketi.root import RootWidget
        return RootWidget

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

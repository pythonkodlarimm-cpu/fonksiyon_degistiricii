# -*- coding: utf-8 -*-

__all__ = [
    "EditorPaneli",
    "RootWidget",
]


def __getattr__(name):
    if name == "EditorPaneli":
        from app.ui.editor_paketi.editor_paneli import EditorPaneli
        return EditorPaneli

    if name == "RootWidget":
        from app.ui.editor_paketi.root_widget import RootWidget
        return RootWidget

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

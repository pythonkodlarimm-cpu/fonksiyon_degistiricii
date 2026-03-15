# -*- coding: utf-8 -*-
from __future__ import annotations

from app.ui.dosya_secici_paketi.models import DocumentSelection, DocumentSession

__all__ = [
    "DocumentSelection",
    "DocumentSession",
    "get_desktop_picker_class",
    "get_android_document_picker_class",
]


def get_desktop_picker_class():
    from app.ui.dosya_secici_paketi.desktop_picker import DesktopPicker
    return DesktopPicker


def get_android_document_picker_class():
    from app.ui.dosya_secici_paketi.android_document_picker import AndroidDocumentPicker
    return AndroidDocumentPicker

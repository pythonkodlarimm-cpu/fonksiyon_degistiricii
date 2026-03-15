# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/__init__.py

ROL:
- Dosya seçici paketinin hafif giriş noktası
- Uygulama açılışını yavaşlatmamak için lazy import yaklaşımı kullanır

KURAL:
- Ağır alt modüller import-time'da yüklenmez
- Hafif model doğrudan dışa açılır
- Gerekirse yardımcı getter fonksiyonları ile modül geç yüklenir

NOT:
- Yeni Android akışında android_tree_picker kullanılır
- desktop_picker tüm platformlarda iç picker olarak kullanılabilir
- Eski android_picker artık ana akışta kullanılmaz

SURUM: 3
TARIH: 2026-03-15
IMZA: FY.
"""

from __future__ import annotations

from app.ui.dosya_secici_paketi.models import PickerSelection

__all__ = [
    "PickerSelection",
    "get_desktop_picker_class",
    "get_android_tree_picker_class",
]


def get_desktop_picker_class():
    from app.ui.dosya_secici_paketi.desktop_picker import DesktopPicker

    return DesktopPicker


def get_android_tree_picker_class():
    from app.ui.dosya_secici_paketi.android_tree_picker import AndroidTreePicker

    return AndroidTreePicker

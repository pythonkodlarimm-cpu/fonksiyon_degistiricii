# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/yoneticisi.py

ROL:
- Root widget katmanına tek giriş noktası sağlamak
- RootWidget erişimini merkezileştirmek

SURUM: 1
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations


class RootWidgetYoneticisi:
    def root_widget_sinifi(self):
        from app.ui.root_paketi.root.root import RootWidget
        return RootWidget

    def root_widget_olustur(self, **kwargs):
        return self.root_widget_sinifi()(**kwargs)
# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/bagimlilik/yoneticisi.py

ROL:
- Root bağımlılık katmanına tek giriş noktası sağlamak
- RootLazyImportsMixin erişimini merkezileştirmek

SURUM: 1
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations


class RootBagimlilikYoneticisi:
    def mixin_sinifi(self):
        from app.ui.root_paketi.bagimlilik.lazy_imports import RootLazyImportsMixin
        return RootLazyImportsMixin
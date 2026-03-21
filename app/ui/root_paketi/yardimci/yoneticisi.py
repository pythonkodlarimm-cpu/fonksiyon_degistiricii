# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/yardimci/yoneticisi.py

ROL:
- Root yardımcı katmanına tek giriş noktası sağlamak
- RootYardimcilariMixin erişimini merkezileştirmek

SURUM: 1
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations


class RootYardimciYoneticisi:
    def mixin_sinifi(self):
        from app.ui.root_paketi.yardimci.yardimcilari import RootYardimcilariMixin
        return RootYardimcilariMixin
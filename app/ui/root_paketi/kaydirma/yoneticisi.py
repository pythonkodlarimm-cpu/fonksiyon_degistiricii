# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/kaydirma/yoneticisi.py

ROL:
- Root kaydırma katmanına tek giriş noktası sağlamak
- RootScrollMixin erişimini merkezileştirmek

SURUM: 1
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations


class RootKaydirmaYoneticisi:
    def mixin_sinifi(self):
        from app.ui.root_paketi.kaydirma.scroll import RootScrollMixin
        return RootScrollMixin
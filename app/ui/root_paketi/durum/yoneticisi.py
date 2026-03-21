# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/durum/yoneticisi.py

ROL:
- Root durum katmanına tek giriş noktası sağlamak
- RootStatusMixin erişimini merkezileştirmek

SURUM: 1
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations


class RootDurumYoneticisi:
    def mixin_sinifi(self):
        from app.ui.root_paketi.durum.status import RootStatusMixin
        return RootStatusMixin
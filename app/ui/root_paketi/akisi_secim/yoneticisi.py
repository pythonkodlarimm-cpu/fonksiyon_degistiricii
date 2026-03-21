# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_secim/yoneticisi.py

ROL:
- Root seçim akışı katmanına tek giriş noktası sağlamak
- RootSecimAkisiMixin erişimini merkezileştirmek

SURUM: 1
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations


class RootSecimAkisiYoneticisi:
    def mixin_sinifi(self):
        from app.ui.root_paketi.akisi_secim.secim_akisi import RootSecimAkisiMixin
        return RootSecimAkisiMixin
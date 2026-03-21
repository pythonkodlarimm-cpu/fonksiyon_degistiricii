# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_guncelleme/yoneticisi.py

ROL:
- Root güncelleme akışı katmanına tek giriş noktası sağlamak
- RootGuncellemeAkisiMixin erişimini merkezileştirmek

SURUM: 1
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations


class RootGuncellemeAkisiYoneticisi:
    def mixin_sinifi(self):
        from app.ui.root_paketi.akisi_guncelleme.guncelleme_akisi import (
            RootGuncellemeAkisiMixin,
        )
        return RootGuncellemeAkisiMixin
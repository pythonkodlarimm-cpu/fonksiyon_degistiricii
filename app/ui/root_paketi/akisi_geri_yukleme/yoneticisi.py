# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_geri_yukleme/yoneticisi.py

ROL:
- Root geri yükleme akışı katmanına tek giriş noktası sağlamak
- RootGeriYuklemeAkisiMixin erişimini merkezileştirmek

SURUM: 1
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations


class RootGeriYuklemeAkisiYoneticisi:
    def mixin_sinifi(self):
        from app.ui.root_paketi.akisi_geri_yukleme.geri_yukleme_akisi import (
            RootGeriYuklemeAkisiMixin,
        )
        return RootGeriYuklemeAkisiMixin
# -*- coding: utf-8 -*-
from __future__ import annotations


class TumDosyaErisimPanelYoneticisi:
    def panel_sinifi(self):
        from app.ui.tum_dosya_erisim_paketi.panel.panel import TumDosyaErisimPaneli
        return TumDosyaErisimPaneli

    def panel_olustur(self, **kwargs):
        return self.panel_sinifi()(**kwargs)
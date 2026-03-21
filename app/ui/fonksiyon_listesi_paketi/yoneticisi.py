# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/yoneticisi.py
"""

from __future__ import annotations


class FonksiyonListesiYoneticisi:
    def _panel_yoneticisi(self):
        from app.ui.fonksiyon_listesi_paketi.panel import PanelYoneticisi
        return PanelYoneticisi()

    def _satir_yoneticisi(self):
        from app.ui.fonksiyon_listesi_paketi.satir import SatirYoneticisi
        return SatirYoneticisi()

    def _arama_yoneticisi(self):
        from app.ui.fonksiyon_listesi_paketi.arama import AramaYoneticisi
        return AramaYoneticisi()

    def _onizleme_yoneticisi(self):
        from app.ui.fonksiyon_listesi_paketi.onizleme import OnizlemeYoneticisi
        return OnizlemeYoneticisi()

    def _yardimci_yoneticisi(self):
        from app.ui.fonksiyon_listesi_paketi.yardimci import YardimciYoneticisi
        return YardimciYoneticisi()

    def panel_sinifi(self):
        return self._panel_yoneticisi().panel_sinifi()

    def panel_olustur(self, on_select, on_error=None, **kwargs):
        PanelSinifi = self.panel_sinifi()
        return PanelSinifi(
            on_select=on_select,
            on_error=on_error,
            **kwargs,
        )

    def satir_sinifi(self):
        return self._satir_yoneticisi().satir_sinifi()

    def arama_yoneticisi(self):
        return self._arama_yoneticisi()

    def onizleme_yoneticisi(self):
        return self._onizleme_yoneticisi()

    def yardimci_yoneticisi(self):
        return self._yardimci_yoneticisi()
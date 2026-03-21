# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tarama_gostergesi_paketi/yoneticisi.py

ROL:
- Tarama loading ve başarı overlay bileşenlerine tek giriş noktası sağlamak
- Root katmanının alt modül detaylarını bilmeden overlay oluşturmasını sağlamak

MİMARİ:
- Loading ve success overlay sınıflarını merkezileştirir
- Üst katman sadece bu yöneticiyi kullanır

SURUM: 1
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations


class TaramaGostergesiYoneticisi:
    def loading_overlay_sinifi(self):
        from app.ui.tarama_gostergesi_paketi.loading_overlay import TaramaLoadingOverlay
        return TaramaLoadingOverlay

    def success_overlay_sinifi(self):
        from app.ui.tarama_gostergesi_paketi.success_overlay import TaramaSuccessOverlay
        return TaramaSuccessOverlay

    def loading_overlay_olustur(self, **kwargs):
        OverlaySinifi = self.loading_overlay_sinifi()
        return OverlaySinifi(**kwargs)

    def success_overlay_olustur(self, **kwargs):
        OverlaySinifi = self.success_overlay_sinifi()
        return OverlaySinifi(**kwargs)
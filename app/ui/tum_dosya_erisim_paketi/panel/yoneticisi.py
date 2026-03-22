# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/panel/yoneticisi.py

ROL:
- Tüm dosya erişim panel bileşenine tek giriş noktası sağlar
- Panel sınıfını lazy import ile yükler
- Üst katmanın panel implementasyon detaylarını bilmesini engeller

MİMARİ:
- Lazy import kullanır (import maliyetini azaltır)
- UI bileşenini doğrudan expose etmez, yönetici üzerinden verir
- Panel oluşturma ve sınıf erişimi ayrılmıştır

KULLANIM:
- panel_sinifi() -> Panel class döner
- panel_olustur(**kwargs) -> Panel instance oluşturur

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- UI katmanı dışında bağımlılığı yoktur

SURUM: 2
TARIH: 2026-03-22
IMZA: FY.
"""

from __future__ import annotations


class TumDosyaErisimPanelYoneticisi:
    def panel_sinifi(self):
        """
        Panel sınıfını lazy import ile döndürür.

        Dönüş:
        - TumDosyaErisimPaneli (class)
        """
        from app.ui.tum_dosya_erisim_paketi.panel.panel import TumDosyaErisimPaneli
        return TumDosyaErisimPaneli

    def panel_olustur(self, **kwargs):
        """
        Panel instance oluşturur.

        Parametreler:
        - **kwargs: Panel constructor parametreleri

        Dönüş:
        - TumDosyaErisimPaneli instance
        """
        return self.panel_sinifi()(**kwargs)

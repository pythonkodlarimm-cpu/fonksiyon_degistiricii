# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/panel/yoneticisi.py

ROL:
- Tüm dosya erişim panel bileşenine tek giriş noktası sağlar
- Panel sınıfını lazy import ile yükler
- Üst katmanın panel implementasyon detaylarını bilmesini engeller
- Panel oluştururken services ve callback bağımlılıklarını güvenli şekilde aşağı katmana geçirir

MİMARİ:
- Lazy import kullanır
- UI bileşenini doğrudan expose etmez, yönetici üzerinden verir
- Panel oluşturma ve sınıf erişimi ayrılmıştır
- Dil değişimi gibi üst katman callback'leri **kwargs ile panele aktarılır
- Fail-soft yaklaşım: hata durumunda tanılama logu basar

KULLANIM:
- panel_sinifi() -> Panel class döner
- panel_olustur(**kwargs) -> Panel instance oluşturur

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- UI katmanı dışında bağımlılığı yoktur

SURUM: 5
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

import traceback
from typing import Any


class TumDosyaErisimPanelYoneticisi:
    def panel_sinifi(self):
        """
        Panel sınıfını lazy import ile döndürür.
        """
        try:
            from app.ui.tum_dosya_erisim_paketi.panel.panel import (
                TumDosyaErisimPaneli,
            )
            return TumDosyaErisimPaneli
        except Exception:
            print("[PANEL_YONETICI] Panel sınıfı yüklenemedi.")
            print(traceback.format_exc())
            raise

    def panel_olustur(self, **kwargs) -> Any:
        """
        Panel instance oluşturur.

        Beklenen parametreler:
        - services: ServicesYoneticisi instance
        - on_language_changed: dil değişim callback'i
        - on_status_changed: opsiyonel durum callback'i

        Dönüş:
        - TumDosyaErisimPaneli instance
        """
        try:
            panel_cls = self.panel_sinifi()

            if "services" not in kwargs:
                print("[PANEL_YONETICI] UYARI: services parametresi verilmedi.")

            return panel_cls(**kwargs)

        except Exception:
            print("[PANEL_YONETICI] Panel oluşturulamadı.")
            print(traceback.format_exc())
            raise

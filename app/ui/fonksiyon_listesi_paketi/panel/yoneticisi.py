# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/panel/yoneticisi.py

ROL:
- Panel alt paketine tek giriş noktası sağlamak
- FonksiyonListesi sınıfını merkezileştirmek
- Üst katmanın panel modülü detaylarını bilmesini engellemek
- Panel oluştururken üst katmandan gelen bağımlılıkları güvenli biçimde aşağı taşımak

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt panel modülü doğrudan dışarı açılmaz
- Fonksiyon listesi paneli üretimi burada toplanır
- Lazy import kullanır
- Fail-soft yaklaşım için tanılama logu bırakır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 2
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

import traceback


class PanelYoneticisi:
    def panel_sinifi(self):
        try:
            from app.ui.fonksiyon_listesi_paketi.panel.panel import FonksiyonListesi
            return FonksiyonListesi
        except Exception:
            print("[FONKSIYON_LISTESI_PANEL_YONETICI] FonksiyonListesi sınıfı yüklenemedi.")
            print(traceback.format_exc())
            raise

    def panel_olustur(
        self,
        on_select,
        on_error=None,
        services=None,
        **kwargs,
    ):
        try:
            sinif = self.panel_sinifi()
            return sinif(
                on_select=on_select,
                on_error=on_error,
                services=services,
                **kwargs,
            )
        except Exception:
            print("[FONKSIYON_LISTESI_PANEL_YONETICI] FonksiyonListesi oluşturulamadı.")
            print(traceback.format_exc())
            raise

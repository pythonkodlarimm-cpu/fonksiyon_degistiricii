# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/satir/yoneticisi.py

ROL:
- Satır (FonksiyonSatiri) bileşenine tek giriş noktası sağlamak
- Üst katmanın doğrudan satır sınıfını bilmesini engellemek
- Satır üretimini merkezileştirmek
- Services (dil sistemi) enjeksiyonunu yönetmek

MİMARİ:
- Üst katman sadece bu yöneticiyi kullanır
- Alt satır modülü doğrudan dışarı açılmaz
- Lazy import kullanılır
- Fail-soft yaklaşım uygulanır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur

SURUM: 2
TARIH: 2026-03-23
IMZA: FY.
"""

import traceback


class SatirYoneticisi:
    def satir_sinifi(self):
        try:
            from app.ui.fonksiyon_listesi_paketi.satir.satir import FonksiyonSatiri
            return FonksiyonSatiri
        except Exception:
            print("[FONKSIYON_LISTESI_SATIR_YONETICI] Satır sınıfı yüklenemedi.")
            print(traceback.format_exc())
            raise

    def satir_olustur(
        self,
        item,
        on_press_row,
        on_error=None,
        is_selected=False,
        services=None,
        **kwargs,
    ):
        try:
            sinif = self.satir_sinifi()
            return sinif(
                item=item,
                on_press_row=on_press_row,
                on_error=on_error,
                is_selected=is_selected,
                services=services,
                **kwargs,
            )
        except Exception:
            print("[FONKSIYON_LISTESI_SATIR_YONETICI] satir_olustur başarısız.")
            print(traceback.format_exc())
            return None

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/ortak/yoneticisi.py

ROL:
- Tüm dosya erişim paketi içindeki ortak modüllere tek giriş noktası sağlamak
- Ortak bileşen, durum mantığı ve dil popup başlatıcı erişimini merkezileştirmek
- Üst katmanın alt modül detaylarını bilmesini engellemek

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt modüller lazy import ile yüklenir
- Ortak yardımcılar burada toplanır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations


class TumDosyaErisimOrtakYoneticisi:
    # =========================================================
    # MODUL ERISIM
    # =========================================================
    def bilesenler_modulu(self):
        from app.ui.tum_dosya_erisim_paketi.ortak import bilesenler
        return bilesenler

    def durum_mantigi_modulu(self):
        from app.ui.tum_dosya_erisim_paketi.ortak import durum_mantigi
        return durum_mantigi

    def dil_popup_baslatici_modulu(self):
        from app.ui.tum_dosya_erisim_paketi.ortak import dil_popup_baslatici
        return dil_popup_baslatici

    # =========================================================
    # BILESENLER
    # =========================================================
    def tiklanabilir_icon_sinifi(self):
        return self.bilesenler_modulu().TiklanabilirIcon

    def animated_separator_sinifi(self):
        return self.bilesenler_modulu().AnimatedSeparator

    def start_icon_glow(self, widget, size_small_dp=36, size_big_dp=40, duration=0.60):
        return self.bilesenler_modulu().start_icon_glow(
            widget=widget,
            size_small_dp=size_small_dp,
            size_big_dp=size_big_dp,
            duration=duration,
        )

    # =========================================================
    # DURUM MANTIGI
    # =========================================================
    def erisim_durumu_getir(self, debug=None):
        return self.durum_mantigi_modulu().erisim_durumu_getir(debug=debug)

    def erisim_durumu_metni(self, durum) -> str:
        return self.durum_mantigi_modulu().erisim_durumu_metni(durum)

    def erisim_destekleniyor_mu(self) -> bool:
        return self.durum_mantigi_modulu().erisim_destekleniyor_mu()

    # =========================================================
    # DIL POPUP
    # =========================================================
    def dil_popup_baslat(self, *args, **kwargs):
        modul = self.dil_popup_baslatici_modulu()

        for fonksiyon_adi in (
            "open_language_popup",
            "show_language_popup",
            "launch_language_popup",
        ):
            fonksiyon = getattr(modul, fonksiyon_adi, None)
            if callable(fonksiyon):
                return fonksiyon(*args, **kwargs)

        raise AttributeError(
            "dil_popup_baslatici içinde uygun popup başlatıcı fonksiyon bulunamadı."
        )
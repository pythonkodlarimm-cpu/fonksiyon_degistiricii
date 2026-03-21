# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/bilesenler/yoneticisi.py

ROL:
- Bilesenler alt paketine tek giriş noktası sağlamak
- Editör bileşen sınıflarını merkezileştirmek
- Üst katmanın bilesen modülü detaylarını bilmesini engellemek

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt bileşen modülü doğrudan dışarı açılmaz
- Kod editörü, bilgi kutusu ve sade kod alanı erişimi burada toplanır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations


class BilesenlerYoneticisi:
    def kod_editoru_sinifi(self):
        from app.ui.editor_paketi.bilesenler.editor_bilesenleri import KodEditoru
        return KodEditoru

    def kod_paneli_sinifi(self):
        from app.ui.editor_paketi.bilesenler.editor_bilesenleri import KodPaneli
        return KodPaneli

    def bilgi_kutusu_sinifi(self):
        from app.ui.editor_paketi.bilesenler.editor_bilesenleri import BilgiKutusu
        return BilgiKutusu

    def sade_kod_alani_sinifi(self):
        from app.ui.editor_paketi.bilesenler.editor_bilesenleri import SadeKodAlani
        return SadeKodAlani

    def sade_kod_alani_olustur(self, **kwargs):
        sinif = self.sade_kod_alani_sinifi()
        return sinif(**kwargs)

    def bilgi_kutusu_olustur(self, **kwargs):
        sinif = self.bilgi_kutusu_sinifi()
        return sinif(**kwargs)
# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/bilesenler/yoneticisi.py

ROL:
- Bilesenler alt paketine tek giriş noktası sağlamak
- Editör bileşen sınıflarını merkezileştirmek
- Üst katmanın bilesen modülü detaylarını bilmesini engellemek
- Bileşen oluştururken üst katmandan gelen bağımlılıkları güvenli biçimde aşağı taşımak

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt bileşen modülü doğrudan dışarı açılmaz
- Kod editörü, bilgi kutusu ve sade kod alanı erişimi burada toplanır
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


class BilesenlerYoneticisi:
    def kod_editoru_sinifi(self):
        try:
            from app.ui.editor_paketi.bilesenler.editor_bilesenleri import KodEditoru
            return KodEditoru
        except Exception:
            print("[EDITOR_BILESEN_YONETICI] KodEditoru sınıfı yüklenemedi.")
            print(traceback.format_exc())
            raise

    def kod_paneli_sinifi(self):
        try:
            from app.ui.editor_paketi.bilesenler.editor_bilesenleri import KodPaneli
            return KodPaneli
        except Exception:
            print("[EDITOR_BILESEN_YONETICI] KodPaneli sınıfı yüklenemedi.")
            print(traceback.format_exc())
            raise

    def bilgi_kutusu_sinifi(self):
        try:
            from app.ui.editor_paketi.bilesenler.editor_bilesenleri import BilgiKutusu
            return BilgiKutusu
        except Exception:
            print("[EDITOR_BILESEN_YONETICI] BilgiKutusu sınıfı yüklenemedi.")
            print(traceback.format_exc())
            raise

    def sade_kod_alani_sinifi(self):
        try:
            from app.ui.editor_paketi.bilesenler.editor_bilesenleri import SadeKodAlani
            return SadeKodAlani
        except Exception:
            print("[EDITOR_BILESEN_YONETICI] SadeKodAlani sınıfı yüklenemedi.")
            print(traceback.format_exc())
            raise

    def sade_kod_alani_olustur(self, **kwargs):
        try:
            sinif = self.sade_kod_alani_sinifi()
            return sinif(**kwargs)
        except Exception:
            print("[EDITOR_BILESEN_YONETICI] SadeKodAlani oluşturulamadı.")
            print(traceback.format_exc())
            raise

    def bilgi_kutusu_olustur(self, **kwargs):
        try:
            sinif = self.bilgi_kutusu_sinifi()
            return sinif(**kwargs)
        except Exception:
            print("[EDITOR_BILESEN_YONETICI] BilgiKutusu oluşturulamadı.")
            print(traceback.format_exc())
            raise

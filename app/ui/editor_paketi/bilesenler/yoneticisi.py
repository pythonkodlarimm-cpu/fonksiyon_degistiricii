# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/bilesenler/yoneticisi.py

ROL:
- Bilesenler alt paketine tek giriş noktası sağlamak
- Editör bileşen sınıflarını merkezileştirmek
- Üst katmanın bilesen modülü detaylarını bilmesini engellemek
- Bileşen oluştururken üst katmandan gelen bağımlılıkları güvenli biçimde aşağı taşımak
- Yeni eklenen aksiyon araç çubuğu bileşenlerini de merkezi olarak sunmak

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt bileşen modülü doğrudan dışarı açılmaz
- Kod editörü, bilgi kutusu, sade kod alanı ve aksiyon çubuğu erişimi burada toplanır
- Lazy import + cache kullanır
- Fail-soft yaklaşım için tanılama logu bırakır
- Cache bozulursa kendini toparlayabilir

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 3
TARIH: 2026-03-26
IMZA: FY.
"""

from __future__ import annotations

import traceback


class BilesenlerYoneticisi:
    """
    Editör bileşenleri için merkezi erişim yöneticisi.
    """

    def __init__(self) -> None:
        self._cache = {}

    # =========================================================
    # INTERNAL
    # =========================================================
    def _get_class(self, key: str, loader):
        try:
            if key in self._cache:
                return self._cache[key]

            cls = loader()
            self._cache[key] = cls
            return cls

        except Exception:
            print(f"[EDITOR_BILESEN_YONETICI] {key} yüklenemedi.")
            print(traceback.format_exc())
            raise

    # =========================================================
    # SINIF ERIŞIMLERI
    # =========================================================
    def kod_editoru_sinifi(self):
        return self._get_class(
            "KodEditoru",
            lambda: __import__(
                "app.ui.editor_paketi.bilesenler.editor_bilesenleri",
                fromlist=["KodEditoru"],
            ).KodEditoru,
        )

    def kod_paneli_sinifi(self):
        return self._get_class(
            "KodPaneli",
            lambda: __import__(
                "app.ui.editor_paketi.bilesenler.editor_bilesenleri",
                fromlist=["KodPaneli"],
            ).KodPaneli,
        )

    def bilgi_kutusu_sinifi(self):
        return self._get_class(
            "BilgiKutusu",
            lambda: __import__(
                "app.ui.editor_paketi.bilesenler.editor_bilesenleri",
                fromlist=["BilgiKutusu"],
            ).BilgiKutusu,
        )

    def sade_kod_alani_sinifi(self):
        return self._get_class(
            "SadeKodAlani",
            lambda: __import__(
                "app.ui.editor_paketi.bilesenler.editor_bilesenleri",
                fromlist=["SadeKodAlani"],
            ).SadeKodAlani,
        )

    def aksiyon_ikon_butonu_sinifi(self):
        return self._get_class(
            "AksiyonIkonButonu",
            lambda: __import__(
                "app.ui.editor_paketi.bilesenler.editor_bilesenleri",
                fromlist=["AksiyonIkonButonu"],
            ).AksiyonIkonButonu,
        )

    def aksiyon_cubugu_sinifi(self):
        return self._get_class(
            "EditorAksiyonCubugu",
            lambda: __import__(
                "app.ui.editor_paketi.bilesenler.editor_bilesenleri",
                fromlist=["EditorAksiyonCubugu"],
            ).EditorAksiyonCubugu,
        )

    # =========================================================
    # OLUSTURUCULAR
    # =========================================================
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

    def aksiyon_cubugu_olustur(self, **kwargs):
        try:
            sinif = self.aksiyon_cubugu_sinifi()
            return sinif(**kwargs)
        except Exception:
            print("[EDITOR_BILESEN_YONETICI] EditorAksiyonCubugu oluşturulamadı.")
            print(traceback.format_exc())
            raise

    # =========================================================
    # CACHE KONTROL
    # =========================================================
    def cache_temizle(self):
        try:
            self._cache.clear()
        except Exception:
            pass

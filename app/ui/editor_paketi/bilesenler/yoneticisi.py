# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/bilesenler/yoneticisi.py

ROL:
- Bileşenler alt paketine tek giriş noktası sağlar
- Editör bileşen sınıflarını merkezileştirir
- Üst katmanın bileşen modülü detaylarını bilmesini engeller
- Bileşen oluştururken üst katmandan gelen bağımlılıkları güvenli biçimde aşağı taşır
- Aksiyon araç çubuğu gibi yeni bileşenleri merkezi olarak sunar

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt bileşen modülü doğrudan dışarı açılmaz
- Kod editörü, bilgi kutusu, sade kod alanı ve aksiyon çubuğu erişimi burada toplanır
- Lazy import + cache kullanır
- Fail-soft yaklaşım uygular

SURUM: 4
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations


class BilesenlerYoneticisi:
    """
    Editör bileşenleri için merkezi erişim yöneticisi.
    """

    MODUL_YOLU = "app.ui.editor_paketi.bilesenler.editor_bilesenleri"

    def __init__(self) -> None:
        self._sinif_cache: dict[str, object] = {}

    def cache_temizle(self):
        """
        Sınıf cache alanını temizler.
        """
        self._sinif_cache = {}

    def _sinif_yukle(self, sinif_adi: str):
        """
        Verilen sınıf adını lazy import ile yükler ve cache içinde tutar.

        Args:
            sinif_adi: Yüklenecek sınıf adı

        Returns:
            type | None
        """
        if sinif_adi in self._sinif_cache:
            return self._sinif_cache.get(sinif_adi)

        try:
            modul = __import__(self.MODUL_YOLU, fromlist=[sinif_adi])
        except Exception as exc:
            print(f"[EDITOR_BILESEN] Modül yüklenemedi: {self.MODUL_YOLU}")
            print(exc)
            self._sinif_cache.pop(sinif_adi, None)
            return None

        try:
            sinif = getattr(modul, sinif_adi, None)
        except Exception as exc:
            print(f"[EDITOR_BILESEN] Sınıf alınamadı: {sinif_adi}")
            print(exc)
            self._sinif_cache.pop(sinif_adi, None)
            return None

        if sinif is None:
            print(f"[EDITOR_BILESEN] Sınıf bulunamadı: {sinif_adi}")
            self._sinif_cache.pop(sinif_adi, None)
            return None

        self._sinif_cache[sinif_adi] = sinif
        return sinif

    def kod_editoru_sinifi(self):
        """
        KodEditoru sınıfını döndürür.
        """
        return self._sinif_yukle("KodEditoru")

    def kod_paneli_sinifi(self):
        """
        KodPaneli sınıfını döndürür.
        """
        return self._sinif_yukle("KodPaneli")

    def bilgi_kutusu_sinifi(self):
        """
        BilgiKutusu sınıfını döndürür.
        """
        return self._sinif_yukle("BilgiKutusu")

    def sade_kod_alani_sinifi(self):
        """
        SadeKodAlani sınıfını döndürür.
        """
        return self._sinif_yukle("SadeKodAlani")

    def aksiyon_ikon_butonu_sinifi(self):
        """
        AksiyonIkonButonu sınıfını döndürür.
        """
        return self._sinif_yukle("AksiyonIkonButonu")

    def aksiyon_cubugu_sinifi(self):
        """
        EditorAksiyonCubugu sınıfını döndürür.
        """
        return self._sinif_yukle("EditorAksiyonCubugu")

    def sade_kod_alani_olustur(self, **kwargs):
        """
        SadeKodAlani örneği oluşturur.
        """
        sinif = self.sade_kod_alani_sinifi()
        if sinif is None:
            return None

        try:
            return sinif(**kwargs)
        except Exception as exc:
            print("[EDITOR_BILESEN] SadeKodAlani oluşturulamadı.")
            print(exc)
            return None

    def bilgi_kutusu_olustur(self, **kwargs):
        """
        BilgiKutusu örneği oluşturur.
        """
        sinif = self.bilgi_kutusu_sinifi()
        if sinif is None:
            return None

        try:
            return sinif(**kwargs)
        except Exception as exc:
            print("[EDITOR_BILESEN] BilgiKutusu oluşturulamadı.")
            print(exc)
            return None

    def aksiyon_cubugu_olustur(self, **kwargs):
        """
        EditorAksiyonCubugu örneği oluşturur.
        """
        sinif = self.aksiyon_cubugu_sinifi()
        if sinif is None:
            return None

        try:
            return sinif(**kwargs)
        except Exception as exc:
            print("[EDITOR_BILESEN] EditorAksiyonCubugu oluşturulamadı.")
            print(exc)
            return None

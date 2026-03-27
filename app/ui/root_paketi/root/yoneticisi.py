# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/yonetici.py

ROL:
- RootWidget için merkezi erişim sağlar
- RootWidget sınıfını lazy import ile yükler
- Modül ve sınıf referansını cache içinde tutar
- Gerekirse RootWidget örneği oluşturur
- Fail-soft yaklaşım uygular

MİMARİ:
- Modül seviyesinde zorunlu import yapmaz
- İhtiyaç anında hedef modülü yükler
- Başarılı yükleme sonrası modül ve sınıf referansını saklar
- Root iç yapısına tek giriş noktası sağlar

GERÇEK DOSYA YOLU:
- app/ui/root_paketi/root/root.py

SURUM: 5
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations


class RootYoneticisi:
    """
    RootWidget için merkezi erişim yöneticisi.
    """

    MODUL_YOLU = "app.ui.root_paketi.root.root"
    SINIF_ADI = "RootWidget"

    def __init__(self) -> None:
        self._modul = None
        self._root_sinifi = None

    def cache_temizle(self) -> None:
        """
        Modül ve sınıf cache alanlarını temizler.
        """
        self._modul = None
        self._root_sinifi = None

    def _modul_yukle(self):
        """
        Hedef modülü lazy import ile yükler.

        Returns:
            module | None
        """
        if self._modul is not None:
            return self._modul

        try:
            modul = __import__(self.MODUL_YOLU, fromlist=[self.SINIF_ADI])
        except Exception as exc:
            print(f"[ROOT_YONETICI] Modül yüklenemedi: {self.MODUL_YOLU}")
            print(exc)
            self._modul = None
            return None

        if not hasattr(modul, self.SINIF_ADI):
            print(
                "[ROOT_YONETICI] "
                f"Beklenen sınıf bulunamadı: {self.MODUL_YOLU}.{self.SINIF_ADI}"
            )
            self._modul = None
            return None

        self._modul = modul
        return modul

    def _root_sinifini_yukle(self):
        """
        RootWidget sınıfını yükler.

        Returns:
            type | None
        """
        if self._root_sinifi is not None:
            return self._root_sinifi

        modul = self._modul_yukle()
        if modul is None:
            return None

        try:
            sinif = getattr(modul, self.SINIF_ADI, None)
        except Exception as exc:
            print(f"[ROOT_YONETICI] Sınıf alınamadı: {self.SINIF_ADI}")
            print(exc)
            self._root_sinifi = None
            return None

        if sinif is None:
            print(f"[ROOT_YONETICI] Sınıf bulunamadı: {self.SINIF_ADI}")
            self._root_sinifi = None
            return None

        self._root_sinifi = sinif
        return sinif

    def modul(self):
        """
        Root modül nesnesini döndürür.

        Returns:
            module | None
        """
        return self._modul_yukle()

    def root_sinifi(self):
        """
        RootWidget sınıfını döndürür.

        Returns:
            type | None
        """
        return self._root_sinifini_yukle()

    def root_olustur(self, *args, **kwargs):
        """
        RootWidget örneği oluşturmaya çalışır.

        Returns:
            object | None
        """
        sinif = self.root_sinifi()
        if sinif is None:
            return None

        try:
            return sinif(*args, **kwargs)
        except Exception as exc:
            print("[ROOT_YONETICI] Root örneği oluşturulamadı.")
            print(exc)
            return None

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_dosya/yoneticisi.py

ROL:
- Root dosya akışı katmanına tek giriş noktası sağlamak
- RootDosyaAkisiMixin erişimini merkezileştirmek
- Root paketi üst yöneticisinin bu katmana güvenli erişmesini sağlamak
- Android ve AAB ortamında tekrar eden import maliyetini azaltacak şekilde çalışmak

MİMARİ:
- Lazy import kullanır
- Alt modül detaylarını dış dünyaya sızdırmaz
- RootPaketiYoneticisi ile entegre çalışır
- Modül ve sınıf referanslarını cache içinde tutar
- Cache bozulursa kendini toparlayacak şekilde yeniden resolve yapabilir
- Fail-soft yaklaşım uygular

API UYUMLULUK:
- Android ve masaüstü ortamlarıyla uyumludur
- Doğrudan platform bağımlı çağrı içermez

SURUM: 4
TARIH: 2026-03-26
IMZA: FY.
"""

from __future__ import annotations

import traceback


class RootDosyaAkisiYoneticisi:
    """
    Root dosya akışı mixin sınıfına erişim sağlayan yönetici.

    Bu sınıfın görevi:
    - RootDosyaAkisiMixin sınıfını lazy import ile yüklemek
    - Root paketi üst katmanının alt dosya akışı modülünü doğrudan bilmesini engellemek
    - Modüler mimaride tek giriş noktası sunmaktır
    """

    modul_yolu = "app.ui.root_paketi.akisi_dosya.dosya_akisi"
    sinif_adi = "RootDosyaAkisiMixin"

    def __init__(self) -> None:
        self._cached_module = None
        self._cached_class = None

    # =========================================================
    # INTERNAL
    # =========================================================
    def _modul_cache_var_mi(self) -> bool:
        """
        Modül cache'inin dolu olup olmadığını kontrol eder.

        Returns:
            bool
        """
        try:
            return self._cached_module is not None
        except Exception:
            return False

    def _sinif_cache_var_mi(self) -> bool:
        """
        Sınıf cache'inin dolu olup olmadığını kontrol eder.

        Returns:
            bool
        """
        try:
            return self._cached_class is not None
        except Exception:
            return False

    def _modul_cache_temizle(self) -> None:
        """
        Modül cache'ini temizler.
        """
        try:
            self._cached_module = None
        except Exception:
            pass

    def _sinif_cache_temizle(self) -> None:
        """
        Sınıf cache'ini temizler.
        """
        try:
            self._cached_class = None
        except Exception:
            pass

    def cache_temizle(self) -> None:
        """
        Yönetici içindeki modül ve sınıf cache'lerini temizler.
        """
        self._sinif_cache_temizle()
        self._modul_cache_temizle()

    def _modul_gecerli_mi(self, module) -> bool:
        """
        Cache içindeki modülün beklenen sınıfı sağlayıp sağlamadığını kontrol eder.

        Args:
            module: Kontrol edilecek modül.

        Returns:
            bool
        """
        try:
            return module is not None and hasattr(module, self.sinif_adi)
        except Exception:
            return False

    def _sinif_gecerli_mi(self, cls) -> bool:
        """
        Cache içindeki sınıfın geçerli olup olmadığını kontrol eder.

        Args:
            cls: Kontrol edilecek sınıf.

        Returns:
            bool
        """
        try:
            return cls is not None and getattr(cls, "__name__", "") == self.sinif_adi
        except Exception:
            return False

    def _yukle_modul(self):
        """
        Hedef modülü lazy import + cache ile güvenli biçimde yükler.

        Returns:
            module | None
        """
        try:
            if self._modul_cache_var_mi() and self._modul_gecerli_mi(
                self._cached_module
            ):
                return self._cached_module
        except Exception:
            self._modul_cache_temizle()

        try:
            module = __import__(self.modul_yolu, fromlist=[self.sinif_adi])

            if not self._modul_gecerli_mi(module):
                print(
                    "[ROOT_DOSYA_AKISI_YONETICI] "
                    "Modül yüklendi ama beklenen sınıf görünmedi: "
                    f"{self.modul_yolu}.{self.sinif_adi}"
                )
                self._modul_cache_temizle()
                return None

            self._cached_module = module
            return module
        except Exception:
            print(
                "[ROOT_DOSYA_AKISI_YONETICI] "
                f"Modül yüklenemedi: {self.modul_yolu}"
            )
            print(traceback.format_exc())
            self._modul_cache_temizle()
            return None

    def _yukle_sinif(self):
        """
        Hedef mixin sınıfını lazy import + cache ile güvenli biçimde yükler.

        Returns:
            type | None
        """
        try:
            if self._sinif_cache_var_mi() and self._sinif_gecerli_mi(
                self._cached_class
            ):
                return self._cached_class
        except Exception:
            self._sinif_cache_temizle()

        module = self._yukle_modul()
        if module is None:
            return None

        try:
            cls = getattr(module, self.sinif_adi, None)

            if not self._sinif_gecerli_mi(cls):
                print(
                    "[ROOT_DOSYA_AKISI_YONETICI] "
                    f"Sınıf geçersiz: {self.sinif_adi}"
                )
                self._sinif_cache_temizle()
                return None

            self._cached_class = cls
            return cls
        except Exception:
            print(
                "[ROOT_DOSYA_AKISI_YONETICI] "
                f"Sınıf alınamadı: {self.sinif_adi}"
            )
            print(traceback.format_exc())
            self._sinif_cache_temizle()
            return None

    # =========================================================
    # PUBLIC
    # =========================================================
    def modul(self):
        """
        Root dosya akışı modülünü döndürür.

        Returns:
            module | None
        """
        return self._yukle_modul()

    def mixin_sinifi(self):
        """
        Root dosya akışı mixin sınıfını döndürür.

        Returns:
            type | None
        """
        return self._yukle_sinif()

    def sinif(self):
        """
        Geriye uyumlu kısa alias.

        Returns:
            type | None
        """
        return self._yukle_sinif()

    def ornek_olustur(self, *args, **kwargs):
        """
        Mixin sınıfı için örnek oluşturmaya çalışır.

        Returns:
            object | None
        """
        cls = self.mixin_sinifi()
        if cls is None:
            return None

        try:
            return cls(*args, **kwargs)
        except Exception:
            print(
                "[ROOT_DOSYA_AKISI_YONETICI] "
                "Mixin örneği oluşturulamadı."
            )
            print(traceback.format_exc())
            return None

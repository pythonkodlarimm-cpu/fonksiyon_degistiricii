# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/akisi_secim/yoneticisi.py

ROL:
- Root seçim akışı katmanına tek giriş noktası sağlamak
- RootSecimAkisiMixin erişimini merkezileştirmek
- Üst yönetici katmanının bu modüle güvenli erişmesini sağlamak
- Android ve AAB ortamında tekrar eden import maliyetini azaltacak şekilde çalışmak

MİMARİ:
- Lazy import kullanır
- Modül ve sınıf referanslarını cache içinde tutar
- Alt modül detaylarını dış dünyaya sızdırmaz
- Fail-soft yaklaşım uygular
- Cache bozulursa kendini toparlayacak şekilde yeniden resolve yapabilir

API UYUMLULUK:
- Android ve masaüstü ortamlarıyla uyumludur
- Doğrudan platform bağımlı çağrı içermez

SURUM: 3
TARIH: 2026-03-26
IMZA: FY.
"""

from __future__ import annotations

import traceback


class RootSecimAkisiYoneticisi:
    """
    Root seçim akışı mixin sınıfına erişim sağlayan yönetici.
    """

    modul_yolu = "app.ui.root_paketi.akisi_secim.secim_akisi"
    sinif_adi = "RootSecimAkisiMixin"

    def __init__(self) -> None:
        self._cached_module = None
        self._cached_class = None

    # =========================================================
    # CACHE
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

    # =========================================================
    # VALIDATION
    # =========================================================
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

    # =========================================================
    # LOAD
    # =========================================================
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
                    "[ROOT_SECIM_AKISI_YONETICI] "
                    "Modül yüklendi ama beklenen sınıf görünmedi: "
                    f"{self.modul_yolu}.{self.sinif_adi}"
                )
                self._modul_cache_temizle()
                return None

            self._cached_module = module
            return module
        except Exception:
            print(
                "[ROOT_SECIM_AKISI_YONETICI] "
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
                    "[ROOT_SECIM_AKISI_YONETICI] "
                    f"Sınıf geçersiz: {self.sinif_adi}"
                )
                self._sinif_cache_temizle()
                return None

            self._cached_class = cls
            return cls
        except Exception:
            print(
                "[ROOT_SECIM_AKISI_YONETICI] "
                f"Sınıf resolve edilemedi: {self.sinif_adi}"
            )
            print(traceback.format_exc())
            self._sinif_cache_temizle()
            return None

    # =========================================================
    # PUBLIC
    # =========================================================
    def modul(self):
        """
        Root seçim akışı modülünü döndürür.

        Returns:
            module | None
        """
        return self._yukle_modul()

    def mixin_sinifi(self):
        """
        RootSecimAkisiMixin sınıfını döndürür.

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
                "[ROOT_SECIM_AKISI_YONETICI] "
                "Mixin örneği oluşturulamadı."
            )
            print(traceback.format_exc())
            return None

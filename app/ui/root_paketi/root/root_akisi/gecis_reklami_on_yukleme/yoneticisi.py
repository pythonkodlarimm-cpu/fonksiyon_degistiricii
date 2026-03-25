# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/gecis_reklami_on_yukleme/yonetici.py

ROL:
- Geçiş reklamı ön yükleme akışı için tek noktadan erişim sağlayan yönetici sınıfıdır
- Root geçiş reklamı ön yükleme mixin sınıfını güvenli biçimde döndürür
- Lazy import mantığıyla modülü ihtiyaç halinde yükler
- İlk yüklenen modül ve sınıf referanslarını cache içinde tutar
- Fail-soft yaklaşım uygular; hata durumunda çökmez, log basar

MİMARİ:
- Yönetici sınıfı modül seviyesinde zorunlu import yapmaz
- __import__ ile hedef modül çalışma anında yüklenir
- Modül ve sınıf referansları instance cache içinde saklanır
- Root katmanı isterse bu yönetici üzerinden mixin sınıfına erişebilir
- Paket erişim yapısı ileride genişletilebilir

KULLANIM:
- yonetici = RootGecisReklamiOnYuklemeYoneticisi()
- mixin_sinifi = yonetici.mixin_sinifi()
- paket = yonetici.modul()

NOT:
- Bu dosya widget üretmez
- Bu dosya root örneği oluşturmaz
- Sadece ilgili modül ve sınıfa merkezi erişim sağlar
- İlk başarılı import sonrası tekrar import maliyeti oluşmaz

SURUM: 2
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import traceback


class RootGecisReklamiOnYuklemeYoneticisi:
    """
    Geçiş reklamı ön yükleme modülü için merkezi erişim yöneticisi.
    """

    modul_yolu = (
        "app.ui.root_paketi.root.root_akisi.gecis_reklami_on_yukleme."
        "gecis_reklami_on_yukleme"
    )
    sinif_adi = "RootGecisReklamiOnYuklemeMixin"

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

    def _yukle_modul(self):
        """
        Hedef modülü lazy import + cache ile güvenli biçimde yükler.

        Returns:
            module | None
        """
        try:
            if self._modul_cache_var_mi():
                return self._cached_module
        except Exception:
            self._modul_cache_temizle()

        try:
            module = __import__(self.modul_yolu, fromlist=[self.sinif_adi])
            self._cached_module = module
            return module
        except Exception:
            print(
                "[ROOT_GECIS_REKLAMI_ON_YUKLEME] "
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
            if self._sinif_cache_var_mi():
                return self._cached_class
        except Exception:
            self._sinif_cache_temizle()

        module = self._yukle_modul()
        if module is None:
            return None

        try:
            cls = getattr(module, self.sinif_adi, None)
            if cls is None:
                print(
                    "[ROOT_GECIS_REKLAMI_ON_YUKLEME] "
                    f"Sınıf bulunamadı: {self.sinif_adi}"
                )
                self._sinif_cache_temizle()
                return None

            self._cached_class = cls
            return cls
        except Exception:
            print(
                "[ROOT_GECIS_REKLAMI_ON_YUKLEME] "
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
        Geçiş reklamı ön yükleme modül nesnesini döndürür.

        Returns:
            module | None
        """
        return self._yukle_modul()

    def mixin_sinifi(self):
        """
        RootGecisReklamiOnYuklemeMixin sınıfını döndürür.

        Returns:
            type | None
        """
        return self._yukle_sinif()

    def ornek_olustur(self, *args, **kwargs):
        """
        Mixin sınıfı için örnek oluşturmaya çalışır.

        Not:
        - Mixin yapılar normalde tek başına instantiate edilmez.
        - Bu metod daha çok test / introspection amaçlıdır.

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
                "[ROOT_GECIS_REKLAMI_ON_YUKLEME] "
                "Mixin örneği oluşturulamadı."
            )
            print(traceback.format_exc())
            return None
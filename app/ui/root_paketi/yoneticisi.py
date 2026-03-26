# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/yoneticisi.py

ROL:
- Root katmanı için tek noktadan erişim sağlayan yönetici sınıfıdır
- RootWidget sınıfını güvenli biçimde döndürür
- Lazy import mantığıyla modülü ihtiyaç halinde yükler
- İlk yüklenen modül ve sınıf referanslarını cache içinde tutar
- Gerekirse RootWidget örneği oluşturur
- Fail-soft yaklaşım uygular; hata durumunda çökmez, log basar
- Android ve AAB ortamında tekrar eden import maliyetini azaltacak şekilde çalışır

MİMARİ:
- Yönetici sınıfı modül seviyesinde zorunlu import yapmaz
- __import__ ile hedef modül çalışma anında yüklenir
- Modül ve sınıf referansları instance cache içinde saklanır
- Paket erişim yapısı ileride genişletilebilir
- Root modülü gerçek klasör yapısına göre root/root.py içinden yüklenir
- Cache bozulursa kendini toparlayacak şekilde yeniden resolve yapabilir
- Üst yönetici katmanı olarak root iç yöneticisi ile aynı import yolunu hedefler
- Geliştirme sırasında hot-reload veya kısmi dosya değişimlerinde cache temizlenebilir

GERÇEK DOSYA YOLU:
- app/ui/root_paketi/root/root.py

KULLANIM:
- yonetici = RootYoneticisi()
- root_sinifi = yonetici.root_sinifi()
- root_widget = yonetici.root_olustur()

NOT:
- Bu dosya doğrudan UI çizmez
- Root örneği oluşturmayı kolaylaştırır
- İlk başarılı import sonrası tekrar import maliyeti oluşmaz
- APK build sırasında path hatası yaşamamak için modul_yolu kesin olarak
  app.ui.root_paketi.root.root şeklinde ayarlanmıştır

SURUM: 7
TARIH: 2026-03-26
IMZA: FY.
"""

from __future__ import annotations

import traceback


class RootYoneticisi:
    """
    Root modülü için merkezi erişim yöneticisi.
    """

    modul_yolu = "app.ui.root_paketi.root.root"
    sinif_adi = "RootWidget"

    def __init__(self) -> None:
        self._cached_module = None
        self._cached_class = None

    # =========================================================
    # CACHE DURUM KONTROL
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

    # =========================================================
    # CACHE TEMIZLEME
    # =========================================================
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
    # MODUL YUKLEME
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
                    "[ROOT_YONETICISI] Modül yüklendi ama beklenen sınıf görünmedi: "
                    f"{self.modul_yolu}.{self.sinif_adi}"
                )
                self._modul_cache_temizle()
                return None

            self._cached_module = module
            return module
        except Exception:
            print(f"[ROOT_YONETICISI] Modül yüklenemedi: {self.modul_yolu}")
            print(traceback.format_exc())
            self._modul_cache_temizle()
            return None

    # =========================================================
    # SINIF YUKLEME
    # =========================================================
    def _yukle_sinif(self):
        """
        Hedef root sınıfını lazy import + cache ile güvenli biçimde yükler.

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
                print(f"[ROOT_YONETICISI] Sınıf geçersiz: {self.sinif_adi}")
                self._sinif_cache_temizle()
                return None

            self._cached_class = cls
            return cls
        except Exception:
            print(f"[ROOT_YONETICISI] Sınıf alınamadı: {self.sinif_adi}")
            print(traceback.format_exc())
            self._sinif_cache_temizle()
            return None

    # =========================================================
    # PUBLIC
    # =========================================================
    def modul(self):
        """
        Root modül nesnesini döndürür.

        Returns:
            module | None
        """
        return self._yukle_modul()

    def root_sinifi(self):
        """
        RootWidget sınıfını döndürür.

        Returns:
            type | None
        """
        return self._yukle_sinif()

    def mixin_sinifi(self):
        """
        Geriye uyumlu kullanım için RootWidget sınıfını döndürür.

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

    def root_olustur(self, *args, **kwargs):
        """
        RootWidget örneği oluşturmaya çalışır.

        Returns:
            object | None
        """
        cls = self.root_sinifi()
        if cls is None:
            return None

        try:
            return cls(*args, **kwargs)
        except Exception:
            print("[ROOT_YONETICISI] Root örneği oluşturulamadı.")
            print(traceback.format_exc())
            return None

    def ornek_olustur(self, *args, **kwargs):
        """
        Geriye uyumlu kullanım için RootWidget örneği oluşturmaya çalışır.

        Returns:
            object | None
        """
        return self.root_olustur(*args, **kwargs)

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/yoneticisi.py

ROL:
- root klasörü içindeki RootWidget için tek noktadan erişim sağlayan yönetici sınıfıdır
- RootWidget sınıfını güvenli biçimde döndürür
- Lazy import mantığıyla modülü ihtiyaç halinde yükler
- İlk yüklenen modül ve sınıf referanslarını cache içinde tutar
- Gerekirse RootWidget örneği oluşturur
- Fail-soft yaklaşım uygular; hata durumunda çökmez, log basar

MİMARİ:
- Yönetici sınıfı modül seviyesinde zorunlu import yapmaz
- __import__ ile hedef modül çalışma anında yüklenir
- Modül ve sınıf referansları instance cache içinde saklanır
- root paketinin kendi iç yapısı için kullanılır
- Gerçek dosya yolu root/root.py olduğu için modul_yolu buna göre ayarlanmıştır

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

SURUM: 1
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import traceback


class RootYoneticisi:
    """
    root klasörü içindeki RootWidget için merkezi erişim yöneticisi.
    """

    modul_yolu = "app.ui.root_paketi.root.root"
    sinif_adi = "RootWidget"

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
            print(f"[ROOT_IC_YONETICI] Modül yüklenemedi: {self.modul_yolu}")
            print(traceback.format_exc())
            self._modul_cache_temizle()
            return None

    def _yukle_sinif(self):
        """
        Hedef root sınıfını lazy import + cache ile güvenli biçimde yükler.

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
                print(f"[ROOT_IC_YONETICI] Sınıf bulunamadı: {self.sinif_adi}")
                self._sinif_cache_temizle()
                return None

            self._cached_class = cls
            return cls
        except Exception:
            print(f"[ROOT_IC_YONETICI] Sınıf alınamadı: {self.sinif_adi}")
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
            print("[ROOT_IC_YONETICI] Root örneği oluşturulamadı.")
            print(traceback.format_exc())
            return None

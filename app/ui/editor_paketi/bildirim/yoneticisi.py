# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/bildirim/yoneticisi.py

ROL:
- Bildirim alt paketine tek giriş noktası sağlamak
- Editör içi aksiyon bildirimi bileşenini merkezileştirmek
- Üst katmanın bildirim modülü detaylarını bilmesini engellemek
- Bildirim oluştururken üst katmandan gelen bağımlılıkları güvenli biçimde aşağı taşımak
- Android ve AAB ortamında tekrar eden import maliyetini azaltacak şekilde çalışmak

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt bildirim modülü doğrudan dışarı açılmaz
- Inline aksiyon bildirimi üretimi burada toplanır
- Lazy import + cache kullanır
- Fail-soft yaklaşım için tanılama logu bırakır
- Cache bozulursa kendini toparlayacak şekilde yeniden resolve yapabilir

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


class BildirimYoneticisi:
    """
    Editör içi bildirim bileşenleri için merkezi erişim yöneticisi.
    """

    modul_yolu = "app.ui.editor_paketi.bildirim.editor_bildirimleri"
    sinif_adi = "EditorAksiyonBildirimi"

    def __init__(self) -> None:
        self._cached_module = None
        self._cached_class = None

    # =========================================================
    # CACHE
    # =========================================================
    def _modul_cache_var_mi(self) -> bool:
        try:
            return self._cached_module is not None
        except Exception:
            return False

    def _sinif_cache_var_mi(self) -> bool:
        try:
            return self._cached_class is not None
        except Exception:
            return False

    def _modul_cache_temizle(self) -> None:
        try:
            self._cached_module = None
        except Exception:
            pass

    def _sinif_cache_temizle(self) -> None:
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
        try:
            return module is not None and hasattr(module, self.sinif_adi)
        except Exception:
            return False

    def _sinif_gecerli_mi(self, cls) -> bool:
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
                    "[EDITOR_BILDIRIM_YONETICI] "
                    "Modül yüklendi ama beklenen sınıf görünmedi: "
                    f"{self.modul_yolu}.{self.sinif_adi}"
                )
                self._modul_cache_temizle()
                return None

            self._cached_module = module
            return module

        except Exception:
            print(
                "[EDITOR_BILDIRIM_YONETICI] "
                f"Modül yüklenemedi: {self.modul_yolu}"
            )
            print(traceback.format_exc())
            self._modul_cache_temizle()
            return None

    def _yukle_sinif(self):
        """
        Hedef bildirim sınıfını lazy import + cache ile güvenli biçimde yükler.

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
                    "[EDITOR_BILDIRIM_YONETICI] "
                    f"Sınıf geçersiz veya bulunamadı: {self.sinif_adi}"
                )
                self._sinif_cache_temizle()
                return None

            self._cached_class = cls
            return cls

        except Exception:
            print(
                "[EDITOR_BILDIRIM_YONETICI] "
                f"Sınıf yüklenemedi: {self.sinif_adi}"
            )
            print(traceback.format_exc())
            self._sinif_cache_temizle()
            return None

    # =========================================================
    # PUBLIC
    # =========================================================
    def modul(self):
        """
        Bildirim modülünü döndürür.

        Returns:
            module | None
        """
        return self._yukle_modul()

    def bildirim_sinifi(self):
        """
        EditorAksiyonBildirimi sınıfını döndürür.

        Returns:
            type | None
        """
        return self._yukle_sinif()

    def mixin_sinifi(self):
        """
        Geriye uyumlu kullanım için EditorAksiyonBildirimi sınıfını döndürür.

        Returns:
            type | None
        """
        return self._yukle_sinif()

    def bildirim_olustur(self, **kwargs):
        """
        Bildirim bileşeni örneği oluşturmaya çalışır.

        Returns:
            object | None
        """
        cls = self.bildirim_sinifi()
        if cls is None:
            return None

        try:
            return cls(**kwargs)
        except Exception:
            print("[EDITOR_BILDIRIM_YONETICI] Bildirim bileşeni oluşturulamadı.")
            print(traceback.format_exc())
            return None

    def ornek_olustur(self, **kwargs):
        """
        Geriye uyumlu kullanım için bildirim bileşeni örneği oluşturur.

        Returns:
            object | None
        """
        return self.bildirim_olustur(**kwargs)

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/bildirim/yoneticisi.py

ROL:
- Bildirim alt paketine tek giriş noktası sağlar
- Editör içi aksiyon bildirimi bileşenini merkezileştirir
- Üst katmanın bildirim modülü detaylarını bilmesini engeller
- Bildirim oluştururken üst katmandan gelen bağımlılıkları güvenli biçimde aşağı taşır
- Android ve AAB ortamında tekrar eden import maliyetini azaltacak şekilde çalışır

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt bildirim modülü doğrudan dışarı açılmaz
- Inline aksiyon bildirimi üretimi burada toplanır
- Lazy import + cache kullanır
- Fail-soft yaklaşım uygular

SURUM: 4
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations


class BildirimYoneticisi:
    """
    Editör içi bildirim bileşenleri için merkezi erişim yöneticisi.
    """

    MODUL_YOLU = "app.ui.editor_paketi.bildirim.editor_bildirimleri"
    SINIF_ADI = "EditorAksiyonBildirimi"

    def __init__(self) -> None:
        self._modul = None
        self._bildirim_sinifi = None

    def cache_temizle(self) -> None:
        """
        Modül ve sınıf cache alanlarını temizler.
        """
        self._modul = None
        self._bildirim_sinifi = None

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
            print(f"[EDITOR_BILDIRIM] Modül yüklenemedi: {self.MODUL_YOLU}")
            print(exc)
            self._modul = None
            return None

        if not hasattr(modul, self.SINIF_ADI):
            print(
                "[EDITOR_BILDIRIM] "
                f"Beklenen sınıf bulunamadı: {self.MODUL_YOLU}.{self.SINIF_ADI}"
            )
            self._modul = None
            return None

        self._modul = modul
        return modul

    def _bildirim_sinifini_yukle(self):
        """
        EditorAksiyonBildirimi sınıfını yükler.

        Returns:
            type | None
        """
        if self._bildirim_sinifi is not None:
            return self._bildirim_sinifi

        modul = self._modul_yukle()
        if modul is None:
            return None

        try:
            sinif = getattr(modul, self.SINIF_ADI, None)
        except Exception as exc:
            print(f"[EDITOR_BILDIRIM] Sınıf alınamadı: {self.SINIF_ADI}")
            print(exc)
            self._bildirim_sinifi = None
            return None

        if sinif is None:
            print(f"[EDITOR_BILDIRIM] Sınıf bulunamadı: {self.SINIF_ADI}")
            self._bildirim_sinifi = None
            return None

        self._bildirim_sinifi = sinif
        return sinif

    def modul(self):
        """
        Bildirim modülünü döndürür.

        Returns:
            module | None
        """
        return self._modul_yukle()

    def bildirim_sinifi(self):
        """
        EditorAksiyonBildirimi sınıfını döndürür.

        Returns:
            type | None
        """
        return self._bildirim_sinifini_yukle()

    def bildirim_olustur(self, **kwargs):
        """
        Bildirim bileşeni örneği oluşturmaya çalışır.

        Returns:
            object | None
        """
        sinif = self.bildirim_sinifi()
        if sinif is None:
            return None

        try:
            return sinif(**kwargs)
        except Exception as exc:
            print("[EDITOR_BILDIRIM] Bildirim bileşeni oluşturulamadı.")
            print(exc)
            return None

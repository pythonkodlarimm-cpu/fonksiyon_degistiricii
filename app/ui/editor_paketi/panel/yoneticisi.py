# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/panel/yoneticisi.py

ROL:
- Panel alt paketine tek giriş noktası sağlar
- EditorPaneli sınıfını merkezileştirir
- Üst katmanın panel modülü detaylarını bilmesini engeller
- Panel oluşturma sırasında üst katmandan gelen bağımlılıkları güvenli biçimde aşağı taşır
- Android ve AAB ortamında tekrar eden import maliyetini azaltacak şekilde çalışır

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt panel modülü doğrudan dışarı açılmaz
- EditorPaneli üretimi burada toplanır
- Lazy import + cache kullanır
- Fail-soft yaklaşım uygular

SURUM: 4
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations


class PanelYoneticisi:
    """
    EditorPaneli için merkezi erişim yöneticisi.
    """

    MODUL_YOLU = "app.ui.editor_paketi.panel.editor_paneli"
    SINIF_ADI = "EditorPaneli"

    def __init__(self) -> None:
        self._modul = None
        self._panel_sinifi = None

    def cache_temizle(self) -> None:
        """
        Modül ve sınıf cache alanlarını temizler.
        """
        self._modul = None
        self._panel_sinifi = None

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
            print(f"[EDITOR_PANEL] Modül yüklenemedi: {self.MODUL_YOLU}")
            print(exc)
            self._modul = None
            return None

        if not hasattr(modul, self.SINIF_ADI):
            print(
                "[EDITOR_PANEL] "
                f"Beklenen sınıf bulunamadı: {self.MODUL_YOLU}.{self.SINIF_ADI}"
            )
            self._modul = None
            return None

        self._modul = modul
        return modul

    def _panel_sinifini_yukle(self):
        """
        EditorPaneli sınıfını yükler.

        Returns:
            type | None
        """
        if self._panel_sinifi is not None:
            return self._panel_sinifi

        modul = self._modul_yukle()
        if modul is None:
            return None

        try:
            sinif = getattr(modul, self.SINIF_ADI, None)
        except Exception as exc:
            print(f"[EDITOR_PANEL] Sınıf alınamadı: {self.SINIF_ADI}")
            print(exc)
            self._panel_sinifi = None
            return None

        if sinif is None:
            print(f"[EDITOR_PANEL] Sınıf bulunamadı: {self.SINIF_ADI}")
            self._panel_sinifi = None
            return None

        self._panel_sinifi = sinif
        return sinif

    def modul(self):
        """
        Panel modülünü döndürür.

        Returns:
            module | None
        """
        return self._modul_yukle()

    def panel_sinifi(self):
        """
        EditorPaneli sınıfını döndürür.

        Returns:
            type | None
        """
        return self._panel_sinifini_yukle()

    def panel_olustur(self, **kwargs):
        """
        EditorPaneli örneği oluşturmaya çalışır.

        Returns:
            object | None
        """
        sinif = self.panel_sinifi()
        if sinif is None:
            return None

        try:
            return sinif(**kwargs)
        except Exception as exc:
            print("[EDITOR_PANEL] EditorPaneli oluşturulamadı.")
            print(exc)
            return None

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/panel/yoneticisi.py

ROL:
- Tüm dosya erişim panel bileşenine tek giriş noktası sağlar
- Panel sınıfını lazy import ile yükler
- Üst katmanın panel implementasyon detaylarını bilmesini engeller
- Panel oluştururken services ve callback bağımlılıklarını güvenli şekilde aşağı katmana geçirir
- Lazy import ve cache ile tekrar eden panel erişim maliyetini azaltır

MİMARİ:
- Lazy import kullanır
- UI bileşenini doğrudan expose etmez, yönetici üzerinden verir
- Panel oluşturma ve sınıf erişimi ayrılmıştır
- Dil değişimi gibi üst katman callback'leri **kwargs ile panele aktarılır
- Fail-soft yaklaşım: hata durumunda tanılama logu basar
- Panel sınıfı cache içinde tutulur
- Root tarafından verilen ortak services instance'ı doğrudan panel alt katmanına aktarılır

KULLANIM:
- panel_sinifi() -> Panel class döner
- panel_olustur(**kwargs) -> Panel instance oluşturur

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- UI katmanı dışında bağımlılığı yoktur

SURUM: 6
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import traceback
from typing import Any


class TumDosyaErisimPanelYoneticisi:
    def __init__(self) -> None:
        self._cached_panel_class = None

    # =========================================================
    # INTERNAL
    # =========================================================
    def _debug(self, message: str) -> None:
        try:
            print(f"[PANEL_YONETICI] {message}")
        except Exception:
            pass

    def _panel_sinif_cache_var_mi(self) -> bool:
        try:
            return self._cached_panel_class is not None
        except Exception:
            return False

    def _panel_sinif_cache_temizle(self) -> None:
        try:
            self._cached_panel_class = None
        except Exception:
            pass

    def cache_temizle(self) -> None:
        """
        Yönetici içindeki panel sınıf cache'ini temizler.
        """
        self._panel_sinif_cache_temizle()

    def _panel_sinifi_gecerli_mi(self, cls) -> bool:
        try:
            return cls is not None and getattr(cls, "__name__", "") == "TumDosyaErisimPaneli"
        except Exception:
            return False

    # =========================================================
    # PUBLIC
    # =========================================================
    def panel_sinifi(self):
        """
        Panel sınıfını lazy import + cache ile döndürür.
        """
        try:
            if self._panel_sinif_cache_var_mi() and self._panel_sinifi_gecerli_mi(
                self._cached_panel_class
            ):
                return self._cached_panel_class
        except Exception:
            self._panel_sinif_cache_temizle()

        try:
            from app.ui.tum_dosya_erisim_paketi.panel.panel import (
                TumDosyaErisimPaneli,
            )

            if not self._panel_sinifi_gecerli_mi(TumDosyaErisimPaneli):
                self._debug("Panel sınıfı yüklendi ama beklenen sınıf doğrulanamadı.")
                self._panel_sinif_cache_temizle()
                return None

            self._cached_panel_class = TumDosyaErisimPaneli
            return TumDosyaErisimPaneli
        except Exception:
            self._debug("Panel sınıfı yüklenemedi.")
            self._debug(traceback.format_exc())
            self._panel_sinif_cache_temizle()
            return None

    def panel_olustur(self, **kwargs) -> Any:
        """
        Panel instance oluşturur.

        Beklenen parametreler:
        - services: ServicesYoneticisi instance
        - on_language_changed: dil değişim callback'i
        - on_status_changed: opsiyonel durum callback'i

        Dönüş:
        - TumDosyaErisimPaneli instance
        """
        try:
            panel_cls = self.panel_sinifi()
            if panel_cls is None:
                return None

            if "services" not in kwargs:
                self._debug("UYARI: services parametresi verilmedi.")

            return panel_cls(**kwargs)

        except Exception:
            self._debug("Panel oluşturulamadı.")
            self._debug(traceback.format_exc())
            return None

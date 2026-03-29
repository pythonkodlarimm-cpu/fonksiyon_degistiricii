# -*- coding: utf-8 -*-
"""
DOSYA: app/services/ayarlar_servisi.py

ROL:
- Uygulama genel ayarlarını yönetir
- Developer mode dahil tüm config değerlerini saklar ve sağlar
- JSON tabanlı kalıcı (persist) ayar sistemi sunar

ÖZELLİKLER:
- Developer mode toggle
- Kalıcı kayıt (assets dışı güvenli path)
- Deterministik okuma/yazma
- Tek dosya config yönetimi
- Bozuk dosya durumunda self-heal (reset)

MİMARİ:
- Services katmanıdır
- UI katmanını bilmez
- Tek instance üzerinden çalışır (ServisYoneticisi cache)
- IO işlemleri kontrollüdür
- Geriye uyumluluk yok (temiz config)

DOSYA YAPISI:
{
  "developer_mode": false
}

KAYIT KONUMU:
- Android: /storage/emulated/0/<app>/ayarlar.json
- Desktop: proje kökü / app_data / ayarlar.json

SURUM: 1
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class AyarlarServisiHatasi(Exception):
    pass


class AyarlarServisi:
    """
    Uygulama ayarlarını yöneten servis.
    """

    __slots__ = ("_path", "_data")

    def __init__(self) -> None:
        self._path = self._ayar_dosya_yolu()
        self._data: dict[str, Any] = {}
        self._yukle()

    # =========================================================
    # PATH
    # =========================================================
    def _ayar_dosya_yolu(self) -> Path:
        try:
            base = Path("/storage/emulated/0/fy_app")
            base.mkdir(parents=True, exist_ok=True)
            return base / "ayarlar.json"
        except Exception:
            base = Path(__file__).resolve().parents[2] / "app_data"
            base.mkdir(parents=True, exist_ok=True)
            return base / "ayarlar.json"

    # =========================================================
    # LOAD / SAVE
    # =========================================================
    def _yukle(self) -> None:
        if not self._path.exists():
            self._data = self._varsayilan()
            self._kaydet()
            return

        try:
            raw = self._path.read_text(encoding="utf-8")
            self._data = json.loads(raw)
        except Exception:
            # bozulmuş dosya → reset
            self._data = self._varsayilan()
            self._kaydet()

    def _kaydet(self) -> None:
        try:
            text = json.dumps(self._data, ensure_ascii=False, indent=2)
            self._path.write_text(text, encoding="utf-8")
        except Exception as e:
            raise AyarlarServisiHatasi(f"Ayarlar kaydedilemedi: {e}")

    def _varsayilan(self) -> dict[str, Any]:
        return {
            "developer_mode": False,
        }

    # =========================================================
    # PUBLIC API
    # =========================================================
    def developer_mode_aktif_mi(self) -> bool:
        """
        Developer mode aktif mi kontrol eder.
        """
        return bool(self._data.get("developer_mode", False))

    def developer_mode_ayarla(self, durum: bool) -> None:
        """
        Developer mode aç/kapat.
        """
        self._data["developer_mode"] = bool(durum)
        self._kaydet()

    def toggle_developer_mode(self) -> bool:
        """
        Developer mode toggle eder ve yeni değeri döner.
        """
        yeni = not self.developer_mode_aktif_mi()
        self.developer_mode_ayarla(yeni)
        return yeni

    def tum_ayarlar(self) -> dict[str, Any]:
        """
        Tüm ayarları döndürür (readonly amaçlı).
        """
        return dict(self._data)
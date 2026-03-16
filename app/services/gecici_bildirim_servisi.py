# -*- coding: utf-8 -*-
"""
DOSYA: app/services/gecici_bildirim_servisi.py

ROL:
- Geçici bildirim gösterme akışını merkezi olarak yönetir
- UI katmanına doğrudan bağımlı iş mantığını tek yerde toplar
- Aktif bildirim katmanı ile konuşur
- Göster / gizle / hazır mı gibi akışları kontrol eder

MİMARİ:
- Widget içermez
- Sadece kayıtlı bildirim katmanına komut verir
- Root katmanı başlangıçta register eder
- Diğer UI parçaları servis üzerinden bildirim tetikler

SURUM: 1
TARIH: 2026-03-16
IMZA: FY.
"""

from __future__ import annotations


class GeciciBildirimServisi:
    def __init__(self):
        self._layer = None

    def register_layer(self, layer) -> None:
        self._layer = layer

    def unregister_layer(self) -> None:
        self._layer = None

    def has_layer(self) -> bool:
        return self._layer is not None

    def show(self, text: str, icon_name: str = "", duration: float = 2.4) -> bool:
        if self._layer is None:
            return False

        try:
            self._layer.show(
                text=str(text or ""),
                icon_name=str(icon_name or ""),
                duration=float(duration or 2.4),
            )
            return True
        except Exception:
            return False

    def hide(self) -> bool:
        if self._layer is None:
            return False

        try:
            self._layer.hide()
            return True
        except Exception:
            return False

    def hide_immediately(self) -> bool:
        if self._layer is None:
            return False

        try:
            self._layer.hide_immediately()
            return True
        except Exception:
            return False


gecici_bildirim_servisi = GeciciBildirimServisi()
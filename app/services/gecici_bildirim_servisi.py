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

API UYUMLULUK DEĞERLENDİRMESİ:
- Bu servis doğrudan Android API çağrısı yapmaz
- Android izin, URI, dosya sistemi veya platform köprüsü kullanmaz
- Bu nedenle API 34 açısından düşük risklidir
- Bu düzenlenmiş sürüm API 34 hedefinde daha güvenli katman doğrulaması ile güncellenmiştir

SURUM: 2
TARIH: 2026-03-17
IMZA: FY.
"""

from __future__ import annotations


class GeciciBildirimServisi:
    """
    Geçici bildirim katmanını yöneten hafif servis.

    Beklenen layer metodları:
    - show(text=..., icon_name=..., duration=...)
    - hide()
    - hide_immediately()

    API 34 uyumluluk notu:
    - Platform bağımsızdır; Android API değişimlerinden doğrudan etkilenmez.
    """

    def __init__(self):
        self._layer = None

    def _normalize_duration(self, duration: float) -> float:
        """
        Süre değerini güvenli biçimde normalize eder.

        Geçersiz veya negatif değer gelirse varsayılan 2.4 döner.
        """
        try:
            val = float(duration)
            if val <= 0:
                return 2.4
            return val
        except Exception:
            return 2.4

    def _is_valid_layer(self, layer) -> bool:
        """
        Verilen nesnenin geçici bildirim katmanı olarak kullanılabilir olup olmadığını kontrol eder.
        """
        if layer is None:
            return False

        try:
            return (
                hasattr(layer, "show")
                and callable(getattr(layer, "show"))
                and hasattr(layer, "hide")
                and callable(getattr(layer, "hide"))
                and hasattr(layer, "hide_immediately")
                and callable(getattr(layer, "hide_immediately"))
            )
        except Exception:
            return False

    def register_layer(self, layer) -> None:
        """
        Geçici bildirim katmanını kaydeder.

        API 34 uyumluluk notu:
        - Katman doğrulaması yapılarak hatalı nesne kaydı engellenir.
        """
        if not self._is_valid_layer(layer):
            self._layer = None
            return

        self._layer = layer

    def unregister_layer(self) -> None:
        """
        Kayıtlı katmanı temizler.
        """
        self._layer = None

    def has_layer(self) -> bool:
        """
        Kullanılabilir bir bildirim katmanı kayıtlı mı kontrol eder.
        """
        return self._is_valid_layer(self._layer)

    def show(self, text: str, icon_name: str = "", duration: float = 2.4) -> bool:
        """
        Geçici bildirimi gösterir.

        Dönüş:
        - True: başarıyla gösterme çağrısı yapıldı
        - False: layer yok ya da çağrı başarısız
        """
        if not self.has_layer():
            return False

        try:
            self._layer.show(
                text=str(text or ""),
                icon_name=str(icon_name or ""),
                duration=self._normalize_duration(duration),
            )
            return True
        except Exception:
            return False

    def hide(self) -> bool:
        """
        Kayıtlı bildirim katmanına normal gizleme komutu gönderir.
        """
        if not self.has_layer():
            return False

        try:
            self._layer.hide()
            return True
        except Exception:
            return False

    def hide_immediately(self) -> bool:
        """
        Kayıtlı bildirim katmanına anında gizleme komutu gönderir.
        """
        if not self.has_layer():
            return False

        try:
            self._layer.hide_immediately()
            return True
        except Exception:
            return False


gecici_bildirim_servisi = GeciciBildirimServisi()
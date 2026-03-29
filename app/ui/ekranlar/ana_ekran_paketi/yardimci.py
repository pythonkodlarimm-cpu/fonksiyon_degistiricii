# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ekranlar/ana_ekran_paketi/yardimci.py

ROL:
- Ana ekranın yardımcı UI ve veri işlemlerini içerir
- Dil çözümleme, arka plan çizimi ve preview üretimi burada tutulur
- Ekran yardımcılarını yerleşim ve aksiyon katmanından ayırır

MİMARİ:
- Yardımcı ve tekrar kullanılabilir metotları içerir
- UI mantığını sadeleştirir
- Servis erişimini tek noktadan kullanır
- Ortak stil ve görünüm yardımcılarını sağlar
- Geriye uyumluluk katmanı içermez

SURUM: 4
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

from kivy.graphics import Color, Rectangle

from app.ui.ortak.renkler import ARKAPLAN


class AnaEkranYardimciMixin:
    """
    Ana ekran yardımcı metotlarını sağlayan mixin.
    """

    def _t(self, key: str, **kwargs) -> str:
        """
        Dil servisi üzerinden çeviri yapar.

        Args:
            key: Çeviri anahtarı.
            **kwargs: Format alanları.

        Returns:
            str: Çevrilmiş metin. Hata olursa anahtarın kendisi döner.
        """
        try:
            return self._services.dil_servisi().t(key, **kwargs)
        except Exception:
            return str(key)

    def _arka_plan(self) -> None:
        """
        Ana ekran arka planını çizer ve boyut değişimlerine bağlar.
        """
        with self.canvas.before:
            Color(*ARKAPLAN)
            self._rect = Rectangle(
                pos=self.pos,
                size=self.size,
            )

        self.bind(pos=self._yenile_arka_plan, size=self._yenile_arka_plan)

    def _yenile_arka_plan(self, *_args) -> None:
        """
        Arka plan dikdörtgeninin konum ve boyutunu günceller.
        """
        if self._rect is None:
            return

        self._rect.pos = self.pos
        self._rect.size = self.size

    def _item_attr(self, item: Any, *names: str, default=None):
        """
        Dict veya obje üzerinden ilk uygun alanı döndürür.

        Args:
            item: Kaynak item.
            *names: Denenecek alan adları.
            default: Hiçbiri bulunamazsa dönecek değer.

        Returns:
            Any: Bulunan alan değeri veya default.
        """
        if item is None:
            return default

        for name in names:
            if not name:
                continue

            if isinstance(item, dict) and name in item:
                return item.get(name)

            try:
                if hasattr(item, name):
                    return getattr(item, name)
            except Exception:
                continue

        return default

    def _aktif_dosya_icerigi(self) -> str:
        """
        Seçili kaynağın metin içeriğini okur.

        Returns:
            str: Dosya içeriği. Seçili kaynak yoksa veya okuma başarısızsa
            boş metin döner.
        """
        if not self._secili_kaynak:
            return ""

        try:
            icerik = self._services.dosya_erisim().metin_oku(self._secili_kaynak)
        except Exception:
            return ""

        return str(icerik or "")

    def _guvenli_satir_no(self, value, *, default: int = 0) -> int:
        """
        Satır numarası değerini güvenli biçimde int'e çevirir.

        Args:
            value: Dönüştürülecek değer.
            default: Hata durumunda kullanılacak varsayılan değer.

        Returns:
            int: Güvenli satır numarası.
        """
        try:
            return int(value or 0)
        except Exception:
            return int(default)

    def _item_preview_text(self, item) -> str:
        """
        Seçilen item için önizleme metni üretir.

        Mantık:
        - item içindeki satır bilgilerini okur
        - aktif dosya içeriğini alır
        - ilgili satır aralığını çıkarır
        - end bilgisi yoksa makul bir preview aralığı üretir

        Args:
            item: Seçilen fonksiyon/item.

        Returns:
            str: Önizleme metni.
        """
        if item is None:
            return ""

        icerik = self._aktif_dosya_icerigi()
        if not icerik:
            return ""

        satirlar = icerik.splitlines()
        if not satirlar:
            return ""

        start = self._guvenli_satir_no(
            self._item_attr(item, "lineno", "satir", default=0)
        )
        end = self._guvenli_satir_no(
            self._item_attr(item, "end_lineno", "bitis_satiri", default=0)
        )

        if start <= 0:
            return ""

        toplam_satir = len(satirlar)

        if end <= 0 or end < start:
            end = min(toplam_satir, start + 40)

        start_index = max(0, start - 1)
        end_index = min(toplam_satir, end)

        if start_index >= end_index:
            return ""

        return "\n".join(satirlar[start_index:end_index]).strip()
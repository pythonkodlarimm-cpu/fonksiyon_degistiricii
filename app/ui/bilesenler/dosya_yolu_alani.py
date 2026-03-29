# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/bilesenler/dosya_yolu_alani.py

ROL:
- Seçilen dosya yolunu / Android URI bilgisini gösterir
- Sade ve düz görünümlü dosya bilgi alanı sunar
- Uzun yolları kontrollü biçimde kısaltır
- Ortak semantic boyut sistemine uyumlu çalışır
- Dil entegrasyonuna uyumludur

MİMARİ:
- Hafif UI bileşeni
- Ortak renk/boyut yapısına uyar
- Gereksiz kart görünümü taşımaz
- Ölçüler yalnızca ortak boyutlar modülünden alınır
- Geriye uyumluluk katmanı içermez

SURUM: 4
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Callable

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from app.ui.ortak.boyutlar import (
    PADDING_KART,
    YUKSEKLIK_GIRDI,
)
from app.ui.ortak.renkler import (
    AYIRICI,
    METIN,
    METIN_SOLUK,
    SEFFAF,
)
from app.ui.ortak.stiller import rounded_bg
from app.ui.ortak.yardimcilar import kisalt_yol


class DosyaYoluAlani(BoxLayout):
    """
    Seçili dosya yolunu gösteren UI bileşeni.

    Özellikler:
    - boş durumda placeholder metin gösterir
    - dolu durumda yolu kısaltarak gösterir
    - renk ile durum ayrımı yapar
    - ortak semantic boyut sistemini kullanır
    """

    __slots__ = ("_label", "_t")

    def __init__(
        self,
        *,
        t: Callable[[str], str] | None = None,
        **kwargs,
    ):
        """
        Dosya yolu alanını oluşturur.

        Args:
            t: Çeviri fonksiyonu.
            **kwargs: BoxLayout argümanları.
        """
        super().__init__(**kwargs)

        self._t = t or (lambda key, **_kwargs: key)

        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = YUKSEKLIK_GIRDI
        self.padding = (PADDING_KART, 0)

        rounded_bg(
            self,
            bg_color=SEFFAF,
            line_color=AYIRICI,
        )

        bos_text = self._t("file_not_selected")
        if bos_text == "file_not_selected":
            bos_text = "Dosya seçilmedi"

        self._label = Label(
            text=bos_text,
            color=METIN_SOLUK,
            halign="left",
            valign="middle",
        )
        self._label.bind(
            size=lambda inst, _val: setattr(inst, "text_size", inst.size)
        )

        self.add_widget(self._label)

    def dosya_yolu_ayarla(self, path: str) -> None:
        """
        Gösterilen dosya yolunu günceller.

        Args:
            path: Ham dosya yolu veya URI.
        """
        raw = str(path or "").strip()

        if not raw:
            bos_text = self._t("file_not_selected")
            if bos_text == "file_not_selected":
                bos_text = "Dosya seçilmedi"

            self._label.text = bos_text
            self._label.color = METIN_SOLUK
            return

        self._label.text = kisalt_yol(raw)
        self._label.color = METIN
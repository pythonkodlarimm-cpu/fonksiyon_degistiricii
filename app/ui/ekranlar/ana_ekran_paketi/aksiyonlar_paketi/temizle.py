# -*- coding: utf-8 -*-
"""
DOSYA: temizle.py

ROL:
- Kod panellerini temizleme aksiyonunu içerir

MİMARİ:
- UI bilmez
- Sadece ekran referanslarını kullanır
- Deterministik çalışır
- Geriye uyumluluk yok

SURUM: 1
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations


class AnaEkranTemizleAksiyonMixin:

    def _temizle(self, *_args) -> None:
        """
        Kod panellerini temizler.
        """

        if self._mevcut_kod_input:
            self._mevcut_kod_input.text = ""

        if self._yeni_kod_input:
            self._yeni_kod_input.text = ""

        if self._bilgi:
            self._bilgi.mesaj(self._t("clear") or "Temizlendi")
# -*- coding: utf-8 -*-
"""
DOSYA: yapistir.py

ROL:
- Clipboard'dan veri alıp yeni kod alanına yapıştırır

MİMARİ:
- Deterministik çalışır
- Veri normalize edilir
- UI bağımsızdır (ref üzerinden çalışır)
- Geriye uyumluluk yok

SURUM: 1
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from kivy.core.clipboard import Clipboard


class AnaEkranYapistirAksiyonMixin:

    def _yapistir(self, *_args) -> None:
        """
        Clipboard verisini normalize ederek yapıştırır.
        """

        try:
            veri: str = Clipboard.paste() or ""

            veri = veri.replace("\r\n", "\n").replace("\t", "    ").strip("\n")

            if self._yeni_kod_input:
                self._yeni_kod_input.text = veri

            if self._bilgi:
                self._bilgi.mesaj(self._t("paste") or "Yapıştırıldı")

        except Exception:
            if self._bilgi:
                self._bilgi.mesaj(self._t("error") or "Yapıştırma hatası")
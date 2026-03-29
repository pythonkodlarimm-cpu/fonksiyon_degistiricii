# -*- coding: utf-8 -*-
"""
DOSYA: temizle.py

ROL:
- Kod panellerini temizleme aksiyonunu içerir
- UI etkilerini güvenli biçimde ana Kivy thread üzerinde yürütür
- BilgiKutusu feedback pipeline ile entegre çalışır

MİMARİ:
- UI bilmez (doğrudan widget referansları ile çalışır)
- Deterministik çalışır
- Fail-soft davranır
- Geriye uyumluluk yok
- UI güncellemeleri ortak ui_thread katmanı üzerinden yürütülür

SURUM: 2
TARIH: 2026-03-29
IMZA: FY.
"""

from __future__ import annotations

from kivy.logger import Logger

from app.ui.ortak.ui_thread import ui_thread_uzerinde_calistir


class AnaEkranTemizleAksiyonMixin:

    def _temizle(self, *_args) -> None:
        """
        Kod panellerini temizler.
        """
        Logger.info("AnaEkranTemizleAksiyon: _temizle girdi.")

        def _ui() -> None:
            try:
                if getattr(self, "_mevcut_kod_input", None):
                    self._mevcut_kod_input.text = ""

                if getattr(self, "_yeni_kod_input", None):
                    self._yeni_kod_input.text = ""

                if getattr(self, "_bilgi", None):
                    mesaj = self._t("clear")
                    if mesaj == "clear":
                        mesaj = "Temizlendi"
                    self._bilgi.mesaj(str(mesaj or "Temizlendi"))

            except Exception as exc:
                Logger.exception(f"AnaEkranTemizleAksiyon: _temizle hata: {exc}")

        ui_thread_uzerinde_calistir(_ui)
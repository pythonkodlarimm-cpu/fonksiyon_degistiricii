# -*- coding: utf-8 -*-
"""
DOSYA: yapistir.py

ROL:
- Clipboard'dan veri alıp yeni kod alanına yapıştırır
- Veri normalize edilir (CRLF -> LF, TAB -> 4 boşluk)
- UI etkilerini güvenli biçimde ana Kivy thread üzerinde yürütür
- BilgiKutusu feedback pipeline ile entegre çalışır

MİMARİ:
- Deterministik çalışır
- Veri normalize edilir
- UI bağımsızdır (ref üzerinden çalışır)
- Fail-soft davranır
- Geriye uyumluluk yok
- UI güncellemeleri ortak ui_thread katmanı üzerinden yürütülür

SURUM: 2
TARIH: 2026-03-29
IMZA: FY.
"""

from __future__ import annotations

from kivy.core.clipboard import Clipboard
from kivy.logger import Logger

from app.ui.ortak.ui_thread import ui_thread_uzerinde_calistir


class AnaEkranYapistirAksiyonMixin:

    def _yapistir(self, *_args) -> None:
        """
        Clipboard verisini normalize ederek yapıştırır.
        """
        Logger.info("AnaEkranYapistirAksiyon: _yapistir girdi.")

        try:
            veri: str = Clipboard.paste() or ""

            # normalize
            veri = veri.replace("\r\n", "\n").replace("\t", "    ").strip("\n")

            def _ui() -> None:
                try:
                    if getattr(self, "_yeni_kod_input", None):
                        self._yeni_kod_input.text = veri

                    if getattr(self, "_bilgi", None):
                        mesaj = self._t("paste")
                        if mesaj == "paste":
                            mesaj = "Yapıştırıldı"
                        self._bilgi.mesaj(str(mesaj or "Yapıştırıldı"))

                except Exception as exc:
                    Logger.exception(
                        f"AnaEkranYapistirAksiyon: UI uygulama hatasi: {exc}"
                    )

            ui_thread_uzerinde_calistir(_ui)

        except Exception as exc:
            Logger.exception(f"AnaEkranYapistirAksiyon: clipboard hata: {exc}")

            def _error_ui() -> None:
                if getattr(self, "_bilgi", None):
                    mesaj = self._t("error")
                    if mesaj == "error":
                        mesaj = "Yapıştırma hatası"
                    self._bilgi.mesaj(str(mesaj or "Yapıştırma hatası"), hata=True)

            ui_thread_uzerinde_calistir(_error_ui)
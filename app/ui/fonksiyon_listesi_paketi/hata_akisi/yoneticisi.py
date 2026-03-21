# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/hata_akisi/yoneticisi.py
"""

from __future__ import annotations


class HataAkisiYoneticisi:
    def _modul(self):
        from app.ui.fonksiyon_listesi_paketi.hata_akisi import hata_akisi
        return hata_akisi

    def debug(self, owner, message: str) -> None:
        self._modul().debug(owner, message)

    def format_exception_details(self, owner, exc: Exception, title: str) -> str:
        return self._modul().format_exception_details(owner, exc, title)

    def report_error(
        self,
        owner,
        exc: Exception,
        title: str = "Fonksiyon Listesi Hatası",
        detailed_text: str = "",
    ) -> None:
        self._modul().report_error(
            owner=owner,
            exc=exc,
            title=title,
            detailed_text=detailed_text,
        )
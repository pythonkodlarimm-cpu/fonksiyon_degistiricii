# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/yardimci/yoneticisi.py
"""

from __future__ import annotations


class YardimciYoneticisi:
    def modul(self):
        from app.ui.fonksiyon_listesi_paketi.yardimci import yardimci
        return yardimci

    def item_key(self, item) -> tuple:
        return self.modul().item_key(item)

    def restore_selected_item(self, all_items, old_item):
        return self.modul().restore_selected_item(all_items, old_item)

    def format_exception_details(self, exc: Exception, title: str = "Fonksiyon Listesi Hatası") -> str:
        return self.modul().format_exception_details(exc, title=title)
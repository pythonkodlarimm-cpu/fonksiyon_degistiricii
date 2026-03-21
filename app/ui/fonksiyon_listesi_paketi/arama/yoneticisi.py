# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/arama/yoneticisi.py
"""

from __future__ import annotations


class AramaYoneticisi:
    def modul(self):
        from app.ui.fonksiyon_listesi_paketi.arama import arama
        return arama

    def normalize_query_tokens(self, value: str) -> list[str]:
        return self.modul().normalize_query_tokens(value)

    def item_search_text(self, item) -> str:
        return self.modul().item_search_text(item)

    def item_matches_query(self, item, tokens: list[str]) -> bool:
        return self.modul().item_matches_query(item, tokens)

    def apply_filter(self, items, value: str):
        return self.modul().apply_filter(items, value)
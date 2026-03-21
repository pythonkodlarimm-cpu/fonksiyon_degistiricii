# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/ui_kurulumu/yoneticisi.py
"""

from __future__ import annotations


class UiKurulumuYoneticisi:
    def _modul(self):
        from app.ui.fonksiyon_listesi_paketi.ui_kurulumu import ui_kurulumu
        return ui_kurulumu

    def build_ui(self, owner) -> None:
        self._modul().build_ui(owner)

    def build_header_row(self, owner) -> None:
        self._modul().build_header_row(owner)

    def build_search_box(self, owner) -> None:
        self._modul().build_search_box(owner)

    def build_list_box(self, owner) -> None:
        self._modul().build_list_box(owner)

    def build_preview_boxes(self, owner) -> None:
        self._modul().build_preview_boxes(owner)

    def build_preview_card(self, owner, title: str, icon_name: str):
        return self._modul().build_preview_card(owner, title=title, icon_name=icon_name)

    def build_table_header_label(self, owner, text: str, size_hint_x: float):
        return self._modul().build_table_header_label(
            owner,
            text=text,
            size_hint_x=size_hint_x,
        )
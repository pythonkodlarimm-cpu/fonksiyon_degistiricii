# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/gorunum_akisi/yoneticisi.py
"""

from __future__ import annotations


class GorunumAkisiYoneticisi:
    def _modul(self):
        from app.ui.fonksiyon_listesi_paketi.gorunum_akisi import gorunum_akisi
        return gorunum_akisi

    def set_toggle_icon(self, owner, icon_name: str) -> None:
        self._modul().set_toggle_icon(owner, icon_name)

    def update_toggle_icon(self, owner) -> None:
        self._modul().update_toggle_icon(owner)

    def toggle_list_visibility(self, owner, *_args) -> None:
        self._modul().toggle_list_visibility(owner, *_args)

    def sync_list_visibility(self, owner) -> None:
        self._modul().sync_list_visibility(owner)
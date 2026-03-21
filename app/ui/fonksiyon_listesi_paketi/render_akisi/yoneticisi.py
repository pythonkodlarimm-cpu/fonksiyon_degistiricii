# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/render_akisi/yoneticisi.py
"""

from __future__ import annotations


class RenderAkisiYoneticisi:
    def _modul(self):
        from app.ui.fonksiyon_listesi_paketi.render_akisi import render_akisi
        return render_akisi

    def make_empty_label(self, owner):
        return self._modul().make_empty_label(owner)

    def refresh_trigger(self, owner, *_args):
        return self._modul().refresh_trigger(owner, *_args)

    def render_items(self, owner, items, keep_scroll: bool = False) -> None:
        self._modul().render_items(owner, items=items, keep_scroll=keep_scroll)

    def scroll_top(self, owner, *_args):
        self._modul().scroll_top(owner, *_args)

    def selected_itemi_gorunur_tut(self, owner, *_args):
        self._modul().selected_itemi_gorunur_tut(owner, *_args)
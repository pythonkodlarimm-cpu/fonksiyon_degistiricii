# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/onizleme/yoneticisi.py
"""

from __future__ import annotations


class OnizlemeYoneticisi:
    def modul(self):
        from app.ui.fonksiyon_listesi_paketi.onizleme import onizleme
        return onizleme

    def preview_from_text(self, text: str, max_lines: int = 5) -> str:
        return self.modul().preview_from_text(text, max_lines=max_lines)
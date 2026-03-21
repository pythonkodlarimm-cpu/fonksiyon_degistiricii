# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/onizleme/onizleme.py
"""

from __future__ import annotations


def preview_from_text(text: str, max_lines: int = 5) -> str:
    metin = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    satirlar = [satir.rstrip() for satir in metin.split("\n")]

    temiz = []
    for satir in satirlar:
        if not temiz and not satir.strip():
            continue
        temiz.append(satir)

    if not temiz:
        return "Henüz önizleme yok."

    out = temiz[:max_lines]
    if len(temiz) > max_lines:
        out.append("...")

    return "\n".join(out)
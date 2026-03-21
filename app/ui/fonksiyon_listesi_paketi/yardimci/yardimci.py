# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/yardimci/yardimci.py
"""

from __future__ import annotations

import traceback


def item_key(item) -> tuple:
    if item is None:
        return ("", "", "", 0, 0)

    return (
        str(getattr(item, "path", "") or ""),
        str(getattr(item, "name", "") or ""),
        str(getattr(item, "kind", "") or ""),
        int(getattr(item, "lineno", 0) or 0),
        int(getattr(item, "end_lineno", 0) or 0),
    )


def restore_selected_item(all_items, old_item):
    if old_item is None:
        return None

    old_key = item_key(old_item)

    for item in list(all_items or []):
        if item_key(item) == old_key:
            return item

    old_path = str(getattr(old_item, "path", "") or "")
    old_name = str(getattr(old_item, "name", "") or "")

    for item in list(all_items or []):
        if (
            str(getattr(item, "path", "") or "") == old_path
            and str(getattr(item, "name", "") or "") == old_name
        ):
            return item

    return None


def format_exception_details(exc: Exception, title: str = "Fonksiyon Listesi Hatası") -> str:
    exc_type = type(exc).__name__
    dosya = "bilinmiyor"
    fonksiyon = "bilinmiyor"
    satir = "bilinmiyor"
    kaynak_satir = ""

    try:
        tb_list = traceback.extract_tb(exc.__traceback__)
        if tb_list:
            son = tb_list[-1]
            dosya = str(getattr(son, "filename", "bilinmiyor") or "bilinmiyor")
            fonksiyon = str(getattr(son, "name", "bilinmiyor") or "bilinmiyor")
            satir = str(getattr(son, "lineno", "bilinmiyor") or "bilinmiyor")
            kaynak_satir = str(getattr(son, "line", "") or "").strip()
    except Exception:
        pass

    parcalar = [
        f"BASLIK:\n{title}",
        f"HATA TÜRÜ:\n{exc_type}",
        f"DOSYA:\n{dosya}",
        f"FONKSİYON:\n{fonksiyon}",
        f"SATIR:\n{satir}",
    ]

    if kaynak_satir:
        parcalar.append(f"KAYNAK SATIR:\n{kaynak_satir}")

    parcalar.append(f"DETAY:\n{str(exc or '').strip() or 'Ayrıntı alınamadı.'}")

    try:
        tb_text = traceback.format_exc().strip()
        if tb_text and tb_text != "NoneType: None":
            parcalar.append(f"TRACEBACK:\n{tb_text}")
    except Exception:
        pass

    return "\n\n".join(parcalar)
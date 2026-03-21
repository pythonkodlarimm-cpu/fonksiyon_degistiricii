# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/hata_akisi/hata_akisi.py
"""

from __future__ import annotations

import traceback


def debug(owner, message: str) -> None:
    try:
        print("[FONKSIYON_LISTESI_PANEL]", str(message))
    except Exception:
        pass


def format_exception_details(owner, exc: Exception, title: str) -> str:
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


def report_error(
    owner,
    exc: Exception,
    title: str = "Fonksiyon Listesi Hatası",
    detailed_text: str = "",
) -> None:
    try:
        detay = str(detailed_text or "").strip() or format_exception_details(
            owner,
            exc,
            title=title,
        )
        if getattr(owner, "on_error", None):
            owner.on_error(exc, title=title, detailed_text=detay)
    except Exception:
        pass
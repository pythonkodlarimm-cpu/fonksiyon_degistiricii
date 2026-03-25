# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/yardimci/yardimci.py

ROL:
- Fonksiyon listesi için yardımcı veri akışlarını toplamak
- Seçili öğeyi yeniden eşlemek
- Hata detay metni üretmek
- Liste panelinde tekrar kullanılan ortak yardımcı davranışları sağlamak
- Aktif dile göre hata metni alan başlıklarını üretebilmek

MİMARİ:
- Saf yardımcı fonksiyonlar içerir
- Üst katman bu modüle doğrudan değil, yardimci/yoneticisi.py üzerinden erişmelidir
- UI bağımsız çalışır
- Owner üzerinden dil servisine erişim desteklenir
- Fail-soft yaklaşım korunur

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 2
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

import traceback


def _m(owner, anahtar: str, default: str = "") -> str:
    try:
        if owner is not None and hasattr(owner, "_m"):
            return str(owner._m(anahtar, default) or default or anahtar)
    except Exception:
        pass
    return str(default or anahtar)


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


def format_exception_details(
    owner,
    exc: Exception,
    title: str = "Fonksiyon Listesi Hatası",
) -> str:
    exc_type = type(exc).__name__
    bilinmiyor = _m(owner, "unknown", "bilinmiyor")

    dosya = bilinmiyor
    fonksiyon = bilinmiyor
    satir = bilinmiyor
    kaynak_satir = ""

    try:
        tb_list = traceback.extract_tb(exc.__traceback__)
        if tb_list:
            son = tb_list[-1]
            dosya = str(getattr(son, "filename", bilinmiyor) or bilinmiyor)
            fonksiyon = str(getattr(son, "name", bilinmiyor) or bilinmiyor)
            satir = str(getattr(son, "lineno", bilinmiyor) or bilinmiyor)
            kaynak_satir = str(getattr(son, "line", "") or "").strip()
    except Exception:
        pass

    parcalar = [
        f"{_m(owner, 'title', 'BASLIK')}:\n{title}",
        f"{_m(owner, 'error_type', 'HATA TÜRÜ')}:\n{exc_type}",
        f"{_m(owner, 'file', 'DOSYA')}:\n{dosya}",
        f"{_m(owner, 'function', 'FONKSİYON')}:\n{fonksiyon}",
        f"{_m(owner, 'line', 'SATIR')}:\n{satir}",
    ]

    if kaynak_satir:
        parcalar.append(
            f"{_m(owner, 'source_line', 'KAYNAK SATIR')}:\n{kaynak_satir}"
        )

    parcalar.append(
        f"{_m(owner, 'detail', 'DETAY')}:\n"
        f"{str(exc or '').strip() or _m(owner, 'detail_unavailable', 'Ayrıntı alınamadı.')}"
    )

    try:
        tb_text = traceback.format_exc().strip()
        if tb_text and tb_text != "NoneType: None":
            parcalar.append(f"{_m(owner, 'traceback', 'TRACEBACK')}:\n{tb_text}")
    except Exception:
        pass

    return "\n\n".join(parcalar)

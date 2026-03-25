# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/hata_akisi/hata_akisi.py

ROL:
- Fonksiyon listesi katmanında hata ayıklama ve hata raporlama akışını yönetmek
- İstisna detaylarını kullanıcıya gösterilebilir metne dönüştürmek
- Üst katmanın on_error callback akışına detaylı hata metni iletmek
- Aktif dile göre görünür hata başlıklarını ve alan adlarını üretebilmek

MİMARİ:
- Hata akışı yardımcıları burada tutulur
- Üst katman bu modüle doğrudan değil, hata_akisi/yoneticisi.py üzerinden erişmelidir
- UI bağımsız çalışır
- Owner üzerinden dil metni çözümü yapılabilir
- Fail-soft yaklaşım korunur

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 3
TARIH: 2026-03-24
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


def debug(owner, message: str) -> None:
    try:
        print("[FONKSIYON_LISTESI_PANEL]", str(message))
    except Exception:
        pass


def format_exception_details(owner, exc: Exception, title: str) -> str:
    exc_type = type(exc).__name__
    dosya = _m(owner, "unknown", "bilinmiyor")
    fonksiyon = _m(owner, "unknown", "bilinmiyor")
    satir = _m(owner, "unknown", "bilinmiyor")
    kaynak_satir = ""

    try:
        tb_list = traceback.extract_tb(exc.__traceback__)
        if tb_list:
            son = tb_list[-1]
            dosya = str(
                getattr(son, "filename", _m(owner, "unknown", "bilinmiyor"))
                or _m(owner, "unknown", "bilinmiyor")
            )
            fonksiyon = str(
                getattr(son, "name", _m(owner, "unknown", "bilinmiyor"))
                or _m(owner, "unknown", "bilinmiyor")
            )
            satir = str(
                getattr(son, "lineno", _m(owner, "unknown", "bilinmiyor"))
                or _m(owner, "unknown", "bilinmiyor")
            )
            kaynak_satir = str(getattr(son, "line", "") or "").strip()
    except Exception:
        pass

    temiz_baslik = str(
        title or _m(owner, "function_list_error", "Fonksiyon Listesi Hatası")
    ).strip() or _m(owner, "function_list_error", "Fonksiyon Listesi Hatası")

    detay = str(exc or "").strip() or _m(
        owner,
        "detail_unavailable",
        "Ayrıntı alınamadı.",
    )

    parcalar = [
        f"{_m(owner, 'title', 'BASLIK')}:\n{temiz_baslik}",
        f"{_m(owner, 'error_type', 'HATA TÜRÜ')}:\n{exc_type}",
        f"{_m(owner, 'file', 'DOSYA')}:\n{dosya}",
        f"{_m(owner, 'function_label_upper', 'FONKSİYON')}:\n{fonksiyon}",
        f"{_m(owner, 'line_label_upper', 'SATIR')}:\n{satir}",
    ]

    if kaynak_satir:
        parcalar.append(
            f"{_m(owner, 'source_line', 'KAYNAK SATIR')}:\n{kaynak_satir}"
        )

    parcalar.append(f"{_m(owner, 'detail', 'DETAY')}:\n{detay}")

    try:
        tb_text = traceback.format_exc().strip()
        if tb_text and tb_text != "NoneType: None":
            parcalar.append(f"{_m(owner, 'traceback', 'TRACEBACK')}:\n{tb_text}")
    except Exception:
        pass

    return "\n\n".join(parcalar)


def report_error(
    owner,
    exc: Exception,
    title: str = "",
    detailed_text: str = "",
) -> None:
    try:
        temiz_baslik = str(
            title or _m(owner, "function_list_error", "Fonksiyon Listesi Hatası")
        ).strip() or _m(owner, "function_list_error", "Fonksiyon Listesi Hatası")

        detay = str(detailed_text or "").strip() or format_exception_details(
            owner,
            exc,
            title=temiz_baslik,
        )

        if getattr(owner, "on_error", None):
            owner.on_error(exc, title=temiz_baslik, detailed_text=detay)
    except Exception:
        pass

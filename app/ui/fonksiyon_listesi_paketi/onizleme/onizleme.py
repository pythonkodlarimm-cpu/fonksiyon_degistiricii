# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/onizleme/onizleme.py

ROL:
- Fonksiyon kodunun kısa önizlemesini üretmek
- Satır sayısını sınırlamak
- Boş satırları temizlemek
- Dil destekli fallback mesaj üretmek
- Yeni otomatik dil sistemiyle uyumlu çalışmak

MİMARİ:
- Saf yardımcı fonksiyonlar içerir
- UI bağımsızdır
- Owner üzerinden _m zinciriyle aktif dil metni çözebilir
- Fail-soft yaklaşımı korunur

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 3
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations


def _m(owner, anahtar: str, default: str = "") -> str:
    try:
        if owner is not None and hasattr(owner, "_m"):
            return str(owner._m(anahtar, default) or default or anahtar)
    except Exception:
        pass
    return str(default or anahtar)


def _normalize_text(text: str) -> str:
    try:
        return str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    except Exception:
        return ""


def _trim_leading_blank_lines(lines: list[str]) -> list[str]:
    temiz = list(lines or [])

    while temiz and not str(temiz[0] or "").strip():
        temiz.pop(0)

    return temiz


def _safe_max_lines(max_lines: int) -> int:
    try:
        value = int(max_lines)
        if value <= 0:
            return 5
        return value
    except Exception:
        return 5


def preview_from_text(owner, text: str, max_lines: int = 5) -> str:
    metin = _normalize_text(text)
    limit = _safe_max_lines(max_lines)

    try:
        satirlar = [str(satir or "").rstrip() for satir in metin.split("\n")]
    except Exception:
        satirlar = []

    temiz = _trim_leading_blank_lines(satirlar)

    if not temiz:
        return _m(owner, "preview_empty", "Henüz önizleme yok.")

    out = temiz[:limit]

    if len(temiz) > limit:
        out.append("...")

    try:
        return "\n".join(out)
    except Exception:
        return _m(owner, "preview_empty", "Henüz önizleme yok.")

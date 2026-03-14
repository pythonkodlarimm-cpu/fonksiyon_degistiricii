# -*- coding: utf-8 -*-

from __future__ import annotations

UYGULAMA_ADI = "Fonksiyon Değiştirici"
PAKET_ADI = "fonksiyon_degistirici"

SURUM = "0.1.0"
BUILD = 1

TARIH = "2026-03-10"
IMZA = "FY."

ACIKLAMA = (
    "Python dosyalarındaki fonksiyonları ve nested function'ları "
    "arayüz üzerinden seçip güncellemek için geliştirilen uygulama."
)


def tam_surum() -> str:
    return f"{SURUM} ({BUILD})"
# -*- coding: utf-8 -*-
"""
DOSYA: app/services/guncelleme/ayarlari.py

ROL:
- Güncelleme akışı için sabit ayarları merkezi olarak tutmak
- Play Store paket adı, version.json adresi ve yönlendirme linklerini üretmek
- Güncelleme kontrol davranışını sade biçimde yönetmek

MİMARİ:
- Güncelleme servisleri bu dosyadaki sabitlerden beslenir
- UI katmanı doğrudan sabit bilmez
- Tek merkezli yapı korunur
- Version kontrolü uzak JSON endpoint üzerinden yapılır

API UYUMLULUK:
- Android API 35 uyumlu
- Play Store yönlendirme akışına uygundur
- Ağ üzerinden sürüm kontrolüne uygundur

SURUM: 2
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations


# =========================================================
# UYGULAMA KIMLIGI
# =========================================================
PLAY_STORE_PACKAGE_NAME: str = "org.fy.fonksiyon_degistirici"


# =========================================================
# GUNCELLEME DAVRANISI
# =========================================================
GUNCELLEME_KONTROL_AKTIF: bool = True
GUNCELLEME_BILDIRIM_METNI: str = "Yeni sürüm mevcut."
GUNCELLEME_BUTON_METNI: str = "Güncelle"


# =========================================================
# VERSION JSON
# =========================================================
VERSION_JSON_URL: str = (
    "https://pythonkodlarimm-cpu.github.io/fonksiyon_degistiricii/docs/version.json"
)

# UI'yi uzun süre bekletmemek için kısa timeout
VERSION_CHECK_TIMEOUT_SECONDS: float = 4.0


# =========================================================
# LINKLER
# =========================================================
def play_store_market_url(package_name: str | None = None) -> str:
    paket = str(package_name or PLAY_STORE_PACKAGE_NAME).strip()
    return f"market://details?id={paket}"


def play_store_web_url(package_name: str | None = None) -> str:
    paket = str(package_name or PLAY_STORE_PACKAGE_NAME).strip()
    return f"https://play.google.com/store/apps/details?id={paket}"
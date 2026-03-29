# -*- coding: utf-8 -*-
"""
DOSYA: app/core/meta/sabitler.py

ROL:
- Uygulama genel sabitlerini içerir
- Sürüm, paket adı, açıklama ve imza bilgilerini sağlar
- Android build süreci ve uygulama içi meta kullanımına hizmet eder

MİMARİ:
- Bu dosya yalnızca sabit veri içerir (runtime hesaplama yok)
- Deterministic yapıdadır (CI/CD ile uyumludur)
- Üst katman doğrudan bu dosyayı değil meta yöneticisini kullanmalıdır

ANDROID NOTLARI:
- SURUM_ADI → kullanıcıya görünen versiyon (versionName)
- SURUM_KODU → Play Store için integer (versionCode)
- SURUM_KODU her build’de artmalıdır (CI ile güncellenebilir)

BAĞIMLILIKLAR:
- Yok

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur

SURUM: 3
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations

from typing import Dict

# =========================================================
# TEMEL KIMLIK
# =========================================================
UYGULAMA_ADI: str = "Fonksiyon Değiştirici"
PAKET_ADI: str = "fonksiyon_degistirici"

# =========================================================
# SURUM
# =========================================================
# Kullanıcıya görünen sürüm
SURUM_ADI: str = "0.1.0"

# Play Store için integer sürüm kodu
SURUM_KODU: int = 1

# Build metadata
BUILD_NUMARASI: int = 1

# =========================================================
# DIGER META
# =========================================================
TARIH: str = "2026-03-10"
IMZA: str = "FY."

ACIKLAMA: str = (
    "Python dosyalarındaki fonksiyonları ve nested function'ları "
    "arayüz üzerinden seçip güncellemek için geliştirilen uygulama."
)

# =========================================================
# FORMATLI VERILER
# =========================================================
def get_tam_surum() -> str:
    """
    Kullanıcıya gösterilecek tam sürüm stringi.
    """
    return f"{SURUM_ADI} ({BUILD_NUMARASI})"


def get_apk_surum_kodu() -> int:
    """
    Android versionCode.
    """
    return SURUM_KODU


def get_apk_surum_adi() -> str:
    """
    Android versionName.
    """
    return SURUM_ADI


def get_uygulama_etiketi() -> str:
    """
    UI / About ekranı için kısa etiket.
    """
    return f"{UYGULAMA_ADI} v{SURUM_ADI}"


def get_meta_bilgisi() -> Dict[str, str | int]:
    """
    Toplu metadata çıktısı.
    """
    return {
        "uygulama_adi": UYGULAMA_ADI,
        "paket_adi": PAKET_ADI,
        "surum_adi": SURUM_ADI,
        "surum_kodu": SURUM_KODU,
        "build": BUILD_NUMARASI,
        "tarih": TARIH,
        "imza": IMZA,
        "aciklama": ACIKLAMA,
        "tam_surum": get_tam_surum(),
    }
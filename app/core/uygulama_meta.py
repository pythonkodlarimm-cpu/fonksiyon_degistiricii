# -*- coding: utf-8 -*-
"""
DOSYA: app/sabitler.py
ROL:
- Uygulama genel sabitleri
- Sürüm, paket adı, açıklama ve imza bilgileri
- Android / APK üretiminde kullanılabilecek temel metadata

NOT:
- Bu modül saf Python sabitleri içerir
- Android / APK tarafında güvenle import edilebilir
"""

from __future__ import annotations


def _clean_text(value) -> str:
    return str(value or "").strip()


def _clean_int(value, fallback: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return int(fallback)


UYGULAMA_ADI = _clean_text("Fonksiyon Değiştirici")
PAKET_ADI = _clean_text("fonksiyon_degistirici")

SURUM = _clean_text("0.1.0")
BUILD = _clean_int(1, fallback=1)

TARIH = _clean_text("2026-03-10")
IMZA = _clean_text("FY.")

ACIKLAMA = _clean_text(
    "Python dosyalarındaki fonksiyonları ve nested function'ları "
    "arayüz üzerinden seçip güncellemek için geliştirilen uygulama."
)


def tam_surum() -> str:
    return f"{SURUM} ({BUILD})"


def apk_surum_kodu() -> int:
    """
    Android build numarası için kullanılabilecek sayısal sürüm kodu.
    """
    return BUILD


def apk_surum_adi() -> str:
    """
    Android / kullanıcı görünümü için sürüm adı.
    """
    return SURUM


def uygulama_etiketi() -> str:
    """
    Başlık / about / log alanlarında kullanılabilecek kısa uygulama etiketi.
    """
    return f"{UYGULAMA_ADI} v{SURUM}"


def meta_bilgisi() -> dict:
    """
    Toplu metadata çıktısı.
    Buildozer veya about ekranı gibi yerlerde kullanılabilir.
    """
    return {
        "uygulama_adi": UYGULAMA_ADI,
        "paket_adi": PAKET_ADI,
        "surum": SURUM,
        "build": BUILD,
        "tarih": TARIH,
        "imza": IMZA,
        "aciklama": ACIKLAMA,
        "tam_surum": tam_surum(),
    }
# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ortak/renkler.py

ROL:
- UI katmanının ortak renk sabitlerini tanımlar
- Tüm UI bileşenleri buradan beslenir
- Hardcoded renk kullanımını engeller

MİMARİ:
- Tek kaynak (single source of truth)
- Tema değişimine uygun yapı
- Geriye uyum korunur

SURUM: 3
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Final


# =========================================================
# TEMEL
# =========================================================
ARKAPLAN: Final[tuple[float, float, float, float]] = (0.08, 0.09, 0.11, 1.0)

KART: Final[tuple[float, float, float, float]] = (0.12, 0.13, 0.16, 1.0)
KART_ALT: Final[tuple[float, float, float, float]] = (0.15, 0.16, 0.19, 1.0)


# =========================================================
# METIN
# =========================================================
METIN: Final[tuple[float, float, float, float]] = (0.95, 0.96, 0.98, 1.0)
METIN_SOLUK: Final[tuple[float, float, float, float]] = (0.72, 0.75, 0.80, 1.0)
METIN_TERS: Final[tuple[float, float, float, float]] = (0.10, 0.11, 0.13, 1.0)

METIN_BASLIK: Final[tuple[float, float, float, float]] = METIN
METIN_ACIKLAMA: Final[tuple[float, float, float, float]] = METIN_SOLUK


# =========================================================
# DURUM
# =========================================================
VURGU: Final[tuple[float, float, float, float]] = (0.20, 0.55, 0.95, 1.0)
BASARI: Final[tuple[float, float, float, float]] = (0.20, 0.75, 0.35, 1.0)
UYARI: Final[tuple[float, float, float, float]] = (0.95, 0.65, 0.20, 1.0)
HATA: Final[tuple[float, float, float, float]] = (0.90, 0.25, 0.25, 1.0)

HATA_BASLIK: Final[tuple[float, float, float, float]] = HATA
HATA_METIN: Final[tuple[float, float, float, float]] = METIN
HATA_ACIKLAMA: Final[tuple[float, float, float, float]] = METIN_SOLUK


# =========================================================
# SINIR / CIZGI
# =========================================================
KENARLIK: Final[tuple[float, float, float, float]] = (0.24, 0.26, 0.30, 1.0)
AYIRICI: Final[tuple[float, float, float, float]] = (0.18, 0.20, 0.24, 1.0)

HATA_KARTI_KENARLIK: Final[tuple[float, float, float, float]] = KENARLIK


# =========================================================
# INPUT / EDITOR
# =========================================================
INPUT_ARKAPLAN: Final[tuple[float, float, float, float]] = (0.07, 0.08, 0.11, 1.0)
INPUT_ODAK: Final[tuple[float, float, float, float]] = (0.20, 0.55, 0.95, 1.0)
INPUT_IPUCU: Final[tuple[float, float, float, float]] = METIN_SOLUK

KOD_ARKAPLAN: Final[tuple[float, float, float, float]] = (0.06, 0.07, 0.10, 1.0)
KOD_SECIM: Final[tuple[float, float, float, float]] = (0.25, 0.45, 0.75, 0.35)

HATA_DETAY_ARKAPLAN: Final[tuple[float, float, float, float]] = INPUT_ARKAPLAN


# =========================================================
# BUTON
# =========================================================
BUTON: Final[tuple[float, float, float, float]] = (0.20, 0.22, 0.28, 1.0)
BUTON_HOVER: Final[tuple[float, float, float, float]] = (0.24, 0.26, 0.34, 1.0)
BUTON_PASIF: Final[tuple[float, float, float, float]] = (0.16, 0.17, 0.20, 1.0)

BUTON_METIN: Final[tuple[float, float, float, float]] = METIN
BUTON_METIN_PASIF: Final[tuple[float, float, float, float]] = METIN_SOLUK

HATA_BUTON: Final[tuple[float, float, float, float]] = BUTON
HATA_BUTON_METIN: Final[tuple[float, float, float, float]] = BUTON_METIN


# =========================================================
# LISTE / OGELER
# =========================================================
LISTE_OGE: Final[tuple[float, float, float, float]] = (0.18, 0.20, 0.26, 1.0)
LISTE_OGE_SECILI: Final[tuple[float, float, float, float]] = (0.22, 0.28, 0.38, 1.0)
LISTE_OGE_HOVER: Final[tuple[float, float, float, float]] = (0.20, 0.23, 0.30, 1.0)


# =========================================================
# OZEL
# =========================================================
SEFFAF: Final[tuple[float, float, float, float]] = (0.0, 0.0, 0.0, 0.0)
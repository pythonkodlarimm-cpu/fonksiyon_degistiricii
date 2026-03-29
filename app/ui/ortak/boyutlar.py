# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ortak/boyutlar.py

ROL:
- UI katmanının ortak ölçü sabitlerini tanımlar
- Tüm ekranlarda tek ölçek kaynağıdır
- Ham ölçüler + semantik ölçüler içerir

MİMARİ:
- dp() yalnızca burada kullanılır
- UI katmanı direkt dp kullanmaz
- Tutarlı spacing / radius / yükseklik sağlar
- Geriye uyumluluk korunmuştur

SURUM: 2
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from kivy.metrics import dp
from typing import Final


# =========================================================
# SPACING (HAM)
# =========================================================
BOSLUK_XXS: Final[float] = dp(4)
BOSLUK_XS: Final[float] = dp(6)
BOSLUK_SM: Final[float] = dp(8)
BOSLUK_MD: Final[float] = dp(12)
BOSLUK_LG: Final[float] = dp(16)
BOSLUK_XL: Final[float] = dp(20)


# =========================================================
# YÜKSEKLİKLER
# =========================================================
YUKSEKLIK_TOOLBAR: Final[float] = dp(56)
YUKSEKLIK_ALT_DURUM: Final[float] = dp(34)
YUKSEKLIK_BUTON: Final[float] = dp(44)
YUKSEKLIK_GIRDI: Final[float] = dp(42)


# =========================================================
# ICON
# =========================================================
ICON_16: Final[float] = dp(16)
ICON_20: Final[float] = dp(20)
ICON_24: Final[float] = dp(24)
ICON_28: Final[float] = dp(28)
ICON_32: Final[float] = dp(32)


# =========================================================
# RADIUS
# =========================================================
KART_RADIUS: Final[list[float]] = [dp(14)] * 4


# =========================================================
# 🔥 SEMANTIC BOYUTLAR (YENİ)
# =========================================================

# Panel padding
PADDING_KART: Final[float] = BOSLUK_SM
PADDING_IC: Final[float] = BOSLUK_XS

# Layout spacing
SPACING_SATIR: Final[float] = BOSLUK_XS
SPACING_BLOK: Final[float] = BOSLUK_SM
SPACING_BUYUK: Final[float] = BOSLUK_MD

# Alt kontrol paneli
YUKSEKLIK_ALT_PANEL: Final[float] = YUKSEKLIK_BUTON + BOSLUK_SM * 2

# Icon buton boyutu (tek merkez)
BUTON_ICON_BOYUT: Final[float] = YUKSEKLIK_BUTON + BOSLUK_SM

# Üst bar icon boyutu
UST_BAR_ICON_KAPSAYICI: Final[float] = YUKSEKLIK_TOOLBAR - BOSLUK_MD

# Metin alanları
YUKSEKLIK_MIN_KOD_ALANI: Final[float] = dp(120)

# Liste panel genişlik oranı
ORAN_SOL_PANEL: Final[float] = 0.40
ORAN_SAG_PANEL: Final[float] = 0.60
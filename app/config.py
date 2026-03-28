# -*- coding: utf-8 -*-
"""
DOSYA: app/config.py

ROL:
- Uygulama genel yapılandırmalarını tutar
- Test modunu merkezi olarak yönetir
- Developer mode kontrolünü sağlar
- UI ve servis davranışlarını merkezi flag'ler ile yönetir

MİMARİ:
- Tüm flag'ler tek noktadan yönetilir
- Default değerler güvenli (False)
- UI ve servis katmanı doğrudan buradan okuma yapar
- Fail-soft yaklaşım desteklenir

SURUM: 4
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations


# =========================================================
# ANA MODLAR
# =========================================================

# Test modu (debug davranışları, alternatif UI vs.)
TEST_MODU_AKTIF = False

# Geliştirici modu (gizli menüler, debug ekranları vs.)
DEVELOPER_MODE = False


# =========================================================
# DAVRANIŞ KONTROLLERİ
# =========================================================

def ayri_popup_dosya_secici_kullan() -> bool:
    """
    Test modu açıksa ayrı popup picker kullanılır.
    """
    return bool(TEST_MODU_AKTIF)


def developer_modu_aktif_mi() -> bool:
    """
    Developer mode aktif mi kontrol eder.
    UI tarafında doğrudan kullanılabilir.
    """
    return bool(DEVELOPER_MODE)


# =========================================================
# GENİŞLETME NOKTALARI (İLERİYE DÖNÜK)
# =========================================================

# İleride buraya eklenebilir:
# - LOG_SEVIYESI
# - CACHE_AKTIF
# - ANALYTICS_AKTIF
# - REKLAM_AKTIF
# - OFFLINE_MOD
#
# Tüm sistem bu dosyadan beslenecek şekilde tasarlanmalı

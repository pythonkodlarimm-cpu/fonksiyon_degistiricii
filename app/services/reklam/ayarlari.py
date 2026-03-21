# -*- coding: utf-8 -*-
"""
DOSYA: app/services/reklam/ayarlari.py

ROL:
- Reklam servisleri için ortak ayar ve sabitleri tutar
- Test/canlı reklam birim geçişini tek yerden yönetir
- Reklam katmanının UI akışını bozmadan merkezileşmesini sağlar
- Gelecekte interstitial / rewarded reklamlara genişletilebilir yapı sağlar

MİMARİ:
- Tüm reklam servisleri buradan beslenir
- Banner / interstitial / rewarded ayrımı buradan yönetilir
- Ortam (test/canlı) tek flag ile kontrol edilir

API UYUMLULUK:
- AdMob SDK uyumlu
- AndroidX uyumlu
- API 35 uyumlu

SURUM: 3
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations


# =========================================================
# ORTAM AYARI
# =========================================================

TEST_MODU: bool = True


def test_modu_aktif_mi() -> bool:
    return bool(TEST_MODU)


# =========================================================
# ADMOB GENEL
# =========================================================

ADMOB_APP_ID: str = "ca-app-pub-5522917995813710~6900495663"


# =========================================================
# BANNER
# =========================================================

TEST_BANNER_ID: str = "ca-app-pub-3940256099942544/9214589741"
CANLI_BANNER_ID: str = "ca-app-pub-5522917995813710/2607730157"


# =========================================================
# INTERSTITIAL
# =========================================================

TEST_INTERSTITIAL_ID: str = "ca-app-pub-3940256099942544/1033173712"
CANLI_INTERSTITIAL_ID: str = ""


# =========================================================
# REWARDED
# =========================================================

TEST_REWARDED_ID: str = "ca-app-pub-3940256099942544/5224354917"
CANLI_REWARDED_ID: str = ""


# =========================================================
# INTERNAL HELPER
# =========================================================

def _coalesce(test_id: str, live_id: str) -> str:
    """
    Canlı ID boşsa fallback olarak test ID döner.
    (kritik: boş reklam ID crash sebebi olur)
    """
    if test_modu_aktif_mi():
        return test_id

    live = str(live_id or "").strip()
    return live if live else test_id


# =========================================================
# AKTİF SEÇİCİLER
# =========================================================

def aktif_banner_reklam_id() -> str:
    return _coalesce(TEST_BANNER_ID, CANLI_BANNER_ID)


def aktif_interstitial_reklam_id() -> str:
    return _coalesce(TEST_INTERSTITIAL_ID, CANLI_INTERSTITIAL_ID)


def aktif_rewarded_reklam_id() -> str:
    return _coalesce(TEST_REWARDED_ID, CANLI_REWARDED_ID)
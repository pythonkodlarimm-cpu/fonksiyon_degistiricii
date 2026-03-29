# -*- coding: utf-8 -*-
"""
DOSYA: app/services/reklam/ayarlari.py

ROL:
- AdMob reklam ayarlarını tek merkezden yönetir
- Test / yayın modunu güvenli biçimde ayırır
- Banner / interstitial / rewarded reklam kimliklerini tek yerden sağlar
- Reklam servis dosyalarının sabit kalmasını sağlar

MİMARİ:
- Tüm reklam servisleri bu dosyadan beslenir
- Ortam seçimi tek merkezden yapılır
- Yanlış mod kombinasyonları engellenir
- Banner ve geçiş reklamı aynı ayar katmanından yönetilir

API UYUMLULUK:
- AdMob SDK uyumlu
- AndroidX uyumlu
- API 35 uyumlu

SURUM: 5
TARIH: 2026-03-22
IMZA: FY.
"""

from __future__ import annotations


# =========================================================
# MOD AYARLARI
# =========================================================
# Test aşamasında:
# TEST_REKLAM_MODU = True
# PLAY_STORE_YAYIN_MODU = False
#
# Canlı yayında:
# TEST_REKLAM_MODU = False
# PLAY_STORE_YAYIN_MODU = True
# =========================================================
TEST_REKLAM_MODU: bool = True
PLAY_STORE_YAYIN_MODU: bool = False


# =========================================================
# TEST REKLAM BİLGİLERİ
# Google resmi test kimlikleri
# =========================================================
TEST_ADMOB_APP_ID: str = "ca-app-pub-3940256099942544~3347511713"
TEST_BANNER_REKLAM_ID: str = "ca-app-pub-3940256099942544/9214589741"
TEST_INTERSTITIAL_REKLAM_ID: str = "ca-app-pub-3940256099942544/1033173712"
TEST_REWARDED_REKLAM_ID: str = "ca-app-pub-3940256099942544/5224354917"


# =========================================================
# CANLI REKLAM BİLGİLERİ
# Kendi gerçek AdMob kimliklerin
# =========================================================
GERCEK_ADMOB_APP_ID: str = "ca-app-pub-5522917995813710~6900495663"
GERCEK_BANNER_REKLAM_ID: str = "ca-app-pub-5522917995813710/2607730157"
GERCEK_INTERSTITIAL_REKLAM_ID: str = "ca-app-pub-5522917995813710/8789776927"
GERCEK_REWARDED_REKLAM_ID: str = ""


# =========================================================
# INTERNAL HELPERS
# =========================================================
def _mod_dogrula() -> None:
    if TEST_REKLAM_MODU and PLAY_STORE_YAYIN_MODU:
        raise ValueError(
            "Reklam ayarı hatası: TEST_REKLAM_MODU ve "
            "PLAY_STORE_YAYIN_MODU aynı anda True olamaz."
        )

    if not TEST_REKLAM_MODU and not PLAY_STORE_YAYIN_MODU:
        raise ValueError(
            "Reklam ayarı hatası: En az bir mod aktif olmalı. "
            "TEST_REKLAM_MODU veya PLAY_STORE_YAYIN_MODU True olmalı."
        )


def _gerekli_deger_kontrol_et(deger: str, alan_adi: str) -> str:
    temiz = str(deger or "").strip()
    if not temiz:
        raise ValueError(
            f"Reklam ayarı hatası: {alan_adi} boş bırakılamaz."
        )
    return temiz


def _aktif_id_getir(
    test_id: str,
    gercek_id: str,
    alan_adi: str,
) -> str:
    _mod_dogrula()

    if test_modu_aktif_mi():
        return _gerekli_deger_kontrol_et(test_id, f"TEST {alan_adi}")

    return _gerekli_deger_kontrol_et(gercek_id, f"GERCEK {alan_adi}")


# =========================================================
# MOD BİLGİLERİ
# =========================================================
def test_modu_aktif_mi() -> bool:
    _mod_dogrula()
    return bool(TEST_REKLAM_MODU)


def yayin_modu_aktif_mi() -> bool:
    _mod_dogrula()
    return bool(PLAY_STORE_YAYIN_MODU)


def reklam_modu_etiketi() -> str:
    _mod_dogrula()
    return "TEST" if TEST_REKLAM_MODU else "YAYIN"


# =========================================================
# AKTİF APP ID
# =========================================================
def aktif_admob_app_id() -> str:
    return _aktif_id_getir(
        TEST_ADMOB_APP_ID,
        GERCEK_ADMOB_APP_ID,
        "ADMOB_APP_ID",
    )


# =========================================================
# AKTİF BANNER
# =========================================================
def aktif_banner_reklam_id() -> str:
    return _aktif_id_getir(
        TEST_BANNER_REKLAM_ID,
        GERCEK_BANNER_REKLAM_ID,
        "BANNER_REKLAM_ID",
    )


# =========================================================
# AKTİF INTERSTITIAL
# =========================================================
def aktif_interstitial_reklam_id() -> str:
    return _aktif_id_getir(
        TEST_INTERSTITIAL_REKLAM_ID,
        GERCEK_INTERSTITIAL_REKLAM_ID,
        "INTERSTITIAL_REKLAM_ID",
    )


# =========================================================
# AKTİF REWARDED
# =========================================================
def aktif_rewarded_reklam_id() -> str:
    return _aktif_id_getir(
        TEST_REWARDED_REKLAM_ID,
        GERCEK_REWARDED_REKLAM_ID,
        "REWARDED_REKLAM_ID",
    )
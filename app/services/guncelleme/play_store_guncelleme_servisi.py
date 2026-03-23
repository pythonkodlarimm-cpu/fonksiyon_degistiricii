# -*- coding: utf-8 -*-
"""
DOSYA: app/services/guncelleme/play_store_guncelleme_servisi.py

ROL:
- Uygulamayı Play Store sayfasına yönlendirmek
- Android ortamında önce market intent denemek
- Gerekirse web Play Store bağlantısına güvenli fallback yapmak

MİMARİ:
- Önce Android bridge ile market:// açılmaya çalışılır
- Başarısız olursa https:// play store adresine düşülür
- Platform dışı ortamlarda güvenli no-op döner
- UI katmanı bu dosyayı doğrudan bilmez

API UYUMLULUK:
- Android API 35 uyumlu
- Google Play yönlendirme akışına uygundur
- Runtime izin gerektirmez

SURUM: 2
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from app.services.guncelleme.ayarlari import (
    PLAY_STORE_PACKAGE_NAME,
    play_store_market_url,
    play_store_web_url,
)


def _android_intent_ile_ac(url: str, package_name: str = "") -> bool:
    temiz_url = str(url or "").strip()
    temiz_paket = str(package_name or "").strip()

    if not temiz_url:
        return False

    try:
        from jnius import autoclass  # type: ignore
    except Exception:
        return False

    try:
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Intent = autoclass("android.content.Intent")
        Uri = autoclass("android.net.Uri")

        current_activity = PythonActivity.mActivity
        if current_activity is None:
            return False

        intent = Intent(Intent.ACTION_VIEW, Uri.parse(temiz_url))

        if temiz_paket:
            intent.setPackage(temiz_paket)

        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        current_activity.startActivity(intent)
        return True
    except Exception:
        return False


def play_store_sayfasini_ac(package_name: str = "") -> bool:
    paket = str(package_name or PLAY_STORE_PACKAGE_NAME).strip()
    if not paket:
        return False

    market_url = play_store_market_url(paket)
    web_url = play_store_web_url(paket)

    if _android_intent_ile_ac(market_url, package_name="com.android.vending"):
        return True

    if _android_intent_ile_ac(web_url):
        return True

    return False
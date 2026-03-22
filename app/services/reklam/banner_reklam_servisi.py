# -*- coding: utf-8 -*-
"""
DOSYA: app/services/reklam/banner_reklam_servisi.py

ROL:
- Android üzerinde AdMob banner reklamını gösterir
- Banner reklamı güvenli, gecikmeli ve tekrar planlama çakışması olmadan başlatır
- Test / yayın reklam birimini ayarlar modülünden alır

SURUM: 1
TARIH: 2026-03-22
IMZA: FY.
"""

from __future__ import annotations

from kivy.clock import Clock
from kivy.utils import platform

try:
    from android.runnable import run_on_ui_thread
except Exception:
    def run_on_ui_thread(func):
        return func


_BANNER_VIEW = None
_BANNER_DURUMU = {
    "baslatildi": False,
    "gosteriliyor": False,
    "planlandi": False,
}


def _debug(message: str) -> None:
    try:
        print("[BANNER_REKLAM]", str(message))
    except Exception:
        pass


def banner_baslatildi_mi() -> bool:
    return bool(_BANNER_DURUMU.get("baslatildi", False))


def banner_gosteriliyor_mu() -> bool:
    return bool(_BANNER_DURUMU.get("gosteriliyor", False))


def banner_planlandi_mi() -> bool:
    return bool(_BANNER_DURUMU.get("planlandi", False))


def _banner_gecikmeli_calis(*_args) -> None:
    _BANNER_DURUMU["planlandi"] = False
    sonuc = banner_goster()
    _debug(f"gecikmeli banner sonucu: {sonuc}")


def banner_goster_gecikmeli(delay: float = 1.5) -> bool:
    if platform != "android":
        _debug("gecikmeli başlatma iptal: android değil")
        return False

    if banner_gosteriliyor_mu():
        _debug("gecikmeli başlatma atlandı: banner zaten gösteriliyor")
        return True

    if banner_planlandi_mi():
        _debug("gecikmeli başlatma atlandı: banner zaten planlandı")
        return True

    _BANNER_DURUMU["planlandi"] = True
    Clock.schedule_once(_banner_gecikmeli_calis, delay)
    _debug(f"banner gecikmeli planlandı: {delay} sn")
    return True


@run_on_ui_thread
def banner_goster() -> bool:
    global _BANNER_VIEW

    if platform != "android":
        _debug("banner_goster iptal: android değil")
        return False

    if _BANNER_VIEW is not None and banner_gosteriliyor_mu():
        _debug("banner zaten aktif")
        return True

    try:
        from jnius import autoclass
        from app.services.reklam.ayarlari import (
            aktif_banner_reklam_id,
            reklam_modu_etiketi,
        )

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        AdView = autoclass("com.google.android.gms.ads.AdView")
        AdSize = autoclass("com.google.android.gms.ads.AdSize")
        AdRequestBuilder = autoclass("com.google.android.gms.ads.AdRequest$Builder")
        MobileAds = autoclass("com.google.android.gms.ads.MobileAds")
        FrameLayoutParams = autoclass("android.widget.FrameLayout$LayoutParams")
        Gravity = autoclass("android.view.Gravity")

        activity = PythonActivity.mActivity
        if activity is None:
            _debug("activity yok")
            _BANNER_DURUMU["gosteriliyor"] = False
            return False

        if not _BANNER_DURUMU["baslatildi"]:
            MobileAds.initialize(activity)
            _debug("MobileAds.initialize çalıştı")

        reklam_id = aktif_banner_reklam_id()
        reklam_modu = reklam_modu_etiketi()

        adview = AdView(activity)
        adview.setAdUnitId(reklam_id)
        adview.setAdSize(AdSize.BANNER)

        params = FrameLayoutParams(
            FrameLayoutParams.WRAP_CONTENT,
            FrameLayoutParams.WRAP_CONTENT,
        )
        params.gravity = Gravity.TOP | Gravity.RIGHT
        params.setMargins(120, 40, 20, 0)

        activity.addContentView(adview, params)

        ad_request = AdRequestBuilder().build()
        adview.loadAd(ad_request)

        _BANNER_VIEW = adview
        _BANNER_DURUMU["baslatildi"] = True
        _BANNER_DURUMU["gosteriliyor"] = True
        _BANNER_DURUMU["planlandi"] = False

        _debug(f"banner gösterildi | mod={reklam_modu}")
        return True

    except Exception as exc:
        _BANNER_VIEW = None
        _BANNER_DURUMU["baslatildi"] = False
        _BANNER_DURUMU["gosteriliyor"] = False
        _BANNER_DURUMU["planlandi"] = False
        _debug(f"hata: {exc}")
        return False


@run_on_ui_thread
def banner_gizle() -> bool:
    global _BANNER_VIEW

    if platform != "android":
        return False

    if _BANNER_VIEW is None:
        _BANNER_DURUMU["gosteriliyor"] = False
        _BANNER_DURUMU["planlandi"] = False
        return False

    try:
        parent = _BANNER_VIEW.getParent()
        if parent is not None:
            parent.removeView(_BANNER_VIEW)

        try:
            _BANNER_VIEW.destroy()
        except Exception:
            pass

        _BANNER_VIEW = None
        _BANNER_DURUMU["gosteriliyor"] = False
        _BANNER_DURUMU["planlandi"] = False

        _debug("banner gizlendi")
        return True

    except Exception as exc:
        _debug(f"gizleme hatası: {exc}")
        return False

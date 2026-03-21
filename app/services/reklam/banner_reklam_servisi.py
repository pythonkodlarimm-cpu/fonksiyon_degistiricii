# -*- coding: utf-8 -*-
"""
DOSYA: app/services/reklam/banner_reklam_servisi.py

ROL:
- Android üzerinde en altta sabit banner reklam göstermek
- AdMob banner akışını UI'den bağımsız servis katmanında tutmak
- Aynı banner'ın tekrar tekrar eklenmesini önlemek
- Başarısız olduğunda uygulama akışını bozmadan sessiz şekilde loglamak

MİMARİ:
- Sadece Android platformunda çalışır
- Native Android view oluşturur
- Kivy widget ağacına yük bindirmez
- Tekil banner mantığı kullanır
- UI thread üzerinde güvenli çalışır
- Reklam ayarlarını lazy import ile alır

API UYUMLULUK:
- API 35 uyumlu
- AndroidX uyumlu
- AdMob SDK ile uyumlu

SURUM: 2
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

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


@run_on_ui_thread
def banner_goster() -> bool:
    global _BANNER_VIEW

    if platform != "android":
        _debug("android dışı platformda banner gösterilmedi")
        return False

    if _BANNER_VIEW is not None and banner_gosteriliyor_mu():
        _debug("banner zaten aktif")
        return True

    try:
        from jnius import autoclass
        from app.services.reklam.reklam_ayarlari import aktif_banner_reklam_id

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        AdView = autoclass("com.google.android.gms.ads.AdView")
        AdSize = autoclass("com.google.android.gms.ads.AdSize")
        AdRequestBuilder = autoclass("com.google.android.gms.ads.AdRequest$Builder")
        MobileAds = autoclass("com.google.android.gms.ads.MobileAds")
        FrameLayoutParams = autoclass("android.widget.FrameLayout$LayoutParams")
        Gravity = autoclass("android.view.Gravity")

        activity = PythonActivity.mActivity
        if activity is None:
            _debug("activity alınamadı")
            return False

        MobileAds.initialize(activity)

        adview = AdView(activity)
        adview.setAdUnitId(aktif_banner_reklam_id())
        adview.setAdSize(AdSize.BANNER)

        params = FrameLayoutParams(
            FrameLayoutParams.MATCH_PARENT,
            FrameLayoutParams.WRAP_CONTENT,
        )
        params.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL

        activity.addContentView(adview, params)

        ad_request = AdRequestBuilder().build()
        adview.loadAd(ad_request)

        _BANNER_VIEW = adview
        _BANNER_DURUMU["baslatildi"] = True
        _BANNER_DURUMU["gosteriliyor"] = True

        _debug("banner başarıyla gösterildi")
        return True

    except Exception as exc:
        _BANNER_VIEW = None
        _BANNER_DURUMU["baslatildi"] = False
        _BANNER_DURUMU["gosteriliyor"] = False
        _debug(f"banner gösterme hatası: {exc}")
        return False


@run_on_ui_thread
def banner_gizle() -> bool:
    global _BANNER_VIEW

    if platform != "android":
        return False

    if _BANNER_VIEW is None:
        _BANNER_DURUMU["gosteriliyor"] = False
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
        _debug("banner gizlendi")
        return True

    except Exception as exc:
        _debug(f"banner gizleme hatası: {exc}")
        return False
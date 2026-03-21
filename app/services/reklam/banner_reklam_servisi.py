# -*- coding: utf-8 -*-
from __future__ import annotations

from kivy.utils import platform
from kivy.clock import Clock

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


# =========================================================
# 🚀 PERFORMANS: GECİKMELİ BAŞLAT (donmayı çözer)
# =========================================================
def banner_goster_gecikmeli(delay: float = 1.5) -> None:
    """
    Uygulama açıldıktan sonra banner'ı gecikmeli başlatır.
    Donma problemini çözer.
    """
    Clock.schedule_once(lambda dt: banner_goster(), delay)


# =========================================================
# 🎯 ANA BANNER GÖSTERME
# =========================================================
@run_on_ui_thread
def banner_goster() -> bool:
    global _BANNER_VIEW

    if platform != "android":
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
            _debug("activity yok")
            return False

        # 🔥 ÖNEMLİ: initialize sadece 1 kere çalışmalı
        if not _BANNER_DURUMU["baslatildi"]:
            MobileAds.initialize(activity)

        adview = AdView(activity)

        # TEST için:
        # adview.setAdUnitId("ca-app-pub-3940256099942544/6300978111")

        adview.setAdUnitId(aktif_banner_reklam_id())
        adview.setAdSize(AdSize.BANNER)

        # =========================================================
        # 🎯 KONUM: ÜST + SAĞ + MENU BOŞLUKLU
        # =========================================================
        params = FrameLayoutParams(
            FrameLayoutParams.WRAP_CONTENT,
            FrameLayoutParams.WRAP_CONTENT,
        )

        # TOP RIGHT
        params.gravity = Gravity.TOP | Gravity.RIGHT

        # 🔥 SOL BOŞLUK: menu.png için alan bırak
        # (cihaza göre oynatabilirsin)
        params.setMargins(120, 40, 20, 0)

        activity.addContentView(adview, params)

        ad_request = AdRequestBuilder().build()
        adview.loadAd(ad_request)

        _BANNER_VIEW = adview
        _BANNER_DURUMU["baslatildi"] = True
        _BANNER_DURUMU["gosteriliyor"] = True

        _debug("banner gösterildi")
        return True

    except Exception as exc:
        _BANNER_VIEW = None
        _BANNER_DURUMU["baslatildi"] = False
        _BANNER_DURUMU["gosteriliyor"] = False
        _debug(f"hata: {exc}")
        return False


# =========================================================
# 🧹 BANNER GİZLE
# =========================================================
@run_on_ui_thread
def banner_gizle() -> bool:
    global _BANNER_VIEW

    if platform != "android":
        return False

    if _BANNER_VIEW is None:
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
        _debug(f"gizleme hatası: {exc}")
        return False

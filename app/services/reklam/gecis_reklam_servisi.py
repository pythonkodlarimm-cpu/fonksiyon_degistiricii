# -*- coding: utf-8 -*-
"""
DOSYA: app/services/reklam/gecis_reklam_servisi.py

ROL:
- Geçiş reklamını (interstitial) yüklemek ve göstermek
- Reklam kapanınca bekleyen callback'i güvenli şekilde çalıştırmak
- Reklam gösterimi sonrası otomatik yeniden yükleme yapmak
- UI katmanını AdMob interstitial detaylarından izole etmek

MİMARİ:
- Reklam birimi kimliği ayarlari.py üzerinden alınır
- Android dışı platformlarda güvenli fallback döner
- Servis kendi iç durumunu modül seviyesinde tutar
- FullScreenContentCallback ile kapanış / hata / tekrar yükleme akışı yönetilir
- Üst katman sadece yükle, hazır mı, göster API'lerini kullanır

API UYUMLULUK:
- AdMob SDK uyumlu
- AndroidX uyumlu
- API 35 uyumlu
- Ana thread üzerinde çalışacak şekilde tasarlanmıştır

SURUM: 1
TARIH: 2026-03-22
IMZA: FY.
"""

from __future__ import annotations

from typing import Callable

from kivy.clock import Clock
from kivy.utils import platform

try:
    from android.runnable import run_on_ui_thread
except Exception:
    def run_on_ui_thread(func):
        return func


_GECIS_REKLAMI = None
_GECIS_REKLAMI_YUKLENIYOR = False
_GECIS_REKLAMI_GOSTERILIYOR = False
_BEKLEYEN_SONRASI_CALLBACK = None


def _debug(message: str) -> None:
    try:
        print("[GECIS_REKLAM]", str(message))
    except Exception:
        pass


def gecis_reklami_hazir_mi() -> bool:
    return _GECIS_REKLAMI is not None


def gecis_reklami_yukleniyor_mu() -> bool:
    return bool(_GECIS_REKLAMI_YUKLENIYOR)


def gecis_reklami_temizle() -> None:
    global _GECIS_REKLAMI
    global _GECIS_REKLAMI_YUKLENIYOR
    global _GECIS_REKLAMI_GOSTERILIYOR
    global _BEKLEYEN_SONRASI_CALLBACK

    _GECIS_REKLAMI = None
    _GECIS_REKLAMI_YUKLENIYOR = False
    _GECIS_REKLAMI_GOSTERILIYOR = False
    _BEKLEYEN_SONRASI_CALLBACK = None
    _debug("Geçiş reklamı state temizlendi.")


def _sonrasi_callback_calis() -> None:
    global _BEKLEYEN_SONRASI_CALLBACK

    callback = _BEKLEYEN_SONRASI_CALLBACK
    _BEKLEYEN_SONRASI_CALLBACK = None

    if callback is None:
        return

    try:
        callback()
    except Exception as exc:
        _debug(f"Sonrası callback hatası: {exc}")


def _yeniden_yuklemeyi_planla(delay: float = 0.35) -> None:
    try:
        Clock.schedule_once(lambda *_: gecis_reklami_yukle(), float(delay))
    except Exception as exc:
        _debug(f"Yeniden yükleme planlama hatası: {exc}")


@run_on_ui_thread
def gecis_reklami_yukle() -> bool:
    global _GECIS_REKLAMI_YUKLENIYOR

    if platform != "android":
        _debug("Yükleme iptal: android değil.")
        return False

    if _GECIS_REKLAMI is not None:
        _debug("Yükleme atlandı: reklam zaten hazır.")
        return True

    if _GECIS_REKLAMI_YUKLENIYOR:
        _debug("Yükleme atlandı: reklam zaten yükleniyor.")
        return True

    try:
        from jnius import PythonJavaClass
        from jnius import autoclass
        from jnius import java_method

        from app.services.reklam.ayarlari import aktif_interstitial_reklam_id

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        InterstitialAd = autoclass("com.google.android.gms.ads.interstitial.InterstitialAd")
        InterstitialAdLoadCallback = autoclass(
            "com.google.android.gms.ads.interstitial.InterstitialAdLoadCallback"
        )
        AdRequestBuilder = autoclass("com.google.android.gms.ads.AdRequest$Builder")

        activity = PythonActivity.mActivity
        if activity is None:
            _debug("Yükleme iptal: activity yok.")
            return False

        reklam_id = aktif_interstitial_reklam_id()
        ad_request = AdRequestBuilder().build()

        _GECIS_REKLAMI_YUKLENIYOR = True

        class _LoadCallback(PythonJavaClass):
            __javaclass__ = "com/google/android/gms/ads/interstitial/InterstitialAdLoadCallback"
            __javacontext__ = "app"

            @java_method(
                "(Lcom/google/android/gms/ads/interstitial/InterstitialAd;)V"
            )
            def onAdLoaded(self, interstitial_ad):
                global _GECIS_REKLAMI
                global _GECIS_REKLAMI_YUKLENIYOR

                _GECIS_REKLAMI = interstitial_ad
                _GECIS_REKLAMI_YUKLENIYOR = False
                _debug("Geçiş reklamı yüklendi.")

            @java_method("(Lcom/google/android/gms/ads/LoadAdError;)V")
            def onAdFailedToLoad(self, load_ad_error):
                global _GECIS_REKLAMI
                global _GECIS_REKLAMI_YUKLENIYOR

                _GECIS_REKLAMI = None
                _GECIS_REKLAMI_YUKLENIYOR = False

                try:
                    msg = str(load_ad_error.toString())
                except Exception:
                    msg = "bilinmeyen yükleme hatası"

                _debug(f"Geçiş reklamı yüklenemedi: {msg}")

        callback = _LoadCallback()
        InterstitialAd.load(
            activity,
            reklam_id,
            ad_request,
            callback,
        )

        _debug("Geçiş reklamı yükleme isteği gönderildi.")
        return True

    except Exception as exc:
        _GECIS_REKLAMI_YUKLENIYOR = False
        _debug(f"Geçiş reklamı yükleme hatası: {exc}")
        return False


@run_on_ui_thread
def gecis_reklami_goster(sonrasi_callback: Callable | None = None) -> bool:
    global _GECIS_REKLAMI
    global _GECIS_REKLAMI_GOSTERILIYOR
    global _BEKLEYEN_SONRASI_CALLBACK

    if platform != "android":
        _debug("Gösterim iptal: android değil.")
        try:
            if sonrasi_callback is not None:
                sonrasi_callback()
        except Exception as exc:
            _debug(f"Android dışı callback hatası: {exc}")
        return False

    if _GECIS_REKLAMI_GOSTERILIYOR:
        _debug("Gösterim atlandı: reklam zaten gösteriliyor.")
        return False

    if _GECIS_REKLAMI is None:
        _debug("Gösterim atlandı: hazır reklam yok.")
        try:
            if sonrasi_callback is not None:
                sonrasi_callback()
        except Exception as exc:
            _debug(f"Hazır reklam yok callback hatası: {exc}")

        _yeniden_yuklemeyi_planla()
        return False

    try:
        from jnius import PythonJavaClass
        from jnius import autoclass
        from jnius import java_method

        PythonActivity = autoclass("org.kivy.android.PythonActivity")

        activity = PythonActivity.mActivity
        if activity is None:
            _debug("Gösterim iptal: activity yok.")
            try:
                if sonrasi_callback is not None:
                    sonrasi_callback()
            except Exception as exc:
                _debug(f"Activity yok callback hatası: {exc}")
            return False

        class _FullScreenCallback(PythonJavaClass):
            __javaclass__ = "com/google/android/gms/ads/FullScreenContentCallback"
            __javacontext__ = "app"

            @java_method("()V")
            def onAdShowedFullScreenContent(self):
                global _GECIS_REKLAMI_GOSTERILIYOR
                _GECIS_REKLAMI_GOSTERILIYOR = True
                _debug("Geçiş reklamı gösterildi.")

            @java_method("()V")
            def onAdDismissedFullScreenContent(self):
                global _GECIS_REKLAMI
                global _GECIS_REKLAMI_GOSTERILIYOR

                _debug("Geçiş reklamı kapandı.")
                _GECIS_REKLAMI = None
                _GECIS_REKLAMI_GOSTERILIYOR = False

                _sonrasi_callback_calis()
                _yeniden_yuklemeyi_planla()

            @java_method("(Lcom/google/android/gms/ads/AdError;)V")
            def onAdFailedToShowFullScreenContent(self, ad_error):
                global _GECIS_REKLAMI
                global _GECIS_REKLAMI_GOSTERILIYOR

                try:
                    msg = str(ad_error.toString())
                except Exception:
                    msg = "bilinmeyen gösterim hatası"

                _debug(f"Geçiş reklamı gösterilemedi: {msg}")

                _GECIS_REKLAMI = None
                _GECIS_REKLAMI_GOSTERILIYOR = False

                _sonrasi_callback_calis()
                _yeniden_yuklemeyi_planla()

        _BEKLEYEN_SONRASI_CALLBACK = sonrasi_callback
        callback = _FullScreenCallback()

        _GECIS_REKLAMI.setFullScreenContentCallback(callback)
        _GECIS_REKLAMI.show(activity)

        _debug("Geçiş reklamı show çağrıldı.")
        return True

    except Exception as exc:
        _debug(f"Geçiş reklamı gösterim hatası: {exc}")
        try:
            if sonrasi_callback is not None:
                sonrasi_callback()
        except Exception as inner_exc:
            _debug(f"Gösterim hatası sonrası callback hatası: {inner_exc}")

        _GECIS_REKLAMI = None
        _GECIS_REKLAMI_GOSTERILIYOR = False
        _BEKLEYEN_SONRASI_CALLBACK = None
        _yeniden_yuklemeyi_planla()
        return False
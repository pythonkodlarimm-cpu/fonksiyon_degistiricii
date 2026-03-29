# -*- coding: utf-8 -*-
"""
DOSYA: app/services/reklam/banner_reklam_servisi.py

ROL:
- Android üzerinde AdMob banner reklamını gösterir
- Banner reklamı güvenli, gecikmeli ve tekrar planlama çakışması olmadan başlatır
- Test / yayın reklam birimini ayarlar modülünden alır
- Hata durumunda ayrıntılı log basar
- Hata oluşursa ekranda kopyalanabilir popup gösterir

MİMARİ:
- Banner görünürlüğü modül seviyesinde tutulur
- Aynı anda birden fazla banner eklenmesi engellenir
- Gecikmeli başlatma planlandı / yükleniyor / gösteriliyor durumlarıyla korunur
- Android dışında güvenli no-op davranışı döner
- Popup gösterimi Kivy ana thread'e schedule edilerek yapılır

NOTLAR:
- Bu sürüm mevcut davranışı bozmadan hata görünürlüğünü artırır
- Banner görünür kabulü load çağrısı sonrası korunmuştur
- Ama hata durumunda ayrıntılı traceback popup ile kullanıcıya sunulur
- Popup içeriği readonly TextInput içinde açılır ve kopyalanabilir

SURUM: 4
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import traceback

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
    "yukleniyor": False,
}


def _debug(message: str) -> None:
    """
    Banner debug log basar.
    """
    try:
        print("[BANNER_REKLAM]", str(message))
    except Exception:
        pass


def _show_error_popup(text: str) -> None:
    """
    Kopyalanabilir hata popup'ı gösterir.

    Args:
        text: Popup içinde gösterilecek hata metni.
    """
    try:
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        from kivy.core.clipboard import Clipboard
        from kivy.metrics import dp

        def _ui(_dt):
            try:
                content = BoxLayout(
                    orientation="vertical",
                    spacing=dp(8),
                    padding=dp(8),
                )

                txt = TextInput(
                    text=str(text or ""),
                    readonly=True,
                    multiline=True,
                    size_hint=(1, 1),
                )

                buton_satiri = BoxLayout(
                    orientation="horizontal",
                    size_hint=(1, None),
                    height=dp(48),
                    spacing=dp(8),
                )

                btn_kopyala = Button(
                    text="Kopyala",
                    size_hint=(1, 1),
                )
                btn_kapat = Button(
                    text="Kapat",
                    size_hint=(1, 1),
                )

                popup_ref = {"popup": None}

                def _copy(*_args):
                    try:
                        Clipboard.copy(txt.text or "")
                    except Exception:
                        pass

                def _close(*_args):
                    try:
                        if popup_ref["popup"] is not None:
                            popup_ref["popup"].dismiss()
                    except Exception:
                        pass

                btn_kopyala.bind(on_release=_copy)
                btn_kapat.bind(on_release=_close)

                buton_satiri.add_widget(btn_kopyala)
                buton_satiri.add_widget(btn_kapat)

                content.add_widget(txt)
                content.add_widget(buton_satiri)

                popup = Popup(
                    title="Reklam Hatası",
                    content=content,
                    size_hint=(0.95, 0.82),
                    auto_dismiss=True,
                )
                popup_ref["popup"] = popup
                popup.open()

            except Exception:
                _debug("Popup UI oluşturulamadı.")
                _debug(traceback.format_exc())

        Clock.schedule_once(_ui, 0)

    except Exception:
        _debug("Hata popup'ı gösterilemedi.")
        _debug(traceback.format_exc())


def _show_error(message: str, exc: Exception | None = None) -> None:
    """
    Hem log basar hem popup gösterir.

    Args:
        message: Ana hata mesajı.
        exc: Opsiyonel exception.
    """
    detay = str(message or "").strip()

    try:
        if exc is not None:
            detay = f"{detay}\n\n{exc}\n\n{traceback.format_exc()}"
    except Exception:
        pass

    _debug(detay)
    _show_error_popup(detay)


def banner_baslatildi_mi() -> bool:
    """
    Banner başlatıldı mı bilgisini döndürür.
    """
    return bool(_BANNER_DURUMU.get("baslatildi", False))


def banner_gosteriliyor_mu() -> bool:
    """
    Banner gösteriliyor mu bilgisini döndürür.
    """
    return bool(_BANNER_DURUMU.get("gosteriliyor", False))


def banner_planlandi_mi() -> bool:
    """
    Banner gecikmeli başlatma planlandı mı bilgisini döndürür.
    """
    return bool(_BANNER_DURUMU.get("planlandi", False))


def banner_yukleniyor_mu() -> bool:
    """
    Banner yükleniyor mu bilgisini döndürür.
    """
    return bool(_BANNER_DURUMU.get("yukleniyor", False))


def _banner_gecikmeli_calis(*_args) -> None:
    """
    Gecikmeli banner çağrısını çalıştırır.
    """
    _BANNER_DURUMU["planlandi"] = False

    try:
        sonuc = banner_goster()
        _debug(f"gecikmeli banner sonucu: {sonuc}")
    except Exception as exc:
        _BANNER_DURUMU["planlandi"] = False
        _BANNER_DURUMU["yukleniyor"] = False
        _BANNER_DURUMU["gosteriliyor"] = False
        _show_error("Gecikmeli banner çalıştırma hatası.", exc=exc)


def banner_goster_gecikmeli(delay: float = 1.5) -> bool:
    """
    Banner reklamı gecikmeli biçimde planlar.

    Args:
        delay: Saniye cinsinden gecikme.

    Returns:
        bool
    """
    try:
        if platform != "android":
            _debug("gecikmeli başlatma iptal: android değil")
            return False

        if banner_gosteriliyor_mu():
            _debug("gecikmeli başlatma atlandı: banner zaten gösteriliyor")
            return True

        if banner_planlandi_mi():
            _debug("gecikmeli başlatma atlandı: banner zaten planlandı")
            return True

        if banner_yukleniyor_mu():
            _debug("gecikmeli başlatma atlandı: banner zaten yükleniyor")
            return True

        _BANNER_DURUMU["planlandi"] = True
        Clock.schedule_once(_banner_gecikmeli_calis, float(delay))
        _debug(f"banner gecikmeli planlandı: {delay} sn")
        return True

    except Exception as exc:
        _BANNER_DURUMU["planlandi"] = False
        _BANNER_DURUMU["yukleniyor"] = False
        _BANNER_DURUMU["gosteriliyor"] = False
        _show_error("banner_goster_gecikmeli hatası.", exc=exc)
        return False


@run_on_ui_thread
def banner_goster() -> bool:
    """
    Android activity üzerine banner reklam eklemeyi dener.

    Returns:
        bool
    """
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
        ViewGroupLayoutParams = autoclass("android.view.ViewGroup$LayoutParams")

        activity = PythonActivity.mActivity
        if activity is None:
            _debug("activity yok")
            _BANNER_DURUMU["gosteriliyor"] = False
            _BANNER_DURUMU["yukleniyor"] = False
            return False

        if _BANNER_VIEW is not None:
            try:
                eski_parent = _BANNER_VIEW.getParent()
                if eski_parent is not None:
                    eski_parent.removeView(_BANNER_VIEW)
            except Exception:
                pass
            _BANNER_VIEW = None

        MobileAds.initialize(activity)
        _debug("MobileAds.initialize çalıştı")

        reklam_id = aktif_banner_reklam_id()
        reklam_modu = reklam_modu_etiketi()

        adview = AdView(activity)
        adview.setAdUnitId(reklam_id)
        adview.setAdSize(AdSize.BANNER)

        params = FrameLayoutParams(
            ViewGroupLayoutParams.WRAP_CONTENT,
            ViewGroupLayoutParams.WRAP_CONTENT,
        )
        params.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL
        params.setMargins(0, 0, 0, 0)

        activity.addContentView(adview, params)

        ad_request = AdRequestBuilder().build()

        _BANNER_VIEW = adview
        _BANNER_DURUMU["baslatildi"] = True
        _BANNER_DURUMU["gosteriliyor"] = True
        _BANNER_DURUMU["planlandi"] = False
        _BANNER_DURUMU["yukleniyor"] = False

        adview.loadAd(ad_request)

        _debug(f"banner load çağrıldı | mod={reklam_modu} | id={reklam_id}")
        return True

    except Exception as exc:
        _BANNER_VIEW = None
        _BANNER_DURUMU["baslatildi"] = False
        _BANNER_DURUMU["gosteriliyor"] = False
        _BANNER_DURUMU["planlandi"] = False
        _BANNER_DURUMU["yukleniyor"] = False
        _show_error("banner_goster hatası.", exc=exc)
        return False


@run_on_ui_thread
def banner_gizle() -> bool:
    """
    Mevcut banner view'ı kaldırmayı dener.

    Returns:
        bool
    """
    global _BANNER_VIEW

    if platform != "android":
        return False

    if _BANNER_VIEW is None:
        _BANNER_DURUMU["gosteriliyor"] = False
        _BANNER_DURUMU["planlandi"] = False
        _BANNER_DURUMU["yukleniyor"] = False
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
        _BANNER_DURUMU["yukleniyor"] = False

        _debug("banner gizlendi")
        return True

    except Exception as exc:
        _show_error("banner_gizle hatası.", exc=exc)
        return False
# -*- coding: utf-8 -*-
"""
DOSYA: app/services/android/ozel_izin_servisi.py

ROL:
- Android özel izinlerini kontrol etmek
- MANAGE_EXTERNAL_STORAGE durumunu sorgulamak
- Kullanıcıyı ilgili sistem ayar ekranına yönlendirmek

NOT:
- Bu servis yalnızca Android'de çalışır
- MANAGE_EXTERNAL_STORAGE runtime popup ile verilmez
- Kullanıcı ayarlar ekranına yönlendirilmelidir
- API 30+ için MANAGE_EXTERNAL_STORAGE desteklenir
- API 35 hedefiyle güvenli sürüm kontrolü içerir
- Android dışı ortamlarda kontrollü fallback sağlar

SURUM: 2
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from kivy.utils import platform


class AndroidOzelIzinServisiHatasi(ValueError):
    """Android özel izin işlemleri sırasında oluşan kontrollü hata."""


_ANDROID_CTX = None


def _debug(message: str) -> None:
    try:
        print("[ANDROID_OZEL_IZIN]", str(message))
    except Exception:
        pass


def _ensure_android() -> None:
    if platform != "android":
        raise AndroidOzelIzinServisiHatasi(
            "Bu servis yalnızca Android ortamında kullanılabilir."
        )


def _classes():
    global _ANDROID_CTX

    if _ANDROID_CTX is not None:
        return _ANDROID_CTX

    _ensure_android()

    try:
        from jnius import autoclass, cast  # type: ignore

        Intent = autoclass("android.content.Intent")
        Uri = autoclass("android.net.Uri")
        Environment = autoclass("android.os.Environment")
        Settings = autoclass("android.provider.Settings")
        BuildVersion = autoclass("android.os.Build$VERSION")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")

        current_activity = cast("android.app.Activity", PythonActivity.mActivity)
        if current_activity is None:
            raise AndroidOzelIzinServisiHatasi(
                "Geçerli Android activity alınamadı."
            )

        _ANDROID_CTX = {
            "Intent": Intent,
            "Uri": Uri,
            "Environment": Environment,
            "Settings": Settings,
            "BuildVersion": BuildVersion,
            "activity": current_activity,
        }
        return _ANDROID_CTX

    except AndroidOzelIzinServisiHatasi:
        raise
    except Exception as exc:
        raise AndroidOzelIzinServisiHatasi(
            "Android özel izin sınıfları yüklenemedi."
        ) from exc


def android_api_seviyesi() -> int:
    """
    Çalışan cihazın Android API seviyesini döndürür.
    Android değilse 0 döner.
    """
    if platform != "android":
        return 0

    try:
        BuildVersion = _classes()["BuildVersion"]
        return int(BuildVersion.SDK_INT)
    except Exception as exc:
        _debug(f"android_api_seviyesi alınamadı: {exc}")
        return 0


def tum_dosya_erisim_destekleniyor_mu() -> bool:
    """
    MANAGE_EXTERNAL_STORAGE desteği yalnızca API 30+ sürümlerde vardır.
    """
    return platform == "android" and android_api_seviyesi() >= 30


def tum_dosya_erisim_izni_var_mi() -> bool:
    """
    MANAGE_EXTERNAL_STORAGE verildi mi kontrol eder.
    API 30 altı sürümlerde False döner.
    """
    if not tum_dosya_erisim_destekleniyor_mu():
        return False

    try:
        Environment = _classes()["Environment"]
        return bool(Environment.isExternalStorageManager())
    except Exception as exc:
        _debug(f"tum_dosya_erisim_izni_var_mi kontrol hatası: {exc}")
        return False


def tum_dosya_erisim_ayarlari_ac() -> None:
    """
    Kullanıcıyı uygulamanın tüm dosya erişimi ayar ekranına yönlendirir.
    API 30+ gerektirir.
    """
    if not tum_dosya_erisim_destekleniyor_mu():
        raise AndroidOzelIzinServisiHatasi(
            "Tüm dosya erişimi ayarı bu Android sürümünde desteklenmiyor."
        )

    ctx = _classes()
    Intent = ctx["Intent"]
    Uri = ctx["Uri"]
    Settings = ctx["Settings"]
    current_activity = ctx["activity"]

    try:
        intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
        intent.setData(Uri.parse("package:" + current_activity.getPackageName()))
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        current_activity.startActivity(intent)
        _debug("uygulamaya özel tüm dosya erişimi ayarı açıldı")
        return
    except Exception as exc:
        _debug(f"uygulamaya özel ayar açılamadı, genel ekrana düşülecek: {exc}")

    try:
        intent = Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        current_activity.startActivity(intent)
        _debug("genel tüm dosya erişimi ayarı açıldı")
    except Exception as exc:
        raise AndroidOzelIzinServisiHatasi(
            "Tüm dosya erişimi ayar ekranı açılamadı."
        ) from exc


def uygulama_detay_ayarlari_ac() -> None:
    """
    Uygulama detay ayarlarını açar.
    """
    ctx = _classes()
    Intent = ctx["Intent"]
    Uri = ctx["Uri"]
    Settings = ctx["Settings"]
    current_activity = ctx["activity"]

    try:
        intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
        intent.setData(Uri.parse("package:" + current_activity.getPackageName()))
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        current_activity.startActivity(intent)
        _debug("uygulama detay ayarı açıldı")
    except Exception as exc:
        raise AndroidOzelIzinServisiHatasi(
            "Uygulama ayar ekranı açılamadı."
        ) from exc
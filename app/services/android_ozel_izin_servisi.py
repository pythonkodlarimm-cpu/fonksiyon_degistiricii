# -*- coding: utf-8 -*-
"""
DOSYA: app/services/android_ozel_izin_servisi.py

ROL:
- Android özel izinlerini kontrol etmek
- MANAGE_EXTERNAL_STORAGE durumunu sorgulamak
- Kullanıcıyı ilgili sistem ayar ekranına yönlendirmek

NOT:
- Bu servis yalnızca Android'de çalışır
- MANAGE_EXTERNAL_STORAGE runtime popup ile verilmez
- Kullanıcı ayarlar ekranına yönlendirilmelidir
"""

from __future__ import annotations

from kivy.utils import platform


class AndroidOzelIzinServisiHatasi(ValueError):
    """Android özel izin işlemleri sırasında oluşan kontrollü hata."""


def _ensure_android() -> None:
    if platform != "android":
        raise AndroidOzelIzinServisiHatasi(
            "Bu servis yalnızca Android ortamında kullanılabilir."
        )


def _classes():
    _ensure_android()

    try:
        from jnius import autoclass, cast  # type: ignore

        Intent = autoclass("android.content.Intent")
        Uri = autoclass("android.net.Uri")
        Environment = autoclass("android.os.Environment")
        Settings = autoclass("android.provider.Settings")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")

        current_activity = cast("android.app.Activity", PythonActivity.mActivity)

        return {
            "Intent": Intent,
            "Uri": Uri,
            "Environment": Environment,
            "Settings": Settings,
            "activity": current_activity,
        }
    except Exception as exc:
        raise AndroidOzelIzinServisiHatasi(
            "Android özel izin sınıfları yüklenemedi."
        ) from exc


def tum_dosya_erisim_izni_var_mi() -> bool:
    """
    MANAGE_EXTERNAL_STORAGE verildi mi kontrol eder.
    """
    if platform != "android":
        return False

    try:
        Environment = _classes()["Environment"]
        return bool(Environment.isExternalStorageManager())
    except Exception:
        return False


def tum_dosya_erisim_ayarlari_ac() -> None:
    """
    Kullanıcıyı uygulamanın tüm dosya erişimi ayar ekranına yönlendirir.
    """
    ctx = _classes()
    Intent = ctx["Intent"]
    Uri = ctx["Uri"]
    Settings = ctx["Settings"]
    current_activity = ctx["activity"]

    try:
        intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
        intent.setData(Uri.parse("package:" + current_activity.getPackageName()))
        current_activity.startActivity(intent)
        return
    except Exception:
        pass

    try:
        intent = Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
        current_activity.startActivity(intent)
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
        current_activity.startActivity(intent)
    except Exception as exc:
        raise AndroidOzelIzinServisiHatasi(
            "Uygulama ayar ekranı açılamadı."
        ) from exc
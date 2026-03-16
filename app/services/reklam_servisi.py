# -*- coding: utf-8 -*-
"""
DOSYA: app/services/reklam_servisi.py

ROL:
- AdMob reklamlarının yüklenmesini ve yönetilmesini sağlar
- Android bridge üzerinden AdMob SDK çağrısı yapar

NOT:
Şu anda TEST reklam kullanılmaktadır.
Google Play'e yüklemeden önce gerçek reklam birimi ile değiştirilmelidir.

TEST BANNER ID:
ca-app-pub-3940256099942544/6300978111

GERÇEK BANNER ID:
ca-app-pub-5522917995813710/2607730157
"""

from __future__ import annotations

from jnius import autoclass
from kivy.utils import platform


class ReklamServisi:

    # =========================================================
    # TEST REKLAM ID
    # =========================================================
    TEST_BANNER_ID = "ca-app-pub-3940256099942544/6300978111"

    # =========================================================
    # GERÇEK REKLAM ID
    # =========================================================
    REAL_BANNER_ID = "ca-app-pub-5522917995813710/2607730157"

    # =========================================================
    # REKLAM YÜKLE
    # =========================================================
    def reklam_yukle(self) -> None:
        """
        Banner reklamı yükler.

        Varsayılan olarak TEST reklam kullanılır.
        Yayın sürümünde REAL_BANNER_ID kullanılmalıdır.
        """

        if platform != "android":
            return

        try:
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity

            AdMobBridge = autoclass("org.fy.bridge.AdMobBridge")

            # AdMob SDK başlat
            AdMobBridge.initialize(activity)

            # TEST reklam yükle
            AdMobBridge.loadBanner(activity, self.TEST_BANNER_ID)

            print("[REKLAM] Test banner yüklendi")

        except Exception as exc:
            print("[REKLAM] yükleme hatası:", exc)

    # =========================================================
    # REKLAM GÖSTER
    # =========================================================
    def reklam_goster(self) -> None:

        if platform != "android":
            return

        try:
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity

            AdMobBridge = autoclass("org.fy.bridge.AdMobBridge")

            AdMobBridge.showBanner(activity)

            print("[REKLAM] Banner gösterildi")

        except Exception as exc:
            print("[REKLAM] gösterme hatası:", exc)

    # =========================================================
    # REKLAM KAPAT
    # =========================================================
    def reklam_kapat(self) -> None:

        if platform != "android":
            return

        try:
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity

            AdMobBridge = autoclass("org.fy.bridge.AdMobBridge")

            AdMobBridge.hideBanner(activity)

            print("[REKLAM] Banner gizlendi")

        except Exception as exc:
            print("[REKLAM] kapatma hatası:", exc)

    # =========================================================
    # REKLAM YOK ET
    # =========================================================
    def reklam_yok_et(self) -> None:

        if platform != "android":
            return

        try:
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity

            AdMobBridge = autoclass("org.fy.bridge.AdMobBridge")

            AdMobBridge.destroyBanner(activity)

            print("[REKLAM] Banner yok edildi")

        except Exception as exc:
            print("[REKLAM] yok etme hatası:", exc)


# =========================================================
# GLOBAL SERVİS NESNESİ
# =========================================================
reklam_servisi = ReklamServisi()
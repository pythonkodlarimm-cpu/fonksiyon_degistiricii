# -*- coding: utf-8 -*-
"""
DOSYA: app/services/reklam_servisi.py

ROL:
- AdMob reklamlarının yüklenmesini ve yönetilmesini sağlar
- Android bridge üzerinden AdMob SDK çağrısı yapar

NOT:
- Şu anda TEST reklam kullanılmaktadır.
- Google Play'e yüklemeden önce gerçek reklam birimi ile değiştirilmelidir.
- Bu sürüm manuel test moduna uyumludur.
- Reklam çağrısı artık açılışta zorunlu değildir; UI içinden butonla tetiklenebilir.

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
    # TEST / GERÇEK REKLAM ID
    # =========================================================
    TEST_BANNER_ID = "ca-app-pub-3940256099942544/6300978111"
    REAL_BANNER_ID = "ca-app-pub-5522917995813710/2607730157"

    def __init__(self) -> None:
        self._initialized = False
        self._banner_yuklendi = False
        self._son_kullanilan_id = self.TEST_BANNER_ID

    # =========================================================
    # INTERNAL
    # =========================================================
    def _android_bridge(self):
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = PythonActivity.mActivity
        AdMobBridge = autoclass("org.fy.bridge.AdMobBridge")
        return activity, AdMobBridge

    # =========================================================
    # REKLAM YÜKLE
    # =========================================================
    def reklam_yukle(self, use_real_ad: bool = False) -> None:
        """
        Banner reklamı yükler.

        Varsayılan:
        - TEST reklam kullanılır.

        use_real_ad=True verilirse gerçek reklam birimi kullanılır.
        Yayın sürümünde gerçek reklam birimi tercih edilmelidir.
        """

        if platform != "android":
            print("[REKLAM] Android dışında reklam yükleme atlandı")
            return

        try:
            activity, AdMobBridge = self._android_bridge()

            if not self._initialized:
                AdMobBridge.initialize(activity)
                self._initialized = True
                print("[REKLAM] AdMob initialize tamamlandı")

            ad_unit_id = self.REAL_BANNER_ID if use_real_ad else self.TEST_BANNER_ID
            self._son_kullanilan_id = ad_unit_id

            AdMobBridge.loadBanner(activity, ad_unit_id)
            self._banner_yuklendi = True

            if use_real_ad:
                print("[REKLAM] Gerçek banner yüklendi")
            else:
                print("[REKLAM] Test banner yüklendi")

        except Exception as exc:
            self._banner_yuklendi = False
            print("[REKLAM] yükleme hatası:", exc)

    # =========================================================
    # REKLAM GÖSTER
    # =========================================================
    def reklam_goster(self) -> None:
        """
        Daha önce yüklenmiş banner varsa görünür hale getirir.
        """

        if platform != "android":
            print("[REKLAM] Android dışında reklam gösterme atlandı")
            return

        try:
            if not self._banner_yuklendi:
                print("[REKLAM] Banner henüz yüklenmedi, önce reklam_yukle çağrılmalı")
                return

            activity, AdMobBridge = self._android_bridge()
            AdMobBridge.showBanner(activity)

            print("[REKLAM] Banner gösterildi")

        except Exception as exc:
            print("[REKLAM] gösterme hatası:", exc)

    # =========================================================
    # REKLAM KAPAT
    # =========================================================
    def reklam_kapat(self) -> None:
        """
        Yüklü banner varsa görünmez hale getirir.
        """

        if platform != "android":
            print("[REKLAM] Android dışında reklam gizleme atlandı")
            return

        try:
            activity, AdMobBridge = self._android_bridge()
            AdMobBridge.hideBanner(activity)

            print("[REKLAM] Banner gizlendi")

        except Exception as exc:
            print("[REKLAM] kapatma hatası:", exc)

    # =========================================================
    # REKLAM YOK ET
    # =========================================================
    def reklam_yok_et(self) -> None:
        """
        Banner nesnesini tamamen yok eder.
        Tekrar kullanmak için yeniden reklam_yukle çağrılmalıdır.
        """

        if platform != "android":
            print("[REKLAM] Android dışında reklam yok etme atlandı")
            return

        try:
            activity, AdMobBridge = self._android_bridge()
            AdMobBridge.destroyBanner(activity)

            self._banner_yuklendi = False

            print("[REKLAM] Banner yok edildi")

        except Exception as exc:
            print("[REKLAM] yok etme hatası:", exc)

    # =========================================================
    # DURUM
    # =========================================================
    def reklam_hazir_mi(self) -> bool:
        return bool(self._banner_yuklendi)

    def test_modu_mu(self) -> bool:
        return self._son_kullanilan_id == self.TEST_BANNER_ID


# =========================================================
# GLOBAL SERVİS NESNESİ
# =========================================================
reklam_servisi = ReklamServisi()

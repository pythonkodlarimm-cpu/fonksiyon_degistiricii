# -*- coding: utf-8 -*-
"""
DOSYA: app/services/sistem/premium_servisi.py

ROL:
- Premium durumunu Android Billing bridge üzerinden kontrol etmek
- Android dışı ortamlarda güvenli fallback sağlamak
- Şu an aktif kullanılmaz, altyapı hazır tutulur

MİMARİ:
- Android'de Java bridge ile konuşur
- BillingBridge üzerinden premium durumunu sorgular
- Android dışı ortamlarda False döner
- Hata durumlarında uygulamayı düşürmez

API UYUMLULUK:
- API 35 uyumlu olacak şekilde güvenli fallback içerir
- Activity ve bridge yükleme kontrolleri yapılır
- Bridge hatalarında crash yerine False döner

NOT:
- Şu an aktif kullanılmamaktadır
- İleride app/services/premium/ paketi olarak ayrılabilir

SURUM: 3
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from kivy.utils import platform


class PremiumServisi:
    """
    Premium durumunu sorgulayan servis.
    """

    def _android_bridge(self):
        """
        Android activity ve BillingBridge sınıfını döndürür.
        """
        from jnius import autoclass, cast  # type: ignore

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = cast("android.app.Activity", PythonActivity.mActivity)

        if activity is None:
            raise ValueError("Android activity alınamadı.")

        BillingBridge = autoclass("org.fy.bridge.BillingBridge")
        return activity, BillingBridge

    def premium_aktif_mi(self) -> bool:
        """
        Premium durumunu kontrol eder.

        Dönüş:
        - True: premium aktif
        - False: premium değil veya kontrol başarısız
        """

        # Android dışı her ortamda direkt kapalı
        if platform != "android":
            return False

        try:
            activity, BillingBridge = self._android_bridge()

            # init güvenli çağrı (tekrar çağrılabilir)
            BillingBridge.init(activity)

            return bool(BillingBridge.isPremiumActive())

        except Exception as exc:
            # Crash yerine kontrollü fallback
            try:
                print("[PREMIUM] kontrol hatasi:", exc)
            except Exception:
                pass
            return False


# =========================================================
# GLOBAL SERVİS NESNESİ (pasif hazır)
# =========================================================
premium_servisi = PremiumServisi()
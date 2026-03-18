# -*- coding: utf-8 -*-
"""
DOSYA: app/services/premium_servisi.py

ROL:
- Premium durumunu Android Billing bridge üzerinden kontrol etmek
- Android dışı ortamlarda güvenli fallback sağlamak

MİMARİ:
- Android'de Java bridge ile konuşur
- BillingBridge üzerinden premium durumunu sorgular
- Android dışı ortamlarda False döner

API UYUMLULUK DEĞERLENDİRMESİ:
- Bu servis doğrudan Android bridge kullandığı için API değişimlerinden etkilenebilir
- API 34 hedefi için activity ve class yükleme kontrolleri eklenmiştir
- Bridge yüklenemezse veya activity alınamazsa kontrollü şekilde False döner

SURUM: 2
TARIH: 2026-03-17
IMZA: FY.
"""

from __future__ import annotations

from kivy.utils import platform


class PremiumServisi:
    """
    Premium durumunu sorgulayan servis.

    API 34 uyumluluk notu:
    - Android bridge çağrıları öncesinde platform ve activity kontrolleri yapılır.
    """

    def _android_bridge(self):
        """
        Android activity ve BillingBridge sınıfını döndürür.

        Dönüş:
        - (activity, BillingBridge)

        Hata:
        - Bridge veya activity alınamazsa Exception yükseltir
        """
        from jnius import autoclass, cast  # type: ignore

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        current_activity = cast("android.app.Activity", PythonActivity.mActivity)
        if current_activity is None:
            raise ValueError("Android activity alınamadı.")

        BillingBridge = autoclass("org.fy.bridge.BillingBridge")
        return current_activity, BillingBridge

    def premium_aktif_mi(self) -> bool:
        """
        Premium durumunu kontrol eder.

        Dönüş:
        - True: premium aktif
        - False: premium değil veya kontrol başarısız

        API 34 uyumluluk notu:
        - Android dışı ortamlarda False döner
        - Bridge tarafı hata verirse uygulamayı düşürmeden False döner
        """
        if platform != "android":
            return False

        try:
            activity, BillingBridge = self._android_bridge()

            BillingBridge.init(activity)

            return bool(BillingBridge.isPremiumActive())

        except Exception as exc:
            print("[PREMIUM] kontrol hatasi:", exc)
            return False


# GLOBAL SERVİS NESNESİ
premium_servisi = PremiumServisi()
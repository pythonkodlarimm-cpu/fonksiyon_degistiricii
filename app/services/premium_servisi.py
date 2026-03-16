# -*- coding: utf-8 -*-

from __future__ import annotations

from jnius import autoclass
from kivy.utils import platform


class PremiumServisi:

    def premium_aktif_mi(self) -> bool:

        if platform != "android":
            return False

        try:

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity

            BillingBridge = autoclass("org.fy.bridge.BillingBridge")

            BillingBridge.init(activity)

            return BillingBridge.isPremiumActive()

        except Exception as exc:

            print("[PREMIUM] kontrol hatasi:", exc)

            return False


# GLOBAL SERVİS NESNESİ
premium_servisi = PremiumServisi()
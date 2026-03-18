# -*- coding: utf-8 -*-
from __future__ import annotations

from kivy.utils import platform


def erisim_durumu_getir(debug=None):
    if platform != "android":
        return False

    try:
        from app.services.android_ozel_izin_servisi import tum_dosya_erisim_izni_var_mi
        return bool(tum_dosya_erisim_izni_var_mi())
    except Exception as exc:
        if debug:
            debug(f"Durum okuma hatası: {exc}")
        return None
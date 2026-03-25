# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/durum/yoneticisi.py

ROL:
- Root durum katmanına tek giriş noktası sağlamak
- RootStatusMixin erişimini merkezileştirmek
- Üst katmanın durum modülü detaylarını bilmesini engellemek

MİMARİ:
- Lazy import kullanır
- RootStatusMixin sınıfını tek noktadan sunar
- Fail-soft yaklaşım için tanılama logu bırakır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 2
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

import traceback


class RootDurumYoneticisi:
    def mixin_sinifi(self):
        try:
            from app.ui.root_paketi.durum.status import RootStatusMixin
            return RootStatusMixin
        except Exception:
            print("[ROOT_DURUM_YONETICI] RootStatusMixin yüklenemedi.")
            print(traceback.format_exc())
            raise

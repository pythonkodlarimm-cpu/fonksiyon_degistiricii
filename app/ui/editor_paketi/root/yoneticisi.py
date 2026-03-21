# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/root/yoneticisi.py

ROL:
- Root alt paketine tek giriş noktası sağlamak
- RootWidget sınıfını merkezileştirmek
- Üst katmanın root modülü detaylarını bilmesini engellemek

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- RootWidget doğrudan import edilmez
- Editor panel tabanlı root oluşturma burada toplanır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations


class RootYoneticisi:
    def root_sinifi(self):
        from app.ui.editor_paketi.root.root_widget import RootWidget
        return RootWidget

    def root_olustur(self, **kwargs):
        sinif = self.root_sinifi()
        return sinif(**kwargs)
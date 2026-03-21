# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/bildirim/yoneticisi.py

ROL:
- Bildirim alt paketine tek giriş noktası sağlamak
- Editör içi aksiyon bildirimi bileşenini merkezileştirmek
- Üst katmanın bildirim modülü detaylarını bilmesini engellemek

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt bildirim modülü doğrudan dışarı açılmaz
- Inline aksiyon bildirimi üretimi burada toplanır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations


class BildirimYoneticisi:
    def bildirim_sinifi(self):
        from app.ui.editor_paketi.bildirim.editor_bildirimleri import (
            EditorAksiyonBildirimi,
        )
        return EditorAksiyonBildirimi

    def bildirim_olustur(self, **kwargs):
        sinif = self.bildirim_sinifi()
        return sinif(**kwargs)
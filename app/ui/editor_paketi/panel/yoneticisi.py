# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/panel/yoneticisi.py

ROL:
- Panel alt paketine tek giriş noktası sağlamak
- EditorPaneli sınıfını merkezileştirmek
- Üst katmanın panel modülü detaylarını bilmesini engellemek

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt panel modülü doğrudan dışarı açılmaz
- EditorPaneli üretimi burada toplanır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations


class PanelYoneticisi:
    def panel_sinifi(self):
        from app.ui.editor_paketi.panel.editor_paneli import EditorPaneli
        return EditorPaneli

    def panel_olustur(self, **kwargs):
        sinif = self.panel_sinifi()
        return sinif(**kwargs)
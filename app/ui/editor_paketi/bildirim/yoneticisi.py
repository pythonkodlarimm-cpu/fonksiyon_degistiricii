# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/bildirim/yoneticisi.py

ROL:
- Bildirim alt paketine tek giriş noktası sağlamak
- Editör içi aksiyon bildirimi bileşenini merkezileştirmek
- Üst katmanın bildirim modülü detaylarını bilmesini engellemek
- Bildirim oluştururken üst katmandan gelen bağımlılıkları güvenli biçimde aşağı taşımak

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt bildirim modülü doğrudan dışarı açılmaz
- Inline aksiyon bildirimi üretimi burada toplanır
- Lazy import kullanır
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


class BildirimYoneticisi:
    def bildirim_sinifi(self):
        try:
            from app.ui.editor_paketi.bildirim.editor_bildirimleri import (
                EditorAksiyonBildirimi,
            )
            return EditorAksiyonBildirimi
        except Exception:
            print("[EDITOR_BILDIRIM_YONETICI] EditorAksiyonBildirimi sınıfı yüklenemedi.")
            print(traceback.format_exc())
            raise

    def bildirim_olustur(self, **kwargs):
        try:
            sinif = self.bildirim_sinifi()
            return sinif(**kwargs)
        except Exception:
            print("[EDITOR_BILDIRIM_YONETICI] Bildirim bileşeni oluşturulamadı.")
            print(traceback.format_exc())
            raise

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dil_paketi/yoneticisi.py

ROL:
- Dil UI katmanı için tek giriş noktası sağlamak
- Dil seçme popup'ını üst katman için kolay erişilebilir hale getirmek
- UI katmanının popup detaylarını bilmesini engellemek

MİMARİ:
- Popup sınıfına lazy import ile erişir
- Root ve diğer UI katmanları sadece bu yöneticiyi bilir
- Dil popup'ının iç detaylarını dışarı sızdırmaz
- İleride dil ayar kartı, dil satırı bileşeni gibi yapılar eklenmeye uygundur

API UYUMLULUK:
- Android API 35 uyumlu
- Android ve masaüstünde güvenli çalışır
- Platform bağımsız UI akışına uygundur

SURUM: 1
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations


class DilYoneticisi:
    def popup_olustur(self, services=None, on_language_changed=None):
        from app.ui.dil_paketi.popup import DilSecimPopup
        return DilSecimPopup(
            services=services,
            on_language_changed=on_language_changed,
        )

    def popup_ac(self, services=None, on_language_changed=None):
        popup = self.popup_olustur(
            services=services,
            on_language_changed=on_language_changed,
        )
        popup.open()
        return popup
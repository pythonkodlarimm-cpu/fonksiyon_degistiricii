# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dil_paketi/popup/yoneticisi.py

ROL:
- Dil popup katmanı için tek giriş noktası sağlamak
- DilSecimPopup oluşturma ve açma işini merkezileştirmek
- Üst katmanın popup sınıf detaylarını bilmesini engellemek

MİMARİ:
- DilSecimPopup sınıfına lazy import ile erişir
- Popup alt katmanını dış dünyadan soyutlar
- Üst katman sadece bu yöneticiyi kullanarak popup açabilir
- İleride farklı dil popup varyantları eklenirse tek noktadan yönetilebilir

API UYUMLULUK:
- Android API 35 uyumlu
- Android ve masaüstünde güvenli çalışır
- Platform bağımsız UI akışına uygundur

SURUM: 1
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations


class DilPopupYoneticisi:
    def popup_olustur(self, services=None, on_language_changed=None):
        from app.ui.dil_paketi.popup.dil_secim_popup import DilSecimPopup
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
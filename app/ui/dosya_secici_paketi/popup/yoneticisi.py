# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/popup/yoneticisi.py

ROL:
- Popup alt paketine tek giriş noktası sağlamak
- Bilgi popup akışını merkezileştirmek
- Üst katmanın popup detaylarını bilmesini engellemek

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt popup modülleri doğrudan dışarı açılmaz
- İleride hata/onay popup'ları için genişletilebilir

API UYUMLULUK:
- Platform bağımsızdır
- Kivy popup tabanlı güvenli UI akışı kullanır
- Android API 35 ile uyumludur

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations


class PopupYoneticisi:
    def bilgi_goster(self, owner, title: str, message: str):
        from app.ui.dosya_secici_paketi.popup.info_popup import show_info_popup
        return show_info_popup(owner=owner, title=title, message=message)
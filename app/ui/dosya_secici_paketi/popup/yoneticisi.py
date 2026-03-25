# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/popup/yoneticisi.py

ROL:
- Popup alt paketine tek giriş noktası sağlamak
- Bilgi popup akışını merkezileştirmek
- Üst katmanın popup detaylarını bilmesini engellemek
- Popup çağrılarını lazy import ile güvenli biçimde yönlendirmek

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt popup modülleri doğrudan dışarı açılmaz
- İleride hata / onay / seçim popup'ları için genişletilebilir
- Fail-soft yaklaşım korunur
- Lazy import kullanır

API UYUMLULUK:
- Platform bağımsızdır
- Kivy popup tabanlı güvenli UI akışı kullanır
- Android API 35 ile uyumludur

SURUM: 2
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

import traceback


class PopupYoneticisi:
    def _info_popup_modulu(self):
        try:
            from app.ui.dosya_secici_paketi.popup.info_popup import show_info_popup
            return show_info_popup
        except Exception:
            print("[DOSYA_SECICI_POPUP_YONETICI] info_popup modülü yüklenemedi.")
            print(traceback.format_exc())
            raise

    def bilgi_goster(self, owner, title: str, message: str):
        try:
            popup_goster = self._info_popup_modulu()
            return popup_goster(
                owner=owner,
                title=title,
                message=message,
            )
        except Exception:
            print("[DOSYA_SECICI_POPUP_YONETICI] bilgi_goster çağrısı başarısız.")
            print(traceback.format_exc())
            return None

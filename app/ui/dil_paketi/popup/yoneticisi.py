# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dil_paketi/popup/yoneticisi.py

ROL:
- Dil popup katmanı için tek giriş noktası sağlamak
- DilSecimPopup oluşturma ve açma işini merkezileştirmek
- Üst katmanın popup sınıf detaylarını bilmesini engellemek
- diller/ klasöründen otomatik algılanan dil listesini kullanan popup akışını tek yerden açmak

MİMARİ:
- DilSecimPopup sınıfına lazy import ile erişir
- Popup alt katmanını dış dünyadan soyutlar
- Üst katman sadece bu yöneticiyi kullanarak popup açabilir
- İleride farklı dil popup varyantları eklenirse tek noktadan yönetilebilir
- Fail-soft yaklaşım kullanır

API UYUMLULUK:
- Android API 35 uyumlu
- Android ve masaüstünde güvenli çalışır
- Platform bağımsız UI akışına uygundur

SURUM: 4
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import traceback


class DilPopupYoneticisi:
    def _debug(self, message: str) -> None:
        try:
            print(f"[DIL_POPUP_YONETICI] {message}")
        except Exception:
            pass

    def popup_sinifi(self):
        """
        Popup sınıfını lazy import ile döndürür.
        """
        try:
            from app.ui.dil_paketi.popup.dil_secim_popup import DilSecimPopup
            return DilSecimPopup
        except Exception:
            self._debug("Popup sınıfı yüklenemedi.")
            self._debug(traceback.format_exc())
            raise

    def popup_olustur(self, services=None, on_language_changed=None):
        """
        Popup instance oluşturur.
        """
        try:
            popup_cls = self.popup_sinifi()
            return popup_cls(
                services=services,
                on_language_changed=on_language_changed,
            )
        except Exception:
            self._debug("Popup oluşturulamadı.")
            self._debug(traceback.format_exc())
            raise

    def popup_ac(self, services=None, on_language_changed=None):
        """
        Popup açar.
        """
        try:
            popup = self.popup_olustur(
                services=services,
                on_language_changed=on_language_changed,
            )

            if popup is not None:
                return popup.open()

            return None

        except Exception:
            self._debug("Popup açılamadı.")
            self._debug(traceback.format_exc())
            return None

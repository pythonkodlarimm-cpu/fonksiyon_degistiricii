# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dil_paketi/yoneticisi.py

ROL:
- Dil UI katmanı için tek giriş noktası sağlamak
- Dil popup'ını üst katman için kolay erişilebilir hale getirmek
- UI katmanının popup detaylarını bilmesini engellemek
- Popup katmanına sadece yöneticisi üzerinden erişim sağlamak

MİMARİ:
- DilPopupYoneticisi'ne lazy import ile erişir
- Root ve diğer UI katmanları sadece bu yöneticiyi bilir
- Popup implementasyonu tamamen gizlidir
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


class DilYoneticisi:
    def _debug(self, message: str) -> None:
        try:
            print(f"[DIL_YONETICI] {message}")
        except Exception:
            pass

    def _popup_yoneticisi(self):
        """
        Popup yöneticisini lazy import ile döndürür.
        """
        try:
            from app.ui.dil_paketi.popup import DilPopupYoneticisi
            return DilPopupYoneticisi()
        except Exception:
            self._debug("Popup yöneticisi yüklenemedi.")
            self._debug(traceback.format_exc())
            raise

    def popup_olustur(self, services=None, on_language_changed=None):
        """
        Popup instance oluşturur.
        """
        try:
            return self._popup_yoneticisi().popup_olustur(
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
            return self._popup_yoneticisi().popup_ac(
                services=services,
                on_language_changed=on_language_changed,
            )
        except Exception:
            self._debug("Popup açılamadı.")
            self._debug(traceback.format_exc())
            return None

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/gorunum_akisi/yoneticisi.py

ROL:
- Görünüm akışı alt paketine tek giriş noktası sağlamak
- Fonksiyon listesi görünüm açma / kapama akışını merkezileştirmek
- Üst katmanın görünüm akışı modül detaylarını bilmesini engellemek
- Toggle ikon ve görünüm senkronizasyon çağrılarını güvenli biçimde yönlendirmek
- Dil yenileme sırasında görünüm metinlerinin doğru uygulanmasına yardımcı olmak

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt görünüm akışı modülü doğrudan dışarı açılmaz
- Liste görünüm davranışı bu yönetici üzerinden çağrılır
- Lazy import kullanır
- Fail-soft yaklaşım için tanılama logu bırakır
- Düşük seviyeli hata durumlarında uygulamayı gereksiz yere çökertmez

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 3
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import traceback


class GorunumAkisiYoneticisi:
    def _debug(self, message: str) -> None:
        try:
            print(f"[FONKSIYON_LISTESI_GORUNUM_YONETICI] {message}")
        except Exception:
            pass

    def _modul(self):
        try:
            from app.ui.fonksiyon_listesi_paketi.gorunum_akisi import gorunum_akisi
            return gorunum_akisi
        except Exception:
            self._debug("Görünüm akışı modülü yüklenemedi.")
            self._debug(traceback.format_exc())
            raise

    def set_toggle_icon(self, owner, icon_name: str) -> None:
        try:
            self._modul().set_toggle_icon(owner, icon_name)
        except Exception:
            self._debug("set_toggle_icon çağrısı başarısız.")
            self._debug(traceback.format_exc())

    def update_toggle_icon(self, owner) -> None:
        try:
            self._modul().update_toggle_icon(owner)
        except Exception:
            self._debug("update_toggle_icon çağrısı başarısız.")
            self._debug(traceback.format_exc())

    def toggle_list_visibility(self, owner, *_args) -> None:
        try:
            self._modul().toggle_list_visibility(owner, *_args)
        except Exception:
            self._debug("toggle_list_visibility çağrısı başarısız.")
            self._debug(traceback.format_exc())

    def sync_list_visibility(self, owner) -> None:
        try:
            self._modul().sync_list_visibility(owner)
        except Exception:
            self._debug("sync_list_visibility çağrısı başarısız.")
            self._debug(traceback.format_exc())

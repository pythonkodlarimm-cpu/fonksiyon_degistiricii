# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/render_akisi/yoneticisi.py

ROL:
- Render akışı modülüne erişim sağlar
- Lazy import ile bağımlılığı geciktirir
- Üst katmanın doğrudan modüle erişmesini engeller
- Tüm render işlemlerini merkezi noktadan yönlendirir
- Dil destekli render akışının güvenli çalışmasına yardımcı olur

MİMARİ:
- Lazy import kullanır
- Tüm çağrılar alt modüle delegasyon şeklindedir
- Fail-soft yaklaşım uygulanır
- Gereksiz raise yerine güvenli fallback tercih edilir

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


class RenderAkisiYoneticisi:
    # =========================================================
    # DEBUG
    # =========================================================
    def _debug(self, message: str) -> None:
        try:
            print(f"[RENDER_YONETICI] {message}")
        except Exception:
            pass

    # =========================================================
    # MODUL
    # =========================================================
    def _modul(self):
        try:
            from app.ui.fonksiyon_listesi_paketi.render_akisi import render_akisi
            return render_akisi
        except Exception:
            self._debug("Render akışı modülü yüklenemedi.")
            self._debug(traceback.format_exc())
            raise

    # =========================================================
    # API
    # =========================================================
    def make_empty_label(self, owner):
        try:
            return self._modul().make_empty_label(owner)
        except Exception:
            self._debug("make_empty_label çağrısı başarısız.")
            self._debug(traceback.format_exc())
            return None

    def refresh_trigger(self, owner, *_args):
        try:
            return self._modul().refresh_trigger(owner, *_args)
        except Exception:
            self._debug("refresh_trigger çağrısı başarısız.")
            self._debug(traceback.format_exc())
            return None

    def render_items(self, owner, items, keep_scroll: bool = False) -> None:
        try:
            self._modul().render_items(
                owner,
                items=items,
                keep_scroll=keep_scroll,
            )
        except Exception:
            self._debug("render_items çağrısı başarısız.")
            self._debug(traceback.format_exc())

    def scroll_top(self, owner, *_args):
        try:
            return self._modul().scroll_top(owner, *_args)
        except Exception:
            self._debug("scroll_top çağrısı başarısız.")
            self._debug(traceback.format_exc())
            return None

    def selected_itemi_gorunur_tut(self, owner, *_args):
        try:
            return self._modul().selected_itemi_gorunur_tut(owner, *_args)
        except Exception:
            self._debug("selected_itemi_gorunur_tut çağrısı başarısız.")
            self._debug(traceback.format_exc())
            return None

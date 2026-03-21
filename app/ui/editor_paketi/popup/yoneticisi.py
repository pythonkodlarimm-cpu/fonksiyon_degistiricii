# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/popup/yoneticisi.py

ROL:
- Popup alt paketine tek giriş noktası sağlamak
- Editör popup akışını merkezileştirmek
- Üst katmanın popup modülü detaylarını bilmesini engellemek

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt popup modülü doğrudan dışarı açılmaz
- Mevcut kod ve yeni kod düzenleme popup akışları burada toplanır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations


class PopupYoneticisi:
    def _modul(self):
        from app.ui.editor_paketi.popup.editor_popuplari import (
            build_popup_toolbar,
            open_current_code_popup,
            open_new_code_editor_popup,
        )

        return {
            "build_popup_toolbar": build_popup_toolbar,
            "open_current_code_popup": open_current_code_popup,
            "open_new_code_editor_popup": open_new_code_editor_popup,
        }

    def build_popup_toolbar(self, actions):
        return self._modul()["build_popup_toolbar"](actions)

    def open_current_code_popup(self, panel, *_args):
        return self._modul()["open_current_code_popup"](panel, *_args)

    def open_new_code_editor_popup(self, panel, *_args):
        return self._modul()["open_new_code_editor_popup"](panel, *_args)
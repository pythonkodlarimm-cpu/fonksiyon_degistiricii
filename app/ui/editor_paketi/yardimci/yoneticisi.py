# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/yardimci/yoneticisi.py

ROL:
- Yardımcı alt paketine tek giriş noktası sağlamak
- Editör paneli yardımcı akışlarını merkezileştirmek
- Üst katmanın yardımcı modül detaylarını bilmesini engellemek
- Yardımcı çağrıları güvenli ve kontrollü biçimde alt modüle yönlendirmek

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt yardımcı modülü doğrudan dışarı açılmaz
- Toast, popup kapatma, inline bildirim ve status akışları burada toplanır
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


class YardimciYoneticisi:
    def _modul(self):
        try:
            from app.ui.editor_paketi.yardimci.editor_yardimcilari import (
                close_popups,
                current_item_display,
                set_popup_error,
                set_status_error,
                set_status_info,
                set_status_success,
                set_status_warning,
                show_inline_notice,
                toast,
            )

            return {
                "toast": toast,
                "close_popups": close_popups,
                "current_item_display": current_item_display,
                "show_inline_notice": show_inline_notice,
                "set_status_info": set_status_info,
                "set_status_warning": set_status_warning,
                "set_status_error": set_status_error,
                "set_status_success": set_status_success,
                "set_popup_error": set_popup_error,
            }
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] Yardımcı modül yüklenemedi.")
            print(traceback.format_exc())
            raise

    def toast(self, text: str, icon_name: str = "", duration: float = 2.2) -> None:
        try:
            return self._modul()["toast"](
                text=text,
                icon_name=icon_name,
                duration=duration,
            )
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] toast çağrısı başarısız.")
            print(traceback.format_exc())
            raise

    def close_popups(self, panel) -> None:
        try:
            return self._modul()["close_popups"](panel)
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] close_popups çağrısı başarısız.")
            print(traceback.format_exc())
            raise

    def current_item_display(self, panel) -> str:
        try:
            return self._modul()["current_item_display"](panel)
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] current_item_display çağrısı başarısız.")
            print(traceback.format_exc())
            raise

    def show_inline_notice(
        self,
        panel,
        title: str,
        text: str,
        icon_name: str = "onaylandi.png",
        tone: str = "success",
        duration: float = 4.0,
        on_tap=None,
    ) -> None:
        try:
            return self._modul()["show_inline_notice"](
                panel=panel,
                title=title,
                text=text,
                icon_name=icon_name,
                tone=tone,
                duration=duration,
                on_tap=on_tap,
            )
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] show_inline_notice çağrısı başarısız.")
            print(traceback.format_exc())
            raise

    def set_status_info(self, panel, message="", line_no=0):
        try:
            return self._modul()["set_status_info"](panel, message, line_no)
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] set_status_info çağrısı başarısız.")
            print(traceback.format_exc())
            raise

    def set_status_warning(self, panel, message="", line_no=0):
        try:
            return self._modul()["set_status_warning"](panel, message, line_no)
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] set_status_warning çağrısı başarısız.")
            print(traceback.format_exc())
            raise

    def set_status_error(self, panel, message="", line_no=0):
        try:
            return self._modul()["set_status_error"](panel, message, line_no)
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] set_status_error çağrısı başarısız.")
            print(traceback.format_exc())
            raise

    def set_status_success(self, panel, message="", line_no=0):
        try:
            return self._modul()["set_status_success"](panel, message, line_no)
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] set_status_success çağrısı başarısız.")
            print(traceback.format_exc())
            raise

    def set_popup_error(self, label, editor_area, message="", line_no=0):
        try:
            return self._modul()["set_popup_error"](
                label,
                editor_area,
                message,
                line_no,
            )
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] set_popup_error çağrısı başarısız.")
            print(traceback.format_exc())
            raise

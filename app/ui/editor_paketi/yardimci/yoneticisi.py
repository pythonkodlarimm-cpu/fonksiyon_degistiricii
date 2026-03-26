# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/yardimci/yoneticisi.py

ROL:
- Yardımcı alt paketine tek giriş noktası sağlamak
- Editör paneli yardımcı akışlarını merkezileştirmek
- Üst katmanın yardımcı modül detaylarını bilmesini engellemek
- Yardımcı çağrıları güvenli ve kontrollü biçimde alt modüle yönlendirmek
- Inline notice için dil anahtarı destekli yeni parametreleri taşımak
- Popup hata metni akışında panel referansı destekli çağrıyı korumak

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt yardımcı modülü doğrudan dışarı açılmaz
- Toast, popup kapatma, inline bildirim ve status akışları burada toplanır
- Lazy import + cache kullanır
- Fail-soft yaklaşım için tanılama logu bırakır
- Cache bozulursa kendini toparlayacak şekilde yeniden yükleme yapılır
- Fonksiyon haritası doğrulanarak cache'e alınır
- Eksik callable bulunursa güvenli biçimde None / fallback döndürülür

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 4
TARIH: 2026-03-26
IMZA: FY.
"""

from __future__ import annotations

import traceback


class YardimciYoneticisi:
    """
    Editör yardımcı modülü için merkezi erişim yöneticisi.
    """

    def __init__(self) -> None:
        self._cache = None

    # =========================================================
    # INTERNAL
    # =========================================================
    def _cache_var_mi(self) -> bool:
        """
        Yardımcı fonksiyon cache'inin geçerli olup olmadığını kontrol eder.

        Returns:
            bool
        """
        try:
            return isinstance(self._cache, dict) and bool(self._cache)
        except Exception:
            return False

    def _cache_temizle(self) -> None:
        """
        Yardımcı fonksiyon cache'ini temizler.
        """
        try:
            self._cache = None
        except Exception:
            pass

    def _harita_gecerli_mi(self, harita) -> bool:
        """
        Yardımcı fonksiyon haritasının beklenen anahtarları ve callable değerleri
        içerip içermediğini kontrol eder.

        Args:
            harita: Kontrol edilecek fonksiyon haritası

        Returns:
            bool
        """
        try:
            if not isinstance(harita, dict):
                return False

            gerekli_anahtarlar = (
                "toast",
                "close_popups",
                "current_item_display",
                "show_inline_notice",
                "set_status_info",
                "set_status_warning",
                "set_status_error",
                "set_status_success",
                "set_popup_error",
            )

            for anahtar in gerekli_anahtarlar:
                if anahtar not in harita:
                    return False
                if not callable(harita.get(anahtar)):
                    return False

            return True
        except Exception:
            return False

    def _modul(self):
        """
        Yardımcı fonksiyonları lazy import + cache ile yükler.

        Returns:
            dict[str, callable]
        """
        try:
            if self._cache_var_mi() and self._harita_gecerli_mi(self._cache):
                return self._cache
        except Exception:
            self._cache_temizle()

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

            harita = {
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

            if not self._harita_gecerli_mi(harita):
                print(
                    "[EDITOR_YARDIMCI_YONETICI] "
                    "Yardımcı modül yüklendi ama fonksiyon haritası geçersiz."
                )
                self._cache_temizle()
                return {}

            self._cache = harita
            return self._cache

        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] Yardımcı modül yüklenemedi.")
            print(traceback.format_exc())
            self._cache_temizle()
            return {}

    def _fonksiyon(self, anahtar: str):
        """
        Verilen anahtar için callable yardımcı fonksiyonu döndürür.

        Args:
            anahtar: Fonksiyon anahtarı

        Returns:
            callable | None
        """
        try:
            harita = self._modul()
            fonksiyon = harita.get(anahtar)

            if callable(fonksiyon):
                return fonksiyon
        except Exception:
            pass

        return None

    # =========================================================
    # PUBLIC
    # =========================================================
    def toast(self, text: str, icon_name: str = "", duration: float = 2.2) -> None:
        try:
            fonksiyon = self._fonksiyon("toast")
            if callable(fonksiyon):
                return fonksiyon(
                    text=text,
                    icon_name=icon_name,
                    duration=duration,
                )
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] toast çağrısı başarısız.")
            print(traceback.format_exc())
        return None

    def close_popups(self, panel) -> None:
        try:
            fonksiyon = self._fonksiyon("close_popups")
            if callable(fonksiyon):
                return fonksiyon(panel)
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] close_popups çağrısı başarısız.")
            print(traceback.format_exc())
        return None

    def current_item_display(self, panel) -> str:
        try:
            fonksiyon = self._fonksiyon("current_item_display")
            if callable(fonksiyon):
                return fonksiyon(panel)
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] current_item_display çağrısı başarısız.")
            print(traceback.format_exc())
        return "-"

    def show_inline_notice(
        self,
        panel,
        title: str,
        text: str,
        icon_name: str = "onaylandi.png",
        tone: str = "success",
        duration: float = 4.0,
        on_tap=None,
        title_key: str = "",
        title_default: str = "",
        text_key: str = "",
        text_default: str = "",
    ) -> None:
        try:
            fonksiyon = self._fonksiyon("show_inline_notice")
            if callable(fonksiyon):
                return fonksiyon(
                    panel=panel,
                    title=title,
                    text=text,
                    icon_name=icon_name,
                    tone=tone,
                    duration=duration,
                    on_tap=on_tap,
                    title_key=title_key,
                    title_default=title_default,
                    text_key=text_key,
                    text_default=text_default,
                )
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] show_inline_notice çağrısı başarısız.")
            print(traceback.format_exc())
        return None

    def set_status_info(self, panel, message="", line_no=0):
        try:
            fonksiyon = self._fonksiyon("set_status_info")
            if callable(fonksiyon):
                return fonksiyon(panel, message, line_no)
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] set_status_info çağrısı başarısız.")
            print(traceback.format_exc())
        return None

    def set_status_warning(self, panel, message="", line_no=0):
        try:
            fonksiyon = self._fonksiyon("set_status_warning")
            if callable(fonksiyon):
                return fonksiyon(panel, message, line_no)
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] set_status_warning çağrısı başarısız.")
            print(traceback.format_exc())
        return None

    def set_status_error(self, panel, message="", line_no=0):
        try:
            fonksiyon = self._fonksiyon("set_status_error")
            if callable(fonksiyon):
                return fonksiyon(panel, message, line_no)
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] set_status_error çağrısı başarısız.")
            print(traceback.format_exc())
        return None

    def set_status_success(self, panel, message="", line_no=0):
        try:
            fonksiyon = self._fonksiyon("set_status_success")
            if callable(fonksiyon):
                return fonksiyon(panel, message, line_no)
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] set_status_success çağrısı başarısız.")
            print(traceback.format_exc())
        return None

    def set_popup_error(
        self,
        label,
        editor_area,
        message="",
        line_no=0,
        panel=None,
    ):
        try:
            fonksiyon = self._fonksiyon("set_popup_error")
            if callable(fonksiyon):
                return fonksiyon(
                    label,
                    editor_area,
                    message,
                    line_no,
                    panel=panel,
                )
        except TypeError:
            try:
                fonksiyon = self._fonksiyon("set_popup_error")
                if callable(fonksiyon):
                    return fonksiyon(
                        label,
                        editor_area,
                        message,
                        line_no,
                    )
            except Exception:
                print("[EDITOR_YARDIMCI_YONETICI] set_popup_error çağrısı başarısız.")
                print(traceback.format_exc())
        except Exception:
            print("[EDITOR_YARDIMCI_YONETICI] set_popup_error çağrısı başarısız.")
            print(traceback.format_exc())
        return None

    # =========================================================
    # DEBUG / MAINTENANCE
    # =========================================================
    def cache_temizle(self) -> None:
        """
        Yardımcı modül cache'ini temizler.
        """
        self._cache_temizle()

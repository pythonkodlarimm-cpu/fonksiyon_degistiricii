# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/yardimci/yoneticisi.py

ROL:
- Yardımcı alt paketine tek giriş noktası sağlar
- Editör paneli yardımcı akışlarını merkezileştirir
- Üst katmanın yardımcı modül detaylarını bilmesini engeller
- Yardımcı çağrıları güvenli biçimde alt modüle yönlendirir
- Lazy import ile yardımcı modülü yalnızca gerektiğinde yükler
- Fail-soft yaklaşım uygular

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt yardımcı modül doğrudan dışarı açılmaz
- Yardımcı fonksiyonlar lazy import ile yüklenir
- Başarılı yükleme sonrası fonksiyon haritası cache içinde tutulur

SURUM: 5
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations


class YardimciYoneticisi:
    """
    Editör yardımcı modülü için merkezi erişim yöneticisi.
    """

    def __init__(self) -> None:
        self._fonksiyonlar = None

    def cache_temizle(self) -> None:
        """
        Yardımcı modül cache'ini temizler.
        """
        self._fonksiyonlar = None

    def _yardimci_fonksiyonlari_yukle(self) -> dict:
        """
        Yardımcı modüldeki fonksiyonları lazy import ile yükler.

        Returns:
            dict
        """
        if isinstance(self._fonksiyonlar, dict) and self._fonksiyonlar:
            return self._fonksiyonlar

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
        except Exception as exc:
            print("[EDITOR_YARDIMCI] Yardımcı modül yüklenemedi.")
            print(exc)
            self._fonksiyonlar = {}
            return self._fonksiyonlar

        self._fonksiyonlar = {
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
        return self._fonksiyonlar

    def _fonksiyon(self, ad: str):
        """
        Verilen ad için yardımcı fonksiyonu döndürür.

        Args:
            ad: Fonksiyon adı

        Returns:
            callable | None
        """
        try:
            fonksiyon = self._yardimci_fonksiyonlari_yukle().get(ad)
            if callable(fonksiyon):
                return fonksiyon
        except Exception:
            pass
        return None

    def toast(
        self,
        text: str,
        icon_name: str = "",
        duration: float = 2.2,
        panel=None,
    ) -> None:
        """
        Toast / sistem bildirimi gösterir.

        Not:
        - Eski kullanım uyumluluğu için panel opsiyoneldir.
        """
        try:
            fonksiyon = self._fonksiyon("toast")
            if callable(fonksiyon):
                try:
                    return fonksiyon(
                        panel=panel,
                        text=text,
                        icon_name=icon_name,
                        duration=duration,
                    )
                except TypeError:
                    return fonksiyon(
                        text=text,
                        icon_name=icon_name,
                        duration=duration,
                    )
        except Exception as exc:
            print("[EDITOR_YARDIMCI] toast çağrısı başarısız.")
            print(exc)
        return None

    def close_popups(self, panel) -> None:
        """
        Panel üzerindeki popup referanslarını kapatır.
        """
        try:
            fonksiyon = self._fonksiyon("close_popups")
            if callable(fonksiyon):
                return fonksiyon(panel)
        except Exception as exc:
            print("[EDITOR_YARDIMCI] close_popups çağrısı başarısız.")
            print(exc)
        return None

    def current_item_display(self, panel) -> str:
        """
        Seçili öğe için kullanıcıya gösterilecek metni döndürür.
        """
        try:
            fonksiyon = self._fonksiyon("current_item_display")
            if callable(fonksiyon):
                return fonksiyon(panel)
        except Exception as exc:
            print("[EDITOR_YARDIMCI] current_item_display çağrısı başarısız.")
            print(exc)
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
        """
        Inline notice gösterir.
        """
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
        except Exception as exc:
            print("[EDITOR_YARDIMCI] show_inline_notice çağrısı başarısız.")
            print(exc)
        return None

    def set_status_info(self, panel, message="", line_no=0):
        """
        Bilgi durumu uygular.
        """
        try:
            fonksiyon = self._fonksiyon("set_status_info")
            if callable(fonksiyon):
                return fonksiyon(panel, message, line_no)
        except Exception as exc:
            print("[EDITOR_YARDIMCI] set_status_info çağrısı başarısız.")
            print(exc)
        return None

    def set_status_warning(self, panel, message="", line_no=0):
        """
        Uyarı durumu uygular.
        """
        try:
            fonksiyon = self._fonksiyon("set_status_warning")
            if callable(fonksiyon):
                return fonksiyon(panel, message, line_no)
        except Exception as exc:
            print("[EDITOR_YARDIMCI] set_status_warning çağrısı başarısız.")
            print(exc)
        return None

    def set_status_error(self, panel, message="", line_no=0):
        """
        Hata durumu uygular.
        """
        try:
            fonksiyon = self._fonksiyon("set_status_error")
            if callable(fonksiyon):
                return fonksiyon(panel, message, line_no)
        except Exception as exc:
            print("[EDITOR_YARDIMCI] set_status_error çağrısı başarısız.")
            print(exc)
        return None

    def set_status_success(self, panel, message="", line_no=0):
        """
        Başarı durumu uygular.
        """
        try:
            fonksiyon = self._fonksiyon("set_status_success")
            if callable(fonksiyon):
                return fonksiyon(panel, message, line_no)
        except Exception as exc:
            print("[EDITOR_YARDIMCI] set_status_success çağrısı başarısız.")
            print(exc)
        return None

    def set_popup_error(
        self,
        label,
        editor_area,
        message="",
        line_no=0,
        panel=None,
    ):
        """
        Popup hata metnini uygular.
        """
        try:
            fonksiyon = self._fonksiyon("set_popup_error")
            if callable(fonksiyon):
                try:
                    return fonksiyon(
                        label,
                        editor_area,
                        message,
                        line_no,
                        panel=panel,
                    )
                except TypeError:
                    return fonksiyon(
                        label,
                        editor_area,
                        message,
                        line_no,
                    )
        except Exception as exc:
            print("[EDITOR_YARDIMCI] set_popup_error çağrısı başarısız.")
            print(exc)
        return None

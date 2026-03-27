# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/popup/yoneticisi.py

ROL:
- Popup alt paketine tek giriş noktası sağlar
- Editör popup akışını merkezileştirir
- Üst katmanın popup modülü detaylarını bilmesini engeller
- Popup metinlerinin seçili dile göre çalışacağı akışı korur
- Popup araç çubuğu ve popup açma akışlarını güvenli biçimde alt modüle yönlendirir

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt popup modülü doğrudan dışarı açılmaz
- Popup fonksiyonları lazy import ile yüklenir
- Başarılı yükleme sonrası fonksiyon haritası cache içinde tutulur
- Fail-soft yaklaşım uygulanır

SURUM: 5
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations


class PopupYoneticisi:
    """
    Editör popup modülü için merkezi erişim yöneticisi.
    """

    def __init__(self) -> None:
        self._fonksiyonlar = None

    def cache_temizle(self) -> None:
        """
        Popup fonksiyon cache'ini temizler.
        """
        self._fonksiyonlar = None

    def _popup_fonksiyonlarini_yukle(self) -> dict:
        """
        Popup modülündeki fonksiyonları lazy import ile yükler.

        Returns:
            dict
        """
        if isinstance(self._fonksiyonlar, dict) and self._fonksiyonlar:
            return self._fonksiyonlar

        try:
            from app.ui.editor_paketi.popup.editor_popuplari import (
                build_popup_toolbar,
                open_current_code_popup,
                open_new_code_editor_popup,
            )
        except Exception as exc:
            print("[EDITOR_POPUP] Popup modülü yüklenemedi.")
            print(exc)
            self._fonksiyonlar = {}
            return self._fonksiyonlar

        self._fonksiyonlar = {
            "build_popup_toolbar": build_popup_toolbar,
            "open_current_code_popup": open_current_code_popup,
            "open_new_code_editor_popup": open_new_code_editor_popup,
        }
        return self._fonksiyonlar

    def _fonksiyon(self, ad: str):
        """
        Verilen ad için popup fonksiyonunu döndürür.

        Args:
            ad: Fonksiyon adı

        Returns:
            callable | None
        """
        try:
            fonksiyon = self._popup_fonksiyonlarini_yukle().get(ad)
            if callable(fonksiyon):
                return fonksiyon
        except Exception:
            pass
        return None

    def _cagir(self, fonksiyon_adi: str, *args, **kwargs):
        """
        İstenen popup fonksiyonunu güvenli biçimde çağırır.

        Args:
            fonksiyon_adi: Çağrılacak fonksiyon adı
            *args: Pozisyonel argümanlar
            **kwargs: Anahtar argümanlar

        Returns:
            Any | None
        """
        try:
            fonksiyon = self._fonksiyon(fonksiyon_adi)
            if callable(fonksiyon):
                return fonksiyon(*args, **kwargs)
        except Exception as exc:
            print(f"[EDITOR_POPUP] {fonksiyon_adi} çağrısı başarısız.")
            print(exc)
            self.cache_temizle()
            return None

        print(f"[EDITOR_POPUP] Popup fonksiyonu bulunamadı: {fonksiyon_adi}")
        return None

    def build_popup_toolbar(self, actions):
        """
        Popup araç çubuğunu oluşturur.

        Args:
            actions: Toolbar aksiyon listesi

        Returns:
            tuple | None
        """
        return self._cagir("build_popup_toolbar", actions)

    def open_current_code_popup(self, panel, *_args):
        """
        Mevcut kod görüntüleme popup'ını açar.

        Args:
            panel: Hedef editor paneli
            *_args: Ek argümanlar
        """
        return self._cagir("open_current_code_popup", panel, *_args)

    def open_new_code_editor_popup(self, panel, *_args):
        """
        Yeni kod düzenleme popup'ını açar.

        Args:
            panel: Hedef editor paneli
            *_args: Ek argümanlar
        """
        return self._cagir("open_new_code_editor_popup", panel, *_args)

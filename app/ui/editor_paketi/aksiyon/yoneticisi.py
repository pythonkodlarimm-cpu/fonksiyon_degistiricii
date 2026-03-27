# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/aksiyon/yoneticisi.py

ROL:
- Aksiyon alt paketine tek giriş noktası sağlar
- Editör panelindeki kullanıcı aksiyonlarını merkezileştirir
- Üst katmanın aksiyon modülü detaylarını bilmesini engeller
- Aksiyon çağrılarını güvenli biçimde alt modüle yönlendirir
- Yapıştırma dahil editör kontrol paneli aksiyonlarını tek merkezde toplar

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt aksiyon modülü doğrudan dışarı açılmaz
- Aksiyon fonksiyonları lazy import ile yüklenir
- Başarılı yükleme sonrası fonksiyon haritası cache içinde tutulur
- Fail-soft yaklaşım uygulanır

SURUM: 6
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations


class AksiyonYoneticisi:
    """
    Editör aksiyon modülü için merkezi erişim yöneticisi.
    """

    def __init__(self) -> None:
        self._fonksiyonlar = None

    def cache_temizle(self) -> None:
        """
        Aksiyon fonksiyon cache'ini temizler.
        """
        self._fonksiyonlar = None

    def _aksiyon_fonksiyonlarini_yukle(self) -> dict:
        """
        Aksiyon modülündeki fonksiyonları lazy import ile yükler.

        Returns:
            dict
        """
        if isinstance(self._fonksiyonlar, dict) and self._fonksiyonlar:
            return self._fonksiyonlar

        try:
            from app.ui.editor_paketi.aksiyon.editor_aksiyonlari import (
                check_new_code,
                clear_new_code,
                copy_current_to_new,
                handle_restore,
                handle_update,
                paste_new_code,
            )
        except Exception as exc:
            print("[EDITOR_AKSIYON] Aksiyon modülü yüklenemedi.")
            print(exc)
            self._fonksiyonlar = {}
            return self._fonksiyonlar

        self._fonksiyonlar = {
            "copy_current_to_new": copy_current_to_new,
            "paste_new_code": paste_new_code,
            "clear_new_code": clear_new_code,
            "check_new_code": check_new_code,
            "handle_update": handle_update,
            "handle_restore": handle_restore,
        }
        return self._fonksiyonlar

    def _fonksiyon(self, ad: str):
        """
        Verilen ad için aksiyon fonksiyonunu döndürür.

        Args:
            ad: Fonksiyon adı

        Returns:
            callable | None
        """
        try:
            fonksiyon = self._aksiyon_fonksiyonlarini_yukle().get(ad)
            if callable(fonksiyon):
                return fonksiyon
        except Exception:
            pass
        return None

    def _cagir(self, aksiyon_adi: str, panel, *_args):
        """
        İstenen aksiyonu güvenli biçimde çağırır.

        Args:
            aksiyon_adi: Çağrılacak aksiyon adı
            panel: Hedef editör paneli
            *_args: Ek argümanlar

        Returns:
            Any | None
        """
        try:
            fonksiyon = self._fonksiyon(aksiyon_adi)
            if callable(fonksiyon):
                return fonksiyon(panel, *_args)
        except Exception as exc:
            print(f"[EDITOR_AKSIYON] {aksiyon_adi} çağrısı başarısız.")
            print(exc)
            self.cache_temizle()
            return None

        print(f"[EDITOR_AKSIYON] Aksiyon bulunamadı: {aksiyon_adi}")
        return None

    def copy_current_to_new(self, panel, *_args):
        """
        Mevcut kodu yeni kod alanına kopyalar.
        """
        return self._cagir("copy_current_to_new", panel, *_args)

    def paste_new_code(self, panel, *_args):
        """
        Pano içeriğini yeni kod alanına yapıştırır.
        """
        return self._cagir("paste_new_code", panel, *_args)

    def clear_new_code(self, panel, *_args):
        """
        Yeni kod alanını temizler.
        """
        return self._cagir("clear_new_code", panel, *_args)

    def check_new_code(self, panel, *_args):
        """
        Yeni kod alanındaki içeriği doğrular.
        """
        return self._cagir("check_new_code", panel, *_args)

    def handle_update(self, panel, *_args):
        """
        Güncelleme akışını yürütür.
        """
        return self._cagir("handle_update", panel, *_args)

    def handle_restore(self, panel, *_args):
        """
        Geri yükleme akışını yürütür.
        """
        return self._cagir("handle_restore", panel, *_args)

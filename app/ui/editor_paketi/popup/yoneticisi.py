# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/popup/yoneticisi.py

ROL:
- Popup alt paketine tek giriş noktası sağlamak
- Editör popup akışını merkezileştirmek
- Üst katmanın popup modülü detaylarını bilmesini engellemek
- Popup metinlerinin seçili dile göre çalışacağı akışı korumak
- Popup araç çubuğu ve popup açma akışlarını güvenli biçimde alt modüle yönlendirmek

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt popup modülü doğrudan dışarı açılmaz
- Mevcut kod ve yeni kod düzenleme popup akışları burada toplanır
- Popup içerikleri editor_popuplari.py içinde tutulur
- Lazy import + cache korunur
- Fail-soft yaklaşım için tanılama logu bırakır
- Cache bozulursa kendini toparlayacak şekilde yeniden resolve yapabilir
- Fonksiyon haritası doğrulanmadan cache'e alınmaz
- Hata halinde cache temizlenir ve bir sonraki çağrıda yeniden yükleme denenir

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


class PopupYoneticisi:
    """
    Editör popup modülü için merkezi erişim yöneticisi.
    """

    modul_yolu = "app.ui.editor_paketi.popup.editor_popuplari"

    def __init__(self) -> None:
        self._cached_modul_haritasi = None

    # =========================================================
    # CACHE
    # =========================================================
    def _cache_var_mi(self) -> bool:
        """
        Popup fonksiyon haritası cache'inin geçerli olup olmadığını kontrol eder.

        Returns:
            bool
        """
        try:
            return isinstance(self._cached_modul_haritasi, dict)
        except Exception:
            return False

    def _cache_temizle(self) -> None:
        """
        Popup fonksiyon haritası cache'ini temizler.
        """
        try:
            self._cached_modul_haritasi = None
        except Exception:
            pass

    def cache_temizle(self) -> None:
        """
        Popup fonksiyon cache'ini temizler.
        """
        self._cache_temizle()

    # =========================================================
    # VALIDATION
    # =========================================================
    def _harita_gecerli_mi(self, harita) -> bool:
        """
        Popup fonksiyon haritasının beklenen anahtarları ve callable değerleri
        içerip içermediğini doğrular.

        Args:
            harita: Kontrol edilecek fonksiyon haritası

        Returns:
            bool
        """
        try:
            if not isinstance(harita, dict):
                return False

            gerekli_anahtarlar = (
                "build_popup_toolbar",
                "open_current_code_popup",
                "open_new_code_editor_popup",
            )

            for anahtar in gerekli_anahtarlar:
                if anahtar not in harita:
                    return False

                if not callable(harita.get(anahtar)):
                    return False

            return True
        except Exception:
            return False

    # =========================================================
    # INTERNAL
    # =========================================================
    def _modul(self):
        """
        Popup fonksiyon haritasını lazy import + cache ile döndürür.

        Returns:
            dict[str, callable]
        """
        try:
            if self._cache_var_mi() and self._harita_gecerli_mi(
                self._cached_modul_haritasi
            ):
                return self._cached_modul_haritasi
        except Exception:
            self._cache_temizle()

        try:
            from app.ui.editor_paketi.popup.editor_popuplari import (
                build_popup_toolbar,
                open_current_code_popup,
                open_new_code_editor_popup,
            )

            harita = {
                "build_popup_toolbar": build_popup_toolbar,
                "open_current_code_popup": open_current_code_popup,
                "open_new_code_editor_popup": open_new_code_editor_popup,
            }

            if not self._harita_gecerli_mi(harita):
                print(
                    "[EDITOR_POPUP_YONETICI] "
                    "Popup modülü yüklendi ama fonksiyon haritası geçersiz."
                )
                self._cache_temizle()
                raise RuntimeError("Popup fonksiyon haritası geçersiz.")

            self._cached_modul_haritasi = harita
            return harita

        except Exception:
            print("[EDITOR_POPUP_YONETICI] Popup modülü yüklenemedi.")
            print(traceback.format_exc())
            self._cache_temizle()
            raise

    def _cagir(self, fonksiyon_adi: str, *args, **kwargs):
        """
        İstenen popup fonksiyonunu güvenli biçimde çağırır.

        Args:
            fonksiyon_adi: Çağrılacak fonksiyon anahtarı
            *args: Pozisyonel argümanlar
            **kwargs: Anahtar argümanlar

        Returns:
            Any
        """
        try:
            harita = self._modul()
            fonksiyon = harita.get(fonksiyon_adi)

            if not callable(fonksiyon):
                raise RuntimeError(
                    f"Popup fonksiyonu bulunamadı veya callable değil: {fonksiyon_adi}"
                )

            return fonksiyon(*args, **kwargs)

        except Exception:
            print(
                "[EDITOR_POPUP_YONETICI] "
                f"{fonksiyon_adi} çağrısı başarısız."
            )
            print(traceback.format_exc())
            self._cache_temizle()
            raise

    # =========================================================
    # PUBLIC API
    # =========================================================
    def build_popup_toolbar(self, actions):
        """
        Popup araç çubuğunu oluşturur.

        Args:
            actions: Toolbar aksiyon listesi

        Returns:
            tuple
        """
        return self._cagir("build_popup_toolbar", actions)

    def open_current_code_popup(self, panel, *_args):
        """
        Mevcut kod görüntüleme popup'ını açar.

        Args:
            panel: Hedef editor paneli
            *_args: Ek argümanlar

        Returns:
            Any
        """
        return self._cagir("open_current_code_popup", panel, *_args)

    def open_new_code_editor_popup(self, panel, *_args):
        """
        Yeni kod düzenleme popup'ını açar.

        Args:
            panel: Hedef editor paneli
            *_args: Ek argümanlar

        Returns:
            Any
        """
        return self._cagir("open_new_code_editor_popup", panel, *_args)

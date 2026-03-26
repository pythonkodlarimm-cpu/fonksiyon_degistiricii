# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/aksiyon/yoneticisi.py

ROL:
- Aksiyon alt paketine tek giriş noktası sağlamak
- Editör panelindeki kullanıcı aksiyonlarını merkezileştirmek
- Üst katmanın aksiyon modülü detaylarını bilmesini engellemek
- Aksiyon çağrılarını güvenli ve kontrollü biçimde alt modüle yönlendirmek
- Yapıştırma dahil editör kontrol paneli aksiyonlarını tek merkezde toplamak

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt aksiyon modülü doğrudan dışarı açılmaz
- Kopyalama, yapıştırma, temizleme, doğrulama, güncelleme ve geri yükleme akışlarını toplar
- Lazy import + cache kullanır
- Fail-soft yaklaşım için tanılama logu bırakır
- Cache bozulursa kendini toparlayacak şekilde yeniden resolve yapabilir
- Fonksiyon haritası doğrulanmadan cache'e alınmaz
- Cache içindeki harita tekrar çağrılarda yeniden kullanılabilir
- Hata halinde cache temizlenir ve sonraki çağrıda yeniden yükleme denenir

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 5
TARIH: 2026-03-26
IMZA: FY.
"""

from __future__ import annotations

import traceback


class AksiyonYoneticisi:
    """
    Editör aksiyon modülü için merkezi erişim yöneticisi.
    """

    modul_yolu = "app.ui.editor_paketi.aksiyon.editor_aksiyonlari"

    def __init__(self) -> None:
        self._cached_modul_haritasi = None

    # =========================================================
    # CACHE
    # =========================================================
    def _cache_var_mi(self) -> bool:
        """
        Fonksiyon haritası cache'inin geçerli bir dict olup olmadığını kontrol eder.

        Returns:
            bool
        """
        try:
            return isinstance(self._cached_modul_haritasi, dict)
        except Exception:
            return False

    def _cache_temizle(self) -> None:
        """
        İç fonksiyon haritası cache'ini temizler.
        """
        try:
            self._cached_modul_haritasi = None
        except Exception:
            pass

    def cache_temizle(self) -> None:
        """
        Aksiyon fonksiyon cache'ini temizler.
        """
        self._cache_temizle()

    # =========================================================
    # VALIDATION
    # =========================================================
    def _harita_gecerli_mi(self, harita) -> bool:
        """
        Aksiyon haritasının beklenen anahtarları ve callable değerleri
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
                "copy_current_to_new",
                "paste_new_code",
                "clear_new_code",
                "check_new_code",
                "handle_update",
                "handle_restore",
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
        Aksiyon fonksiyon haritasını lazy import + cache ile döndürür.

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
            from app.ui.editor_paketi.aksiyon.editor_aksiyonlari import (
                check_new_code,
                clear_new_code,
                copy_current_to_new,
                handle_restore,
                handle_update,
                paste_new_code,
            )

            harita = {
                "copy_current_to_new": copy_current_to_new,
                "paste_new_code": paste_new_code,
                "clear_new_code": clear_new_code,
                "check_new_code": check_new_code,
                "handle_update": handle_update,
                "handle_restore": handle_restore,
            }

            if not self._harita_gecerli_mi(harita):
                print(
                    "[EDITOR_AKSIYON_YONETICI] "
                    "Aksiyon modülü yüklendi ama fonksiyon haritası geçersiz."
                )
                self._cache_temizle()
                raise RuntimeError("Aksiyon fonksiyon haritası geçersiz.")

            self._cached_modul_haritasi = harita
            return harita

        except Exception:
            print("[EDITOR_AKSIYON_YONETICI] Aksiyon modülü yüklenemedi.")
            print(traceback.format_exc())
            self._cache_temizle()
            raise

    def _cagir(self, aksiyon_adi: str, panel, *_args):
        """
        İstenen aksiyonu güvenli biçimde çağırır.

        Args:
            aksiyon_adi: Çağrılacak aksiyon anahtarı
            panel: Hedef editor paneli
            *_args: Ek argümanlar

        Returns:
            Any
        """
        try:
            harita = self._modul()
            fonksiyon = harita.get(aksiyon_adi)

            if not callable(fonksiyon):
                raise RuntimeError(
                    f"Aksiyon bulunamadı veya callable değil: {aksiyon_adi}"
                )

            return fonksiyon(panel, *_args)

        except Exception:
            print(
                "[EDITOR_AKSIYON_YONETICI] "
                f"{aksiyon_adi} çağrısı başarısız."
            )
            print(traceback.format_exc())
            self._cache_temizle()
            raise

    # =========================================================
    # PUBLIC API
    # =========================================================
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

# -*- coding: utf-8 -*-
"""
DOSYA: main.py

ROL:
- Uygulamanın giriş noktasıdır
- UI katmanını başlatır
- Servis ve UI entegrasyonunu tetikler
- Android / Pydroid3 / masaüstü uyumlu çalışır
- UI guard ve genel başlatma hatalarını kopyalanabilir hata kartında gösterir
- İsteğe bağlı icon debug çıktısı üretir

MİMARİ:
- UI -> Services -> Core zinciri
- Core doğrudan çağrılmaz
- UIYoneticisi tek giriş noktasıdır
- UI build öncesi guard kontrolü çalıştırılır
- Hata durumunda çökme yerine okunabilir hata kartı gösterilir
- Debug çıktısı kontrollü ve tek noktadan yönetilir

SURUM: 6
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

import sys
import traceback

from kivy.app import App
from kivy.config import Config


# ---------------------------------------------------------
# KIVY AYARLARI
# ---------------------------------------------------------
Config.set("graphics", "resizable", "0")
Config.set("kivy", "exit_on_escape", "0")


# ---------------------------------------------------------
# DEBUG
# ---------------------------------------------------------
ICON_DEBUG_AKTIF = True
GUARD_DEBUG_AKTIF = True


def _debug_yaz(*args: object) -> None:
    """
    Güvenli debug yazdırma yardımcısı.
    """
    try:
        print(*args)
    except Exception:
        pass


def _icon_debug_yazdir() -> None:
    """
    Icon çözümleme debug çıktısı üretir.
    """
    if not ICON_DEBUG_AKTIF:
        return

    try:
        from app.ui.ortak.ikonlar import (
            icon_mevcut_mu,
            ikon_kok_dizini,
            ikon_yolu,
        )

        _debug_yaz("ICON ROOT =", ikon_kok_dizini())
        _debug_yaz("ICON menu =", ikon_yolu("menu.png"))
        _debug_yaz("ICON menu exists =", icon_mevcut_mu("menu.png"))
        _debug_yaz("ICON dosya_sec =", ikon_yolu("dosya_sec.png"))
        _debug_yaz("ICON dosya_sec exists =", icon_mevcut_mu("dosya_sec.png"))
        _debug_yaz("ICON settings =", ikon_yolu("settings.png"))
        _debug_yaz("ICON settings exists =", icon_mevcut_mu("settings.png"))
    except Exception:
        _debug_yaz("Icon debug yazdırılamadı:")
        traceback.print_exc()


def _ui_guard_calistir() -> None:
    """
    UI build öncesi guard kontrolünü çalıştırır.

    Guard modülü yoksa veya import edilemezse hata yukarı taşınır.
    Guard fonksiyonu mevcutsa doğrudan çalıştırılır.
    """
    from app.ui.ortak.guard import ui_guard_kontrolu

    if GUARD_DEBUG_AKTIF:
        _debug_yaz("UI GUARD: başlatılıyor...")

    ui_guard_kontrolu()

    if GUARD_DEBUG_AKTIF:
        _debug_yaz("UI GUARD: başarılı.")


class FonksiyonDegistiriciApp(App):
    """
    Ana uygulama sınıfı.
    """

    __slots__ = ("_ui",)

    def __init__(self, **kwargs):
        """
        App nesnesini oluşturur.
        """
        super().__init__(**kwargs)
        self._ui = None

    def build(self):
        """
        Root widget üretimi.
        """
        try:
            _icon_debug_yazdir()
            _ui_guard_calistir()

            from app.ui import UIYoneticisi

            self._ui = UIYoneticisi()
            return self._ui.create_root()

        except Exception as exc:
            return self._fallback_hata_karti(exc)

    def _fallback_hata_karti(self, exc: Exception):
        """
        Hata durumunda kullanıcıya okunabilir hata kartı döndürür.
        """
        from app.ui.bilesenler.hata_karti import HataKarti

        try:
            from app.ui.ortak.guard import UIGuardHatasi, ui_guard_hata_metni
        except Exception:
            UIGuardHatasi = type("_TmpGuardErr", (Exception,), {})

            def ui_guard_hata_metni(err: Exception) -> str:
                return f"{err.__class__.__name__}: {err}"

        if isinstance(exc, UIGuardHatasi):
            detay = ui_guard_hata_metni(exc)
            baslik = "UI Guard Hatası"
            aciklama = (
                "Arayüz ortak yapı kontrolünden geçemedi. "
                "Aşağıdaki detay kopyalanabilir ve nokta atışı çözüm içerir."
            )
        else:
            detay = (
                f"{exc.__class__.__name__}: {exc}\n\n"
                f"{traceback.format_exc()}"
            )
            baslik = "Başlatma Hatası"
            aciklama = (
                "Uygulama başlatılırken beklenmeyen bir hata oluştu. "
                "Aşağıdaki detay kopyalanabilir."
            )

        _debug_yaz(detay)

        return HataKarti(
            baslik=baslik,
            aciklama=aciklama,
            detay=detay,
        )


def main() -> None:
    """
    Uygulamayı başlatır.
    """
    try:
        FonksiyonDegistiriciApp().run()
    except Exception:
        _debug_yaz("Uygulama başlatılamadı:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

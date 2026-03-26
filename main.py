# -*- coding: utf-8 -*-
"""
DOSYA: main.py

ROL:
- Uygulama giriş noktası
- Kivy App sınıfını başlatır
- RootWidget oluşturur
- Uygulama başlığında sürüm bilgisini gösterir
- Proje kökünü sys.path içine ekler
- APK içinde ve normal çalıştırmada importları sade ve güvenli tutar
- Hata olursa traceback'i ekranda göstermeye çalışır
- Lifecycle yönetimi (pause / resume)
- Root state kaydet / geri yükle tetikleme
- Resume sonrası UI refresh zincirini başlatma

SURUM: 3
TARIH: 2026-03-26
IMZA: FY.
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


def _safe_resolve(path: Path) -> Path:
    """
    Path nesnesini güvenli biçimde resolve etmeye çalışır.
    """
    try:
        return path.resolve()
    except Exception:
        try:
            return path.absolute()
        except Exception:
            return path


def _proje_koku_bul() -> Path:
    """
    Proje kökünü güvenli biçimde bulur.
    """
    try:
        return _safe_resolve(Path(__file__).parent)
    except Exception:
        try:
            return _safe_resolve(Path.cwd())
        except Exception:
            return Path(".")


PROJE_ROOT = _proje_koku_bul()

if str(PROJE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJE_ROOT))


def _build_error_root(hata_metni: str) -> BoxLayout:
    """
    Uygulama açılış hatalarında gösterilecek basit fallback root'u üretir.
    """
    root = BoxLayout(
        orientation="vertical",
        padding=dp(18),
        spacing=dp(12),
    )

    baslik = Label(
        text="Fonksiyon Degistirici",
        size_hint_y=None,
        height=dp(42),
        font_size="20sp",
        bold=True,
        color=(1, 1, 1, 1),
        halign="center",
        valign="middle",
        shorten=True,
        shorten_from="right",
        max_lines=1,
    )
    baslik.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    root.add_widget(baslik)

    mesaj = Label(
        text="Uygulama açılırken hata oluştu.\n\n" + str(hata_metni or ""),
        color=(1, 0.82, 0.82, 1),
        halign="left",
        valign="top",
    )
    mesaj.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))
    root.add_widget(mesaj)

    return root


class FonksiyonDegistiriciApp(App):
    """
    Uygulamanın ana App sınıfı.
    """

    def build(self):
        """
        Root widget'ı oluşturur.
        """
        try:
            try:
                from kivy.core.window import Window
                Window.softinput_mode = "below_target"
            except Exception:
                pass

            from app.core import CoreYoneticisi
            from app.ui.root_paketi import RootWidget

            core = CoreYoneticisi()
            self.title = f"{core.uygulama_adi()} v{core.tam_surum()}"

            self.root_widget = RootWidget()
            return self.root_widget

        except Exception:
            hata = traceback.format_exc()
            try:
                print(hata)
            except Exception:
                pass

            self.root_widget = None
            return _build_error_root(hata)

    def on_start(self):
        """
        Uygulama başlatıldıktan sonra debug amaçlı kök yolu loglar.
        """
        try:
            print("PROJE_ROOT =", PROJE_ROOT)
        except Exception:
            pass

    # =========================================================
    # PAUSE → STATE SAVE
    # =========================================================
    def on_pause(self):
        """
        Uygulama arka plana geçerken root state kaydını tetikler.
        """
        try:
            print("[APP] on_pause")

            root_widget = getattr(self, "root_widget", None)
            if root_widget is not None:
                if hasattr(root_widget, "uygulama_durumu_kaydet"):
                    root_widget.uygulama_durumu_kaydet()

        except Exception:
            try:
                print(traceback.format_exc())
            except Exception:
                pass

        return True

    # =========================================================
    # RESUME → STATE LOAD + UI REFRESH
    # =========================================================
    def on_resume(self):
        """
        Uygulama arka plandan geri gelince state restore ve UI refresh zincirini tetikler.
        """
        try:
            print("[APP] on_resume")

            root_widget = getattr(self, "root_widget", None)
            if root_widget is not None:
                # İlk restore denemesi
                if hasattr(root_widget, "uygulama_durumu_geri_yukle"):
                    try:
                        root_widget.uygulama_durumu_geri_yukle()
                    except Exception:
                        try:
                            print(traceback.format_exc())
                        except Exception:
                            pass

                # Ana resume zinciri
                Clock.schedule_once(self._resume_ui_refresh, 0.10)

        except Exception:
            try:
                print(traceback.format_exc())
            except Exception:
                pass

    # =========================================================
    # RESUME UI REFRESH
    # =========================================================
    def _resume_ui_refresh(self, _dt):
        """
        Resume sonrası root üstünde genel yenileme zincirini çalıştırır.
        """
        try:
            root_widget = getattr(self, "root_widget", None)
            if root_widget is None:
                return

            # Öncelikli ortak giriş
            if hasattr(root_widget, "uygulama_resume_akisini_tetikle"):
                root_widget.uygulama_resume_akisini_tetikle()
                return

            # Eski/uyumlu giriş
            if hasattr(root_widget, "resume_sonrasi_yenile"):
                root_widget.resume_sonrasi_yenile()
                return

            # Son fallback
            if hasattr(root_widget, "_post_build_refresh"):
                root_widget._post_build_refresh()

        except Exception:
            try:
                print(traceback.format_exc())
            except Exception:
                pass


def main() -> None:
    """
    Uygulamayı başlatır.
    """
    try:
        FonksiyonDegistiriciApp().run()
    except Exception:
        try:
            print(traceback.format_exc())
        except Exception:
            pass


if __name__ == "__main__":
    main()

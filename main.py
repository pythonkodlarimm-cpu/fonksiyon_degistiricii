# -*- coding: utf-8 -*-
"""
DOSYA: main.py

ROL:
- Uygulama giriş noktasıdır
- Kivy App sınıfını başlatır
- RootWidget oluşturur
- Uygulama başlığında sürüm bilgisini gösterir
- Proje kökünü sys.path içine ekler
- Hata olursa fallback hata ekranı göstermeye çalışır
- Lifecycle yönetimini yapar
- Pause sırasında root state kaydını tetikler
- Resume sonrası root refresh zincirini başlatır

SURUM: 4
TARIH: 2026-03-27
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
            self._window_ayarlarini_uygula()

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

    def _window_ayarlarini_uygula(self) -> None:
        """
        Pencere / klavye davranışı ile ilgili güvenli ayarları uygular.
        """
        try:
            from kivy.core.window import Window
            Window.softinput_mode = "below_target"
        except Exception:
            pass

    def on_start(self):
        """
        Uygulama başlatıldıktan sonra debug amaçlı proje kökünü loglar.
        """
        try:
            print("PROJE_ROOT =", PROJE_ROOT)
        except Exception:
            pass

    def on_pause(self):
        """
        Uygulama arka plana geçerken root state kaydını tetikler.
        """
        try:
            print("[APP] on_pause")
        except Exception:
            pass

        try:
            root_widget = getattr(self, "root_widget", None)
            if root_widget is not None:
                kaydet = getattr(root_widget, "uygulama_durumu_kaydet", None)
                if callable(kaydet):
                    kaydet()
        except Exception:
            try:
                print(traceback.format_exc())
            except Exception:
                pass

        return True

    def on_resume(self):
        """
        Uygulama arka plandan geri gelince root refresh zincirini tetikler.
        """
        try:
            print("[APP] on_resume")
        except Exception:
            pass

        try:
            root_widget = getattr(self, "root_widget", None)
            if root_widget is None:
                return

            geri_yukle = getattr(root_widget, "uygulama_durumu_geri_yukle", None)
            if callable(geri_yukle):
                try:
                    geri_yukle()
                except Exception:
                    try:
                        print(traceback.format_exc())
                    except Exception:
                        pass

            Clock.schedule_once(self._resume_ui_refresh, 0.10)
        except Exception:
            try:
                print(traceback.format_exc())
            except Exception:
                pass

    def _resume_ui_refresh(self, _dt):
        """
        Resume sonrası root üstünde genel yenileme zincirini çalıştırır.
        """
        try:
            root_widget = getattr(self, "root_widget", None)
            if root_widget is None:
                return

            resume_akisi = getattr(root_widget, "uygulama_resume_akisini_tetikle", None)
            if callable(resume_akisi):
                resume_akisi()
                return

            resume_yenile = getattr(root_widget, "resume_sonrasi_yenile", None)
            if callable(resume_yenile):
                resume_yenile()
                return

            post_build_refresh = getattr(root_widget, "_post_build_refresh", None)
            if callable(post_build_refresh):
                post_build_refresh()
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

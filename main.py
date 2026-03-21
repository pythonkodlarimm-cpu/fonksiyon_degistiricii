# -*- coding: utf-8 -*-
"""
DOSYA: main.py
MODUL: main

ROL:
- Uygulamanın giriş noktası
- Kivy App sınıfını başlatır
- RootWidget oluşturur
- Uygulama başlığında sürüm bilgisini gösterir
- Proje kökünü sys.path içine ekler
- APK içinde ve normal çalıştırmada importları sade ve güvenli tutar
- Hata olursa traceback'i ekranda göstermeye çalışır
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


def _safe_resolve(path: Path) -> Path:
    try:
        return path.resolve()
    except Exception:
        try:
            return path.absolute()
        except Exception:
            return path


def _proje_koku_bul() -> Path:
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
    def build(self):
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

            return RootWidget()

        except Exception:
            hata = traceback.format_exc()
            try:
                print(hata)
            except Exception:
                pass
            return _build_error_root(hata)

    def on_start(self):
        try:
            print("PROJE_ROOT =", PROJE_ROOT)
        except Exception:
            pass


def main() -> None:
    try:
        FonksiyonDegistiriciApp().run()
    except Exception:
        try:
            print(traceback.format_exc())
        except Exception:
            pass


if __name__ == "__main__":
    main()

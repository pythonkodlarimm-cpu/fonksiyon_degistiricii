# -*- coding: utf-8 -*-
"""
DOSYA: main.py
MODUL: main

ROL:
- Uygulamanın giriş noktası.
- Kivy App sınıfını başlatır.
- RootWidget oluşturur.
- Uygulama başlığında sürüm bilgisini gösterir.
- Proje kökünü sys.path içine ekler.
- APK içinde ve normal çalıştırmada importları sade ve güvenli tutar.
- Hata olursa traceback'i ekranda göstermeye çalışır.

SURUM: 6
TARIH: 2026-03-14
IMZA: FY.
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
    """
    Bu proje yapısında en güvenli yaklaşım:
    main.py dosyasının bulunduğu klasörü proje kökü kabul etmektir.

    Android / APK içinde resolve davranışı farklı olabileceği için
    güvenli çözüm kullanılır.
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
    Uygulama açılışında hata olursa sade bir hata ekranı gösterir.
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
    Ana Kivy uygulaması.
    """

    def build(self):
        """
        Importları burada yapıyoruz ki açılış hataları ekranda gösterilebilsin.
        """
        try:
            try:
                from kivy.core.window import Window

                Window.softinput_mode = "below_target"
            except Exception:
                pass

            from app.core.uygulama_meta import UYGULAMA_ADI, tam_surum
            from app.ui.root import RootWidget

            self.title = f"{UYGULAMA_ADI} v{tam_surum()}"
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
            print(f"PROJE_ROOT = {PROJE_ROOT}")
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

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

SURUM: 4
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


def _proje_koku_bul() -> Path:
    """
    Bu proje yapısında en güvenli yaklaşım:
    main.py dosyasının bulunduğu klasörü proje kökü kabul etmektir.
    """
    try:
        return Path(__file__).resolve().parent
    except Exception:
        return Path.cwd().resolve()


PROJE_ROOT = _proje_koku_bul()

if str(PROJE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJE_ROOT))


from app.core.uygulama_meta import UYGULAMA_ADI, tam_surum
from app.ui.root import RootWidget


def _build_error_root(hata_metni: str) -> BoxLayout:
    """
    Root açılamazsa kullanıcıya sade bir hata ekranı gösterir.
    """
    root = BoxLayout(
        orientation="vertical",
        padding=dp(18),
        spacing=dp(12),
    )

    baslik = Label(
        text=UYGULAMA_ADI,
        size_hint_y=None,
        height=dp(42),
        font_size="20sp",
        bold=True,
        color=(1, 1, 1, 1),
        halign="center",
        valign="middle",
    )
    baslik.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    root.add_widget(baslik)

    alt = Label(
        text=f"Sürüm {tam_surum()}",
        size_hint_y=None,
        height=dp(24),
        font_size="12sp",
        color=(0.75, 0.82, 0.92, 1),
        halign="center",
        valign="middle",
    )
    alt.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    root.add_widget(alt)

    mesaj = Label(
        text="Uygulama açılırken hata oluştu.\n\nDetay:\n" + hata_metni,
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
        Root widget oluşturur.
        """
        self.title = f"{UYGULAMA_ADI} v{tam_surum()}"

        try:
            return RootWidget()
        except Exception as exc:
            print("Uygulama başlatılırken hata oluştu:")
            traceback.print_exc()
            return _build_error_root(str(exc))

    def on_start(self):
        try:
            print(f"{UYGULAMA_ADI} başlatıldı. Sürüm: {tam_surum()}")
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
        print("Uygulama çalıştırılamadı:")
        traceback.print_exc()


if __name__ == "__main__":
    main()
# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/bilesenler/hata_karti.py

ROL:
- Başlatma / guard / beklenmeyen hata durumlarını kullanıcıya
  okunabilir ve kopyalanabilir kart olarak gösterir
- UI açılmasa bile minimum bağımlılıkla çalışır
- UI ortak contract yapısına uygun biçimde ortak renk/boyut kullanır

MİMARİ:
- Tek başına kullanılabilir
- Guard hatası ve genel hata için ortak görünüm sağlar
- Kopyalanabilir detay alanı içerir
- Hardcoded tema/boyut kullanımı minimuma indirilmiştir
- Ortak UI katmanına uyar
- Geriye uyumluluk katmanı içermez

SURUM: 2
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from kivy.app import App
from kivy.core.clipboard import Clipboard
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from app.ui.ortak.boyutlar import BOSLUK_MD, BOSLUK_SM, YUKSEKLIK_BUTON
from app.ui.ortak.renkler import (
    ARKAPLAN,
    HATA,
    INPUT_ARKAPLAN,
    KART,
    METIN,
    METIN_SOLUK,
    SEFFAF,
)


def _arkaplan_ciz(widget, color: tuple[float, float, float, float]) -> None:
    """
    Widget arkaplanını güvenli şekilde çizer.
    """
    with widget.canvas.before:
        Color(*color)
        widget._bg_rect = Rectangle(pos=widget.pos, size=widget.size)

    def _guncelle(*_args):
        widget._bg_rect.pos = widget.pos
        widget._bg_rect.size = widget.size

    widget.bind(pos=_guncelle, size=_guncelle)


class HataKarti(BoxLayout):
    """
    Kopyalanabilir hata kartı.
    """

    __slots__ = ("_text_input",)

    def __init__(
        self,
        *,
        baslik: str,
        aciklama: str,
        detay: str,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.spacing = BOSLUK_MD
        self.padding = BOSLUK_MD

        _arkaplan_ciz(self, ARKAPLAN)

        lbl_baslik = Label(
            text=str(baslik or ""),
            size_hint_y=None,
            height=YUKSEKLIK_BUTON,
            color=HATA,
            bold=True,
            halign="left",
            valign="middle",
        )
        lbl_baslik.bind(
            size=lambda inst, _val: setattr(inst, "text_size", inst.size)
        )
        self.add_widget(lbl_baslik)

        lbl_aciklama = Label(
            text=str(aciklama or ""),
            size_hint_y=None,
            height=YUKSEKLIK_BUTON + BOSLUK_MD,
            color=METIN_SOLUK,
            halign="left",
            valign="middle",
        )
        lbl_aciklama.bind(
            size=lambda inst, _val: setattr(inst, "text_size", inst.size)
        )
        self.add_widget(lbl_aciklama)

        kart = BoxLayout(
            orientation="vertical",
            padding=BOSLUK_SM,
        )
        _arkaplan_ciz(kart, KART)

        scroll = ScrollView(
            do_scroll_x=True,
            do_scroll_y=True,
            bar_width=max(2, int(BOSLUK_SM / 2)),
        )

        self._text_input = TextInput(
            text=str(detay or ""),
            readonly=True,
            multiline=True,
            background_color=SEFFAF,
            foreground_color=METIN,
            hint_text_color=METIN_SOLUK,
            cursor_color=METIN,
        )

        # TextInput görünümü için iç katman
        input_katmani = BoxLayout(
            orientation="vertical",
            padding=BOSLUK_SM,
        )
        _arkaplan_ciz(input_katmani, INPUT_ARKAPLAN)

        input_katmani.add_widget(self._text_input)
        scroll.add_widget(input_katmani)
        kart.add_widget(scroll)
        self.add_widget(kart)

        alt = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=YUKSEKLIK_BUTON,
            spacing=BOSLUK_SM,
        )

        btn_kopyala = Button(text="Kopyala")
        btn_kapat = Button(text="Kapat")

        btn_kopyala.bind(on_release=self._kopyala)
        btn_kapat.bind(on_release=self._kapat)

        alt.add_widget(btn_kopyala)
        alt.add_widget(btn_kapat)
        self.add_widget(alt)

    def _kopyala(self, *_args) -> None:
        try:
            Clipboard.copy(self._text_input.text or "")
        except Exception:
            pass

    def _kapat(self, *_args) -> None:
        try:
            app = App.get_running_app()
            if app is not None:
                app.stop()
        except Exception:
            pass
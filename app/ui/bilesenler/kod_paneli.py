# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/bilesenler/kod_paneli.py

ROL:
- Başlık + kod alanını tek kart içinde sunan ortak panel bileşenidir
- Mevcut kod ve yeni kod alanlarında ortak yapı sağlar
- Kod alanı içinde kaydırma desteği sunar
- Select / copy / paste popup ve seçim oklarını kapatır
- Header üzerinde kopyalama ve tam ekran aksiyonları sağlar
- Kopyalama sonrası dış callback ile bilgi akışına bağlanabilir
- İkon ve başlık okunabilirliği mobil kullanım için güçlendirilmiştir

MİMARİ:
- UI bileşenidir
- Servis katmanını bilmez
- Deterministik çalışır
- Lazy popup cache kullanır
- Type güvenliği yüksektir
- Geriye uyumluluk katmanı içermez
- Alt nesneler tekrar tekrar oluşturulmaz

SURUM: 6
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Callable

from kivy.animation import Animation
from kivy.core.clipboard import Clipboard
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from app.ui.ortak.boyutlar import (
    BOSLUK_SM,
    ICON_16,
    KART_RADIUS,
    PADDING_KART,
    SPACING_SATIR,
)
from app.ui.ortak.ikonlar import ikon_yolu
from app.ui.ortak.renkler import (
    INPUT_IPUCU,
    KART_ALT,
    KENARLIK,
    METIN,
)


class _NoMenuTextInput(TextInput):
    """
    Seçim popup'ı, copy/paste balonu ve seçim okları kapatılmış TextInput.
    """

    __slots__ = ()

    def cancel_selection(self) -> None:
        """
        Güvenli seçim iptali.
        """
        try:
            super().cancel_selection()
        except Exception:
            pass

    def on_touch_down(self, touch):
        """
        Dokunma anında seçim menüsü oluşmasını engeller.
        """
        if self.collide_point(*touch.pos):
            self.cancel_selection()
            try:
                self._handle_left = None
                self._handle_right = None
                self._handle_middle = None
            except Exception:
                pass

        return super().on_touch_down(touch)

    def on_double_tap(self) -> None:
        """
        Çift dokunuş seçim davranışını kapatır.
        """
        self.cancel_selection()

    def _show_cut_copy_paste(self, *_args, **_kwargs):
        """
        Cut/copy/paste popup'ını kapatır.
        """
        return

    def _show_selection_handles(self, *_args, **_kwargs):
        """
        Selection handle oklarını kapatır.
        """
        return

    def _hide_cut_copy_paste(self, *_args, **_kwargs):
        """
        Popup saklama çağrısını no-op yapar.
        """
        return

    def _hide_handles(self, *_args, **_kwargs):
        """
        Selection handle gizleme çağrısını no-op yapar.
        """
        return


class _IconButton(ButtonBehavior, Image):
    """
    Minimal ikon buton.

    Özellikler:
    - Görsel ikon tıklama alanı sağlar
    - Pulse animasyonu ile basım geri bildirimi üretir
    """

    __slots__ = ("_normal_size",)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._normal_size = tuple(self.size)

    def pulse(self) -> None:
        """
        Kısa pulse animasyonu uygular.
        """
        self._normal_size = tuple(self.size)

        buyuk = (
            self._normal_size[0] + dp(4),
            self._normal_size[1] + dp(4),
        )

        anim = (
            Animation(size=buyuk, duration=0.08)
            + Animation(size=self._normal_size, duration=0.10)
        )
        anim.start(self)


class _KodPanelKapsayici(BoxLayout):
    """
    Arka plan ve kenarlık çizen sade kart kapsayıcısı.
    """

    __slots__ = ("_bg_rect", "_line")

    def __init__(
        self,
        *,
        bg_color=KART_ALT,
        line_color=KENARLIK,
        line_width: float = 1.15,
        **kwargs,
    ):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(*bg_color)
            self._bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=KART_RADIUS,
            )

        with self.canvas.after:
            Color(*line_color)
            self._line = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    KART_RADIUS[0] if KART_RADIUS else 0,
                ),
                width=line_width,
            )

        self.bind(pos=self._yenile, size=self._yenile)

    def _yenile(self, *_args) -> None:
        """
        Panel çizimini boyut ve konuma göre günceller.
        """
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._line.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            KART_RADIUS[0] if KART_RADIUS else 0,
        )


class KodPaneli(_KodPanelKapsayici):
    """
    Başlık, kopyalama ve tam ekran aksiyonları ile ortak kod paneli.
    """

    __slots__ = (
        "_baslik_label",
        "_input",
        "_t",
        "_popup",
        "_popup_input",
        "_readonly",
        "_copy_button",
        "_fullscreen_button",
        "_on_copy",
    )

    def __init__(
        self,
        *,
        title: str,
        readonly: bool,
        hint_text: str = "",
        background_color=(0, 0, 0, 1),
        foreground_color=METIN,
        hint_text_color=INPUT_IPUCU,
        multiline: bool = True,
        t: Callable[[str], str] | None = None,
        on_copy: Callable[[], None] | None = None,
        **kwargs,
    ):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("padding", PADDING_KART)
        kwargs.setdefault("spacing", SPACING_SATIR)

        super().__init__(**kwargs)

        self._t = t or (lambda key, **_kwargs: key)
        self._readonly = bool(readonly)
        self._popup = None
        self._popup_input = None
        self._on_copy = on_copy
        self._copy_button = None
        self._fullscreen_button = None

        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(36),
            spacing=dp(10),
        )

        self._baslik_label = self._baslik_olustur(title)
        self._copy_button = self._copy_butonu_olustur()
        self._fullscreen_button = self._fullscreen_butonu_olustur()

        header.add_widget(self._baslik_label)
        header.add_widget(self._copy_button)
        header.add_widget(self._fullscreen_button)

        self.add_widget(header)

        self._input = _NoMenuTextInput(
            readonly=self._readonly,
            multiline=multiline,
            background_color=background_color,
            foreground_color=foreground_color,
            hint_text=str(hint_text or ""),
            hint_text_color=hint_text_color,
            size_hint_y=None,
            font_size=dp(16),
            padding=(dp(12), dp(12), dp(12), dp(12)),
            cursor_width=dp(2),
        )
        self._input.bind(
            minimum_height=lambda inst, val: setattr(inst, "height", max(val, dp(320)))
        )

        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(5),
        )
        scroll.add_widget(self._input)

        self.add_widget(scroll)

    @staticmethod
    def _baslik_olustur(text: str) -> Label:
        """
        Panel başlığını üretir.
        """
        lbl = Label(
            text=str(text or ""),
            size_hint_y=None,
            height=dp(30),
            color=METIN,
            halign="left",
            valign="middle",
            bold=True,
            font_size=dp(18),
            shorten=True,
            shorten_from="right",
        )
        lbl.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))
        return lbl

    def _copy_butonu_olustur(self) -> _IconButton:
        """
        Kopyalama ikon butonunu üretir.
        """
        btn = _IconButton(
            source=ikon_yolu("copy.png"),
            size_hint=(None, None),
            size=(dp(28), dp(28)),
            allow_stretch=True,
            keep_ratio=True,
        )
        btn.bind(on_release=self._kopyala)
        return btn

    def _fullscreen_butonu_olustur(self) -> _IconButton:
        """
        Tam ekran ikon butonunu üretir.
        """
        btn = _IconButton(
            source=ikon_yolu("visibility_on.png"),
            size_hint=(None, None),
            size=(dp(28), dp(28)),
            allow_stretch=True,
            keep_ratio=True,
        )
        btn.bind(on_release=self._toggle_fullscreen)
        return btn

    def _kopyala(self, *_args) -> None:
        """
        Panel içeriğini panoya kopyalar.
        """
        try:
            Clipboard.copy(str(self._input.text or ""))

            if self._copy_button is not None:
                self._copy_button.pulse()

            if callable(self._on_copy):
                self._on_copy()
        except Exception:
            pass

    def _toggle_fullscreen(self, *_args) -> None:
        """
        Tam ekran popup açar / kapatır.
        """
        if self._fullscreen_button is not None:
            self._fullscreen_button.pulse()

        if self._popup is None:
            self._popup_input = _NoMenuTextInput(
                readonly=self._readonly,
                multiline=True,
                background_color=self._input.background_color,
                foreground_color=self._input.foreground_color,
                hint_text="",
                hint_text_color=self._input.hint_text_color,
                size_hint_y=None,
                font_size=dp(18),
                padding=(dp(14), dp(14), dp(14), dp(14)),
                cursor_width=dp(2),
            )
            self._popup_input.bind(
                minimum_height=lambda inst, val: setattr(inst, "height", max(val, dp(500)))
            )

            popup_scroll = ScrollView(
                do_scroll_x=False,
                do_scroll_y=True,
                bar_width=dp(5),
            )
            popup_scroll.add_widget(self._popup_input)

            self._popup = Popup(
                title=self._baslik_label.text,
                content=popup_scroll,
                size_hint=(1, 1),
                auto_dismiss=True,
            )

        if self._popup.parent:
            self._popup.dismiss()
            return

        self._popup_input.text = str(self._input.text or "")
        self._popup.open()

    @property
    def input_widget(self) -> TextInput:
        """
        İç TextInput referansını döndürür.
        """
        return self._input

    @property
    def text(self) -> str:
        """
        Metin alanı içeriğini döndürür.
        """
        return str(self._input.text or "")

    @text.setter
    def text(self, value: str) -> None:
        """
        Metin alanı içeriğini ayarlar.
        """
        self._input.text = str(value or "")

    def temizle(self) -> None:
        """
        Metin alanını temizler.
        """
        self._input.text = ""

    def baslik_ayarla(self, text: str) -> None:
        """
        Panel başlığını günceller.
        """
        self._baslik_label.text = str(text or "")

    def hint_ayarla(self, text: str) -> None:
        """
        Metin alanı ipucu metnini günceller.
        """
        self._input.hint_text = str(text or "")

    def readonly_ayarla(self, value: bool) -> None:
        """
        Salt-okunur durumunu günceller.
        """
        self._readonly = bool(value)
        self._input.readonly = self._readonly

        if self._popup_input is not None:
            self._popup_input.readonly = self._readonly


__all__ = (
    "KodPaneli",
)
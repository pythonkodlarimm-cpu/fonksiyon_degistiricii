# -*- coding: utf-8 -*-
"""
SURUM: 9
"""

from __future__ import annotations

from typing import Callable

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

from app.ui.ortak.boyutlar import (
    BOSLUK_SM,
    PADDING_KART,
    YUKSEKLIK_ALT_DURUM,
)
from app.ui.ortak.renkler import (
    HATA,
    METIN,
    METIN_SOLUK,
)


class BilgiKutusu(BoxLayout):

    __slots__ = ("_ikon", "_label", "_t", "_kapat_event")

    def __init__(
        self,
        *,
        t: Callable[[str], str] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self._t = t or (lambda key, **_kwargs: key)
        self._kapat_event = None

        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = YUKSEKLIK_ALT_DURUM
        self.padding = (PADDING_KART, 0)
        self.spacing = BOSLUK_SM

        self._ikon = Image(
            size_hint=(None, None),
            size=(dp(20), dp(20)),
            opacity=0,
        )

        self._label = Label(
            text=self._t("app_ready") or "Hazır",
            color=METIN_SOLUK,
            halign="left",
            valign="middle",
        )
        self._label.bind(
            size=lambda inst, _val: setattr(inst, "text_size", inst.size)
        )

        self.add_widget(self._ikon)
        self.add_widget(self._label)

    def mesaj(
        self,
        text: str,
        *,
        ikon: str | None = None,
        pulse: bool = False,
        hata: bool = False,
    ) -> None:

        self._label.text = str(text or "")
        self._label.color = HATA if hata else METIN

        # önce eski timer varsa iptal
        if self._kapat_event:
            self._kapat_event.cancel()
            self._kapat_event = None

        if ikon:
            try:
                from app.ui.ortak.ikonlar import ikon_yolu

                self._ikon.source = ikon_yolu(ikon)
                self._ikon.opacity = 1
            except Exception:
                self._ikon.opacity = 0
        else:
            self._ikon.opacity = 0

        if pulse and self._ikon.opacity > 0:
            self._pulse()

        # 🔥 3 saniye sonra ikon kapanır
        self._kapat_event = Clock.schedule_once(self._ikonu_kapat, 3.0)

    def _pulse(self):
        try:
            Animation.cancel_all(self._ikon)

            anim = (
                Animation(opacity=0.5, duration=0.15)
                + Animation(opacity=1.0, duration=0.15)
            )
            anim.start(self._ikon)
        except Exception:
            pass

    def _ikonu_kapat(self, *_args):
        """
        3 saniye sonra ikon gizlenir.
        """
        try:
            Animation.cancel_all(self._ikon)
            self._ikon.opacity = 0
        except Exception:
            pass
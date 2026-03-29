# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/bilesenler/aksiyon_ikon_butonu.py
"""

from __future__ import annotations

from typing import Callable

from kivy.graphics import Color, RoundedRectangle
from kivy.logger import Logger
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label

from app.ui.ortak.boyutlar import (
    ICON_24,
    KART_RADIUS,
)
from app.ui.ortak.ikonlar import ikon_yolu
from app.ui.ortak.renkler import (
    BUTON,
    METIN,
)


class AksiyonIkonButonu(ButtonBehavior, AnchorLayout):
    """
    Ortak ikon butonu.
    """

    __slots__ = (
        "_callback",
        "_arka_plan_rect",
        "_ikon_widget",
        "_normal_renk",
        "_basili_renk",
        "_icon_name",
    )

    def __init__(
        self,
        *,
        icon_name: str,
        on_press_callback: Callable | None = None,
        fallback_text: str = "?",
        button_size: tuple[int, int] = (48, 48),
        icon_size: tuple[int, int] = (ICON_24, ICON_24),
        bg_color=BUTON,
        pressed_factor: float = 0.88,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self._callback = on_press_callback
        self._icon_name = str(icon_name or "")

        self.size_hint = (None, None)
        self.size = button_size
        self.anchor_x = "center"
        self.anchor_y = "center"

        self._normal_renk = tuple(bg_color)
        self._basili_renk = self._renk_koyulastir(self._normal_renk, pressed_factor)

        with self.canvas.before:
            self._bg_color_instruction = Color(*self._normal_renk)
            self._arka_plan_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=KART_RADIUS,
            )

        self.bind(pos=self._yenile, size=self._yenile)

        source = ikon_yolu(icon_name)
        Logger.info(
            f"UIButon: init icon={self._icon_name} "
            f"callback={'var' if callable(self._callback) else 'yok'} "
            f"source={source}"
        )

        if source:
            self._ikon_widget = Image(
                source=source,
                size_hint=(None, None),
                size=icon_size,
                fit_mode="contain",
            )
        else:
            self._ikon_widget = self._fallback_label(
                text=fallback_text,
                size=icon_size,
            )

        self.add_widget(self._ikon_widget)

    @staticmethod
    def _fallback_label(*, text: str, size: tuple[int, int]) -> Label:
        lbl = Label(
            text=str(text or "?"),
            color=METIN,
            bold=True,
            size_hint=(None, None),
            size=size,
            halign="center",
            valign="middle",
        )
        lbl.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))
        return lbl

    @staticmethod
    def _renk_koyulastir(renk, katsayi: float):
        if not isinstance(renk, (list, tuple)) or len(renk) < 3:
            return renk

        r = max(0.0, min(1.0, float(renk[0]) * katsayi))
        g = max(0.0, min(1.0, float(renk[1]) * katsayi))
        b = max(0.0, min(1.0, float(renk[2]) * katsayi))

        if len(renk) >= 4:
            a = max(0.0, min(1.0, float(renk[3])))
            return (r, g, b, a)

        return (r, g, b)

    def _yenile(self, *_args) -> None:
        self._arka_plan_rect.pos = self.pos
        self._arka_plan_rect.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            Logger.info(f"UIButon: touch_down icon={self._icon_name}")
        return super().on_touch_down(touch)

    def on_press(self) -> None:
        Logger.info(f"UIButon: on_press icon={self._icon_name}")
        self._bg_color_instruction.rgba = self._basili_renk

    def on_release(self) -> None:
        Logger.info(
            f"UIButon: on_release icon={self._icon_name} "
            f"callback={'var' if callable(self._callback) else 'yok'}"
        )
        self._bg_color_instruction.rgba = self._normal_renk

        if callable(self._callback):
            try:
                self._callback(self)
                Logger.info(f"UIButon: callback ok icon={self._icon_name}")
            except Exception as exc:
                Logger.exception(
                    f"UIButon: callback hata icon={self._icon_name}: {exc}"
                )

    def on_touch_up(self, touch):
        sonuc = super().on_touch_up(touch)
        self._bg_color_instruction.rgba = self._normal_renk
        return sonuc


__all__ = (
    "AksiyonIkonButonu",
)
# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/bilesenler/fonksiyon_satiri.py

ROL:
- Fonksiyon listesinde tek bir öğeyi profesyonel satır kartı olarak gösterir
- Gerçek fonksiyon adını ve meta bilgisini görünür biçimde sunar
- Seçili / normal durum görselleştirmesini yönetir
- Tıklama ile dış callback tetikler
- Dil entegrasyonuna uyumludur
- Mobil okunabilirlik ve dokunma ergonomisi optimize edilmiştir

MİMARİ:
- UI bileşenidir
- Item verisini dict veya obje üzerinden okuyabilir
- Sabit yükseklikli satır kartı sunar
- Geriye uyumluluk katmanı içermez
- Mevcut dil anahtar seti korunur

SURUM: 4
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Any, Callable

from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from app.ui.ortak.renkler import (
    KART_ALT,
    KENARLIK,
    METIN,
    METIN_SOLUK,
)


class FonksiyonSatiri(ButtonBehavior, BoxLayout):

    __slots__ = (
        "_item",
        "_callback",
        "_secili",
        "_t",
        "_bg_color_instruction",
        "_line_color_instruction",
        "_bg_rect",
        "_line_rect",
        "_ad_label",
        "_meta_label",
    )

    def __init__(
        self,
        *,
        item: Any,
        on_select: Callable[[Any], None] | None = None,
        t: Callable[[str], str] | None = None,
        **kwargs,
    ):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint_y", None)

        # 🔥 DAHA OKUNUR YÜKSEKLİK
        kwargs.setdefault("height", dp(88))

        kwargs.setdefault("spacing", dp(6))
        kwargs.setdefault("padding", (dp(14), dp(12), dp(14), dp(12)))

        super().__init__(**kwargs)

        self._item = item
        self._callback = on_select
        self._secili = False
        self._t = t or (lambda key, **_kwargs: key)

        # =====================================================
        # ARKA PLAN
        # =====================================================
        with self.canvas.before:
            self._bg_color_instruction = Color(*KART_ALT)
            self._bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(20)] * 4,
            )

        with self.canvas.after:
            self._line_color_instruction = Color(*KENARLIK)
            self._line_rect = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dp(20),
                ),
                width=1.2,
            )

        self.bind(pos=self._yenile, size=self._yenile)

        # =====================================================
        # BAŞLIK (FONKSİYON ADI)
        # =====================================================
        self._ad_label = Label(
            text=self._ad_text(),
            color=METIN,
            bold=True,
            halign="left",
            valign="middle",

            # 🔥 DAHA OKUNUR FONT
            font_size=dp(16),

            size_hint_y=None,
            height=dp(30),

            shorten=True,
            shorten_from="right",
        )
        self._ad_label.bind(
            size=lambda inst, _: setattr(inst, "text_size", inst.size)
        )

        # =====================================================
        # META
        # =====================================================
        self._meta_label = Label(
            text=self._meta_text(),
            color=METIN_SOLUK,
            halign="left",
            valign="middle",
            font_size=dp(12),

            size_hint_y=None,
            height=dp(20),

            shorten=True,
            shorten_from="right",
        )
        self._meta_label.bind(
            size=lambda inst, _: setattr(inst, "text_size", inst.size)
        )

        self.add_widget(self._ad_label)
        self.add_widget(self._meta_label)

        self._stili_uygula()

    # =========================================================
    # DRAW UPDATE
    # =========================================================
    def _yenile(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._line_rect.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(20),
        )

    # =========================================================
    # DATA OKUMA
    # =========================================================
    @staticmethod
    def _item_attr(item: Any, *names: str, default=None):
        for name in names:
            if isinstance(item, dict) and name in item:
                return item.get(name)
            if hasattr(item, name):
                return getattr(item, name)
        return default

    def _tr(self, key: str, fallback: str) -> str:
        text = self._t(key)
        return fallback if text == key else str(text or fallback)

    # =========================================================
    # TEXT ÜRETİMİ
    # =========================================================
    def _ad_text(self) -> str:
        fallback = self._tr("function_generic", "Fonksiyon")
        ad = self._item_attr(self._item, "name", "ad", default=fallback)
        return str(ad or fallback)

    def _satir_text(self) -> str:
        start = self._item_attr(self._item, "lineno", "satir", default=None)
        try:
            start_i = int(start) if start else 0
        except Exception:
            start_i = 0

        if start_i > 0:
            return f"{self._tr('line', 'Satır')}: {start_i}"

        return ""

    def _parametre_sayisi(self) -> int | None:
        args = self._item_attr(self._item, "args", "params", default=None)

        if isinstance(args, (list, tuple)):
            return len(args)

        if isinstance(args, str):
            return len([x for x in args.split(",") if x.strip()])

        return None

    def _meta_text(self) -> str:
        parts = []

        satir = self._satir_text()
        if satir:
            parts.append(satir)

        param = self._parametre_sayisi()
        if param is not None:
            parts.append(f"{self._tr('params', 'Param')}: {param}")

        return " • ".join(parts)

    # =========================================================
    # STATE
    # =========================================================
    def secili_yap(self, value: bool) -> None:
        self._secili = bool(value)
        self._stili_uygula()

    def _stili_uygula(self) -> None:
        if self._secili:
            # 🔥 DAHA NET SEÇİLİ STATE
            self._bg_color_instruction.rgba = (0.26, 0.32, 0.46, 1)
            self._line_color_instruction.rgba = (0.45, 0.65, 1.0, 1)
        else:
            self._bg_color_instruction.rgba = KART_ALT
            self._line_color_instruction.rgba = KENARLIK

    # =========================================================
    # EVENT
    # =========================================================
    def on_release(self) -> None:
        if callable(self._callback):
            self._callback(self._item)
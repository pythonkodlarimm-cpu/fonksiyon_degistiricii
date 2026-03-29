# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ekranlar/ayarlar_ekrani.py

ROL:
- Uygulama genel ayar ekranı
- Dil seçimi, genel ayarlar ve developer mode kontrolü sağlar

MİMARİ:
- UI katmanıdır
- Servisler dışarıdan enjekte edilir
- Deterministik davranır
- Dil sistemi ile entegredir

YENİ:
- Developer Mode toggle eklendi
- AyarlarServisi ile bağlı
- Anında persist edilir

SURUM: 13
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Callable

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.switch import Switch


class AyarlarEkrani(BoxLayout):
    """
    Ayarlar ekranı.
    """

    __slots__ = (
        "_servisler",
        "_t",
    )

    def __init__(
        self,
        *,
        servisler,
        t: Callable[[str], str] | None = None,
        **kwargs,
    ) -> None:
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("padding", dp(12))
        kwargs.setdefault("spacing", dp(10))
        super().__init__(**kwargs)

        self._servisler = servisler
        self._t = t or (lambda x, **_: x)

        self._build()

    # =========================================================
    # UI BUILD
    # =========================================================
    def _build(self) -> None:
        # -------------------------------
        # BAŞLIK
        # -------------------------------
        self.add_widget(
            Label(
                text=self._t("settings") or "Ayarlar",
                size_hint_y=None,
                height=dp(40),
                bold=True,
            )
        )

        # -------------------------------
        # DEVELOPER MODE
        # -------------------------------
        self.add_widget(self._developer_mode_satiri())

    # =========================================================
    # DEVELOPER MODE UI
    # =========================================================
    def _developer_mode_satiri(self) -> BoxLayout:
        """
        Developer mode toggle satırı.
        """

        layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
        )

        label = Label(
            text=self._t("developer_mode") or "Geliştirici Modu",
            halign="left",
            valign="middle",
        )
        label.bind(size=lambda inst, val: setattr(inst, "text_size", inst.size))

        switch = Switch(
            active=self._servisler.ayarlar().developer_mode_aktif_mi()
        )

        switch.bind(active=self._on_dev_mode_degisti)

        layout.add_widget(label)
        layout.add_widget(switch)

        return layout

    # =========================================================
    # AKSİYON
    # =========================================================
    def _on_dev_mode_degisti(self, _switch, value: bool) -> None:
        """
        Developer mode değiştiğinde tetiklenir.
        """

        self._servisler.ayarlar().developer_mode_ayarla(value)
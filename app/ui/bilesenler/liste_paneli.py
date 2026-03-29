# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/bilesenler/liste_paneli.py

ROL:
- Başlık ve içerik alanı olan sade liste/kart panel bileşenini sağlar
- Fonksiyon listesi gibi içerikleri kart görünümünde sunar
- Ortak panel dili ile uyumlu tekrar kullanılabilir kapsayıcı sunar
- Başlık ve içerik alanını tek kart içinde düzenli biçimde toplar
- Dil değişimlerinde başlığı güvenli biçimde yenileyebilir

MİMARİ:
- UI bileşenidir
- Servis katmanını bilmez
- İçerik widget'ı dışarıdan eklenir
- Scroll yönetimini içerik widget'ına bırakır
- Ortak renk, boyut ve panel çizim sistemine uyar
- Geriye uyumluluk katmanı içermez
- Mevcut dil anahtar seti korunur

SURUM: 5
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Callable

from kivy.graphics import Color, Line, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from app.ui.ortak.boyutlar import (
    BOSLUK_SM,
    ICON_16,
    KART_RADIUS,
    PADDING_KART,
    SPACING_SATIR,
)
from app.ui.ortak.renkler import (
    KART_ALT,
    KENARLIK,
    METIN,
)


class ListePaneli(BoxLayout):
    """
    Başlık ve içerik alanı olan sade kart paneli.
    """

    __slots__ = (
        "_bg_rect",
        "_line",
        "_baslik_label",
        "_t",
        "_title_key",
        "_title_fallback",
    )

    def __init__(
        self,
        *,
        title: str = "",
        t: Callable[[str], str] | None = None,
        title_key: str | None = None,
        title_fallback: str | None = None,
        **kwargs,
    ):
        """
        Liste panelini oluşturur.

        Args:
            title:
                Doğrudan başlık metni.
            t:
                Çeviri fonksiyonu.
            title_key:
                Başlık için dil anahtarı.
            title_fallback:
                Çeviri çözülemezse kullanılacak fallback başlık.
            **kwargs:
                BoxLayout argümanları.
        """
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("padding", PADDING_KART)
        kwargs.setdefault("spacing", SPACING_SATIR)

        super().__init__(**kwargs)

        self._t = t or (lambda key, **_kwargs: key)
        self._title_key = str(title_key or "").strip() or None
        self._title_fallback = (
            str(title_fallback or "").strip()
            or str(title or "").strip()
        )

        with self.canvas.before:
            Color(*KART_ALT)
            self._bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=KART_RADIUS,
            )

        with self.canvas.after:
            Color(*KENARLIK)
            self._line = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    KART_RADIUS[0] if KART_RADIUS else 0,
                ),
                width=1.15,
            )

        self.bind(pos=self._yenile, size=self._yenile)

        self._baslik_label = Label(
            text=self._baslik_metni_coz(title),
            size_hint_y=None,
            height=ICON_16 + BOSLUK_SM,
            color=METIN,
            halign="left",
            valign="middle",
            bold=True,
            font_size=ICON_16 - 1,
        )
        self._baslik_label.bind(
            size=lambda inst, _val: setattr(inst, "text_size", inst.size)
        )
        self.add_widget(self._baslik_label)

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

    def _tr(self, key: str, fallback: str) -> str:
        """
        Dil anahtarını çözer; çözülemezse fallback döner.
        """
        text = self._t(key)
        if text == key:
            return str(fallback or "")
        return str(text or fallback or "")

    def _baslik_metni_coz(self, direct_title: str = "") -> str:
        """
        Başlık metnini dil anahtarı veya doğrudan metin üzerinden çözer.
        """
        if self._title_key:
            return self._tr(self._title_key, self._title_fallback or direct_title)

        return str(direct_title or self._title_fallback or "")

    def baslik_ayarla(self, text: str) -> None:
        """
        Panel başlığını doğrudan günceller.
        """
        self._title_key = None
        self._title_fallback = str(text or "")
        self._baslik_label.text = str(text or "")

    def baslik_key_ayarla(
        self,
        key: str,
        fallback: str = "",
    ) -> None:
        """
        Panel başlığını dil anahtarı üzerinden ayarlar.
        """
        self._title_key = str(key or "").strip() or None
        self._title_fallback = str(fallback or "").strip()
        self.baslik_yenile()

    def baslik_yenile(self) -> None:
        """
        Mevcut dil fonksiyonu ile başlığı yeniden çözer.
        """
        self._baslik_label.text = self._baslik_metni_coz()


__all__ = (
    "ListePaneli",
)
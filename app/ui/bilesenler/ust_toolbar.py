# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/bilesenler/ust_toolbar.py

ROL:
- Uygulama üst alanında kullanılacak sade toolbar bileşenini sağlar
- Sol tarafta menü ikon aksiyonunu içerir
- Orta alanda başlık metnini ve isteğe bağlı sürüm bilgisini gösterir
- Ortak UI stil ve boyut sistemine uyar
- Dil entegrasyonuna uyumludur
- Dil değişimlerinde başlık ve sürüm etiketini güvenli şekilde yenileyebilir

MİMARİ:
- UI bileşenidir
- Servis katmanını bilmez
- Callback dışarıdan enjekte edilir
- Çeviri fonksiyonu dışarıdan alınır
- Ortak ikon butonu bileşenini kullanır
- Geriye uyumluluk katmanı içermez
- Mevcut dil anahtar seti korunur
- Hardcoded başlık yerine anahtar + fallback sistemi kullanır
- Sürüm metni dışarıdan verilir; toolbar bunu sadece gösterir

SURUM: 5
TARIH: 2026-03-29
IMZA: FY.
"""

from __future__ import annotations

from typing import Callable

from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from app.ui.bilesenler.aksiyon_ikon_butonu import AksiyonIkonButonu
from app.ui.ortak.boyutlar import (
    BOSLUK_LG,
    BOSLUK_SM,
    BOSLUK_XS,
    ICON_24,
    KART_RADIUS,
    YUKSEKLIK_TOOLBAR,
)
from app.ui.ortak.renkler import (
    AYIRICI,
    KART_ALT,
    METIN,
    METIN_SOLUK,
)


class _ToolbarPanel(BoxLayout):
    """
    Toolbar arka plan ve kenarlık kapsayıcısı.
    """

    __slots__ = ("_bg_rect", "_line")

    def __init__(
        self,
        *,
        bg_color=KART_ALT,
        line_color=AYIRICI,
        line_width: float = 1.0,
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
        Arka plan ve kenarlık çizimini günceller.
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


class UstToolbar(_ToolbarPanel):
    """
    Sol menü ikonu, ortada başlık ve isteğe bağlı sürüm metni gösteren üst toolbar.
    """

    __slots__ = (
        "_t",
        "_on_menu",
        "_title_label",
        "_version_label",
        "_title_key",
        "_fallback_title",
        "_version_text",
    )

    def __init__(
        self,
        *,
        on_menu: Callable | None = None,
        t: Callable[[str], str] | None = None,
        title_key: str = "app_title",
        fallback_title: str = "Fonksiyon Değiştirici",
        version_text: str = "",
        **kwargs,
    ):
        """
        Toolbar bileşenini oluşturur.
        """
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", YUKSEKLIK_TOOLBAR)
        kwargs.setdefault("padding", (BOSLUK_SM, BOSLUK_XS, BOSLUK_SM, BOSLUK_XS))
        kwargs.setdefault("spacing", BOSLUK_SM)

        self._t = t or (lambda key, **_kwargs: key)
        self._on_menu = on_menu
        self._title_key = str(title_key or "").strip()
        self._fallback_title = str(fallback_title or "").strip()
        self._version_text = str(version_text or "").strip()

        super().__init__(**kwargs)

        self._sol_alani_kur()
        self._orta_alani_kur()
        self._sag_alani_kur()

    def _sol_alani_kur(self) -> None:
        """
        Sol menü butonu alanını kurar.
        """
        sol = BoxLayout(
            orientation="horizontal",
            size_hint=(None, 1),
            width=YUKSEKLIK_TOOLBAR,
        )
        sol.add_widget(
            AksiyonIkonButonu(
                icon_name="menu.png",
                on_press_callback=self._on_menu,
                fallback_text="M",
                button_size=(
                    YUKSEKLIK_TOOLBAR - BOSLUK_LG,
                    YUKSEKLIK_TOOLBAR - BOSLUK_LG,
                ),
                icon_size=(ICON_24, ICON_24),
            )
        )
        self.add_widget(sol)

    def _orta_alani_kur(self) -> None:
        """
        Başlık ve sürüm alanını kurar.
        """
        orta = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
        )

        orta_icerik = BoxLayout(
            orientation="vertical",
            spacing=0,
            size_hint=(1, 1),
        )

        self._title_label = Label(
            text=self._baslik_metni_coz(),
            color=METIN,
            bold=True,
            halign="center",
            valign="middle",
            size_hint=(1, None),
            height=dp(28),
            font_size=dp(16),
        )
        self._title_label.bind(
            size=lambda inst, _val: setattr(inst, "text_size", inst.size)
        )

        self._version_label = Label(
            text=self._version_text,
            color=METIN_SOLUK,
            halign="center",
            valign="middle",
            size_hint=(1, None),
            height=dp(16),
            font_size=dp(11),
            shorten=True,
            shorten_from="right",
        )
        self._version_label.bind(
            size=lambda inst, _val: setattr(inst, "text_size", inst.size)
        )

        orta_icerik.add_widget(Widget())
        orta_icerik.add_widget(self._title_label)
        orta_icerik.add_widget(self._version_label)
        orta_icerik.add_widget(Widget())

        orta.add_widget(orta_icerik)
        self.add_widget(orta)

    def _sag_alani_kur(self) -> None:
        """
        Sağ boş denge alanını kurar.
        """
        sag = BoxLayout(
            orientation="horizontal",
            size_hint=(None, 1),
            width=YUKSEKLIK_TOOLBAR,
        )
        sag.add_widget(Widget())
        self.add_widget(sag)

    def _tr(self, key: str, fallback: str) -> str:
        """
        Dil anahtarını güvenli biçimde çözer.
        """
        if not key:
            return str(fallback or "")

        try:
            sonuc = self._t(key)
            metin = str(sonuc or "").strip()
            if metin and metin != key:
                return metin
        except Exception:
            pass

        return str(fallback or "")

    def _baslik_metni_coz(self) -> str:
        """
        Geçerli başlık metnini dil sistemi üzerinden çözer.
        """
        return self._tr(
            self._title_key,
            self._fallback_title,
        )

    def baslik_guncelle(
        self,
        *,
        title_key: str | None = None,
        fallback_title: str | None = None,
    ) -> None:
        """
        Başlığı çeviri anahtarı üzerinden günceller.
        """
        if title_key is not None:
            self._title_key = str(title_key or "").strip()

        if fallback_title is not None:
            self._fallback_title = str(fallback_title or "").strip()

        self._title_label.text = self._baslik_metni_coz()

    def baslik_yenile(self) -> None:
        """
        Mevcut çeviri fonksiyonu ile başlığı yeniden çözer.
        """
        self._title_label.text = self._baslik_metni_coz()

    def baslik_metni_ayarla(self, text: str) -> None:
        """
        Başlığı doğrudan verilen metin ile günceller.
        """
        self._title_key = ""
        self._fallback_title = str(text or "")
        self._title_label.text = str(text or "")

    def surum_metni_ayarla(self, text: str) -> None:
        """
        Sürüm etiketini günceller.
        """
        self._version_text = str(text or "").strip()

        if self._version_label is not None:
            self._version_label.text = self._version_text

    def surum_metni_yenile(self) -> None:
        """
        Mevcut sürüm metnini yeniden uygular.
        """
        if self._version_label is not None:
            self._version_label.text = self._version_text

    def tum_metinleri_yenile(self) -> None:
        """
        Başlık ve sürüm etiketini birlikte yeniler.
        """
        self.baslik_yenile()
        self.surum_metni_yenile()


__all__ = (
    "UstToolbar",
        )

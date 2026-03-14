# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/iconlu_baslik.py
ROL:
- İkon + metin gösteren ortak başlık bileşeni
- Kart başlıkları, bölüm başlıkları ve üst bilgi alanlarında kullanılır

GÖRSEL HEDEF:
- Daha profesyonel başlık görünümü
- Daha düzgün ikon hizası
- Daha net tipografi
- Mobilde daha temiz boşluk dengesi

GUNCELLEME:
- Daha sade ve uyumlu yerleşim
- İkon / metin aynı satırda stabil hizalanır
- İkon sonradan değiştirilebilir
- Uzun başlıklarda taşma azaltılır
"""

from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from app.ui.icon_yardimci import icon_path


class IconluBaslik(BoxLayout):
    """
    Ortak ikonlu başlık bileşeni.

    Özellikler:
    - solda ikon, sağda metin
    - mobil uyumlu sabit yükseklik
    - uzun metinlerde taşmadan okunabilir görünüm
    - başlık seviyesine uygun daha güçlü tipografi
    - ikon yoksa da hizası bozulmaz
    """

    def __init__(
        self,
        text: str,
        icon_name: str = "",
        height_dp: int = 36,
        font_size: str = "16sp",
        color=(0.96, 0.97, 1, 1),
        bold: bool = True,
        icon_size_dp: int | None = None,
        spacing_dp: int = 10,
        icon_opacity: float = 0.96,
        **kwargs,
    ):
        super().__init__(
            orientation="horizontal",
            spacing=dp(spacing_dp),
            size_hint_y=None,
            height=dp(height_dp),
            **kwargs,
        )

        self._base_color = tuple(color)
        self._base_height_dp = int(height_dp)
        self._icon_size_dp = int(icon_size_dp or max(18, height_dp - 10))
        self._icon_opacity = float(icon_opacity)
        self._icon_name = str(icon_name or "").strip()

        self.icon = None

        kaynak = icon_path(self._icon_name)
        if kaynak:
            self.icon = Image(
                source=kaynak,
                size_hint=(None, None),
                size=(dp(self._icon_size_dp), dp(self._icon_size_dp)),
                allow_stretch=True,
                keep_ratio=True,
                color=self._base_color,
                opacity=self._icon_opacity,
            )
            self.add_widget(self.icon)
        else:
            self.add_widget(
                Widget(
                    size_hint=(None, None),
                    size=(dp(self._icon_size_dp), dp(self._icon_size_dp)),
                )
            )

        self.label = Label(
            text=str(text or ""),
            color=self._base_color,
            bold=bool(bold),
            halign="left",
            valign="middle",
            font_size=font_size,
            shorten=True,
            shorten_from="right",
            max_lines=1,
        )
        self.label.bind(size=self._sync_label_size)
        self.add_widget(self.label)

    def _sync_label_size(self, widget, size):
        widget.text_size = (size[0], size[1])

    def set_text(self, text: str) -> None:
        self.label.text = str(text or "")

    def set_color(self, color) -> None:
        try:
            self._base_color = tuple(color)
        except Exception:
            return

        try:
            self.label.color = self._base_color
        except Exception:
            pass

        try:
            if self.icon is not None:
                self.icon.color = self._base_color
        except Exception:
            pass

    def set_icon(self, icon_name: str) -> None:
        yeni_ad = str(icon_name or "").strip()
        if not yeni_ad:
            return

        kaynak = icon_path(yeni_ad)
        if not kaynak:
            return

        if self.icon is None:
            try:
                if self.children:
                    self.remove_widget(self.children[-1])
            except Exception:
                pass

            self.icon = Image(
                source=kaynak,
                size_hint=(None, None),
                size=(dp(self._icon_size_dp), dp(self._icon_size_dp)),
                allow_stretch=True,
                keep_ratio=True,
                color=self._base_color,
                opacity=self._icon_opacity,
            )
            self.add_widget(self.icon, index=len(self.children))
        else:
            self.icon.source = kaynak

        self._icon_name = yeni_ad
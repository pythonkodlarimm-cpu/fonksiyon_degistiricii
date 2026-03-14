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

APK / ANDROID NOTLARI:
- İkon yükleme güvenli yapılır
- Boş ikon durumunda yer tutucu korunur
- source değişince reload() denenir
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
        self._icon_placeholder = None

        self._build_left_icon_area()
        self._build_label(text=text, font_size=font_size, bold=bold)

    def _build_left_icon_area(self) -> None:
        kaynak = icon_path(self._icon_name)

        if kaynak:
            self.icon = self._create_icon_widget(kaynak)
            self.add_widget(self.icon)
            self._icon_placeholder = None
        else:
            self._icon_placeholder = self._create_placeholder_widget()
            self.add_widget(self._icon_placeholder)
            self.icon = None

    def _build_label(self, text: str, font_size: str, bold: bool) -> None:
        self.label = Label(
            text=str(text or ""),
            size_hint_x=1,
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

    def _create_icon_widget(self, source: str) -> Image:
        return Image(
            source=source,
            size_hint=(None, None),
            size=(dp(self._icon_size_dp), dp(self._icon_size_dp)),
            color=self._base_color,
            opacity=self._icon_opacity,
        )

    def _create_placeholder_widget(self) -> Widget:
        return Widget(
            size_hint=(None, None),
            size=(dp(self._icon_size_dp), dp(self._icon_size_dp)),
        )

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
                if self._icon_placeholder is not None and self._icon_placeholder in self.children:
                    self.remove_widget(self._icon_placeholder)
            except Exception:
                pass

            self._icon_placeholder = None
            self.icon = self._create_icon_widget(kaynak)
            self.add_widget(self.icon, index=len(self.children))
        else:
            try:
                self.icon.source = kaynak
                self.icon.opacity = self._icon_opacity
                self.icon.color = self._base_color
                self.icon.reload()
            except Exception:
                pass

        self._icon_name = yeni_ad

    def clear_icon(self) -> None:
        try:
            if self.icon is not None and self.icon in self.children:
                self.remove_widget(self.icon)
        except Exception:
            pass

        self.icon = None

        if self._icon_placeholder is None:
            self._icon_placeholder = self._create_placeholder_widget()

        try:
            if self._icon_placeholder not in self.children:
                self.add_widget(self._icon_placeholder, index=len(self.children))
        except Exception:
            pass

        self._icon_name = ""
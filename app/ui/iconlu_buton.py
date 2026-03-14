# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/iconlu_buton.py
ROL:
- İkon + metin gösteren ortak buton bileşeni
- Mobil uyumlu, okunaklı ve profesyonel görünüm sağlar

GÖRSEL HEDEF:
- Daha güçlü kart hissi
- Daha net ikon hizası
- Daha okunur metin
- Basışta hafif görsel geri bildirim
- Disabled durumda daha anlaşılır görünüm

GUNCELLEME:
- Daha uyumlu canvas yapısı
- İçeriği kapatmayan sade arka plan
- icon_only yerleşimi düzeltildi
- Label / icon hizası stabil hale getirildi
"""

from __future__ import annotations

from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

from app.ui.icon_yardimci import icon_path


class IconluButon(ButtonBehavior, BoxLayout):
    """
    Ortak ikonlu buton.

    Özellikler:
    - Sol tarafta ikon, sağda metin
    - Yuvarlatılmış modern arka plan
    - Basışta renk + hafif küçülme geri bildirimi
    - Mobilde daha rahat dokunma alanı
    - Disabled görünümü desteklenir
    """

    icon_only = BooleanProperty(False)
    _base_scale = NumericProperty(1.0)

    def __init__(
        self,
        text: str,
        icon_name: str = "",
        bg=(0.18, 0.18, 0.22, 1),
        fg=(0.96, 0.97, 1, 1),
        radius=18,
        icon_width_dp=24,
        font_size="14sp",
        height_dp=56,
        padding_x_dp=14,
        spacing_dp=10,
        **kwargs,
    ):
        super().__init__(
            orientation="horizontal",
            spacing=dp(spacing_dp),
            padding=(dp(padding_x_dp), dp(10)),
            size_hint_y=None,
            height=dp(height_dp),
            **kwargs,
        )

        self._radius = float(radius)

        self._normal_bg = tuple(bg)
        self._down_bg = self._calc_pressed_bg(self._normal_bg)
        self._disabled_bg = self._calc_disabled_bg(self._normal_bg)

        self._normal_fg = tuple(fg)
        self._disabled_fg = self._calc_disabled_fg(self._normal_fg)

        self._pressed_scale = 0.985
        self._icon_px = dp(icon_width_dp)

        with self.canvas.before:
            self._bg_color = Color(*self._normal_bg)
            self.bg_rect = RoundedRectangle(radius=[dp(self._radius)])

        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
            disabled=self._sync_disabled_state,
            _base_scale=lambda *_: self._update_canvas(),
        )

        source = icon_path(icon_name)
        self.icon = None
        if source:
            self.icon = Image(
                source=source,
                size_hint=(None, None),
                size=(self._icon_px, self._icon_px),
                allow_stretch=True,
                keep_ratio=True,
                color=self._normal_fg,
            )
            self.add_widget(self.icon)

        self.label = Label(
            text=str(text or ""),
            color=self._normal_fg,
            halign="left",
            valign="middle",
            font_size=font_size,
            bold=True,
            shorten=True,
            shorten_from="right",
        )
        self.label.bind(size=self._sync_label_size)

        if str(text or "").strip():
            self.add_widget(self.label)
            self.icon_only = False
        else:
            self.icon_only = True

        self._sync_content_layout()
        self._sync_disabled_state()
        self._update_canvas()

    # =========================================================
    # RENK HESAPLARI
    # =========================================================
    def _calc_pressed_bg(self, rgba):
        r, g, b, a = rgba
        factor = 0.88
        return (r * factor, g * factor, b * factor, a)

    def _calc_disabled_bg(self, rgba):
        r, g, b, a = rgba
        return (
            min(1, r * 0.72),
            min(1, g * 0.72),
            min(1, b * 0.72),
            a * 0.92,
        )

    def _calc_disabled_fg(self, rgba):
        r, g, b, a = rgba
        return (
            min(1, r * 0.78 + 0.10),
            min(1, g * 0.78 + 0.10),
            min(1, b * 0.78 + 0.10),
            a * 0.85,
        )

    # =========================================================
    # LAYOUT / CANVAS
    # =========================================================
    def _sync_label_size(self, widget, size):
        widget.text_size = (size[0], None)

    def _sync_content_layout(self):
        if self.icon_only:
            self.orientation = "horizontal"
            self.spacing = dp(0)
            self.padding = (dp(10), dp(10))
            self.size_hint_x = self.size_hint_x
        else:
            self.orientation = "horizontal"
            self.spacing = dp(10)

    def _update_canvas(self, *_args):
        scale = float(getattr(self, "_base_scale", 1.0) or 1.0)

        scaled_w = self.width * scale
        scaled_h = self.height * scale
        x = self.center_x - (scaled_w / 2.0)
        y = self.center_y - (scaled_h / 2.0)

        self.bg_rect.pos = (x, y)
        self.bg_rect.size = (scaled_w, scaled_h)

    def _animate_scale(self, scale_value: float, duration: float):
        Animation.cancel_all(self, "_base_scale")
        Animation(_base_scale=scale_value, duration=duration).start(self)

    def _sync_disabled_state(self, *_args):
        try:
            if self.disabled:
                self._bg_color.rgba = self._disabled_bg
                self.opacity = 0.82
                self.label.color = self._disabled_fg
                if self.icon is not None:
                    self.icon.color = self._disabled_fg
            else:
                self._bg_color.rgba = self._normal_bg
                self.opacity = 1
                self.label.color = self._normal_fg
                if self.icon is not None:
                    self.icon.color = self._normal_fg
        except Exception:
            pass

    # =========================================================
    # PUBLIC API
    # =========================================================
    def set_text(self, text: str) -> None:
        yeni_metin = str(text or "")
        label_var = self.label.parent is self

        self.label.text = yeni_metin

        if yeni_metin.strip():
            if not label_var:
                self.add_widget(self.label)
            self.icon_only = False
        else:
            if label_var:
                self.remove_widget(self.label)
            self.icon_only = True

        self._sync_content_layout()

    def set_colors(self, *, bg=None, fg=None) -> None:
        if bg is not None:
            self._normal_bg = tuple(bg)
            self._down_bg = self._calc_pressed_bg(self._normal_bg)
            self._disabled_bg = self._calc_disabled_bg(self._normal_bg)

        if fg is not None:
            self._normal_fg = tuple(fg)
            self._disabled_fg = self._calc_disabled_fg(self._normal_fg)

        self._sync_disabled_state()

    # =========================================================
    # BUTTON FEEDBACK
    # =========================================================
    def on_press(self):
        try:
            if not self.disabled:
                self._bg_color.rgba = self._down_bg
                self.opacity = 0.98
                self._animate_scale(self._pressed_scale, 0.06)
        except Exception:
            pass
        return super().on_press()

    def on_release(self):
        try:
            if not self.disabled:
                self._bg_color.rgba = self._normal_bg
                self.opacity = 1
                self._animate_scale(1.0, 0.08)
        except Exception:
            pass
        return super().on_release()
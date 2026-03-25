# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/bilesenler/editor_bilesenleri.py

ROL:
- Editör paketinin temel görsel bileşenlerini sağlamak
- Kod editörü, bilgi kutusu ve sade kod alanı bileşenlerini tanımlamak
- Editör paneli için tekrar kullanılabilir UI yapı taşları üretmek
- Aktif dile göre görünür metinleri yenileyebilmek

MİMARİ:
- Bu dosya sadece bileşen tanımlar
- Üst katman doğrudan bu modüle değil, bilesenler/yoneticisi.py üzerinden erişmelidir
- Platform bağımsız UI bileşenleri içerir
- Görünen sabit metinler ServicesYoneticisi üzerinden çözülebilir
- Dil değişiminde mevcut görünen varsayılan metinler güvenli şekilde yenilenir
- Hint text güncellemesi doğrudan editör widget'ına da yansıtılır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 4
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.codeinput import CodeInput
from kivy.uix.image import Image
from kivy.uix.label import Label
from pygments.lexers import PythonLexer

from app.services.yoneticisi import ServicesYoneticisi
from app.ui.tema import INPUT_BG, RADIUS_MD


class KodEditoru(CodeInput):
    """Temel Python editörü."""

    error_line = NumericProperty(0)

    def __init__(self, readonly=False, hint_text="", **kwargs):
        self.hint_text = str(hint_text or "")

        kwargs.setdefault("lexer", PythonLexer())
        kwargs.setdefault("readonly", readonly)
        kwargs.setdefault("multiline", True)
        kwargs.setdefault("do_wrap", False)
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_active", "")
        kwargs.setdefault("background_color", (0.07, 0.09, 0.12, 1))
        kwargs.setdefault("foreground_color", (0.96, 0.97, 1, 1))
        kwargs.setdefault("cursor_color", (1, 1, 1, 1))
        kwargs.setdefault("selection_color", (0.20, 0.35, 0.55, 0.45))
        kwargs.setdefault("font_size", "16sp")
        kwargs.setdefault("padding", (dp(12), dp(4), dp(12), dp(8)))
        kwargs.setdefault("write_tab", False)
        kwargs.setdefault("tab_width", 4)
        kwargs.setdefault("scroll_from_swipe", True)
        kwargs.setdefault("size_hint", (1, 1))
        kwargs.setdefault("style_name", "monokai")

        super().__init__(**kwargs)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        try:
            key = keycode[1]
        except Exception:
            return super().keyboard_on_key_down(window, keycode, text, modifiers)

        if not self.readonly and key == "enter":
            self._insert_auto_indent()
            return True

        if not self.readonly and key == "tab":
            self.insert_text("    ")
            return True

        return super().keyboard_on_key_down(window, keycode, text, modifiers)

    def _insert_auto_indent(self):
        try:
            _cursor_col, cursor_row = self.cursor
            lines = self.text.split("\n")
            current_line = lines[cursor_row] if 0 <= cursor_row < len(lines) else ""
            current_indent = current_line[
                : len(current_line) - len(current_line.lstrip(" "))
            ]
            extra_indent = "    " if current_line.rstrip().endswith(":") else ""
            self.insert_text("\n" + current_indent + extra_indent)
        except Exception:
            self.insert_text("\n")

    def reset_view_to_top(self):
        try:
            self.cursor = (0, 0)
        except Exception:
            pass

        try:
            self.scroll_x = 0
        except Exception:
            pass

        try:
            self.scroll_y = 1
        except Exception:
            pass

    def scroll_to_top(self):
        self.reset_view_to_top()
        Clock.schedule_once(lambda *_: self.reset_view_to_top(), 0)
        Clock.schedule_once(lambda *_: self.reset_view_to_top(), 0.03)
        Clock.schedule_once(lambda *_: self.reset_view_to_top(), 0.08)

    def set_error_line(self, line_no: int):
        try:
            self.error_line = max(0, int(line_no or 0))
        except Exception:
            self.error_line = 0

    def set_hint_text(self, text: str) -> None:
        try:
            self.hint_text = str(text or "")
        except Exception:
            self.hint_text = ""


class KodPaneli(BoxLayout):
    def __init__(self, bg=INPUT_BG, border=(0.18, 0.24, 0.34, 1), **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            self._bg_color = Color(*tuple(bg))
            self._bg_rect = RoundedRectangle(radius=[dp(RADIUS_MD)])

        with self.canvas.after:
            self._border_color = Color(*tuple(border))
            self._border_line = Line(
                rounded_rectangle=(0, 0, 0, 0, dp(RADIUS_MD)),
                width=1.1,
            )

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

    def _update_canvas(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._border_line.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(RADIUS_MD),
        )


class BilgiKutusu(BoxLayout):
    def __init__(
        self,
        services: ServicesYoneticisi | None = None,
        **kwargs,
    ):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            padding=(dp(12), dp(8)),
            spacing=dp(10),
            **kwargs,
        )

        self.services = services or ServicesYoneticisi()

        self._pulse_anim = None
        self._pulse_stop_event = None
        self._last_tone = "info"

        self._bg_info = (0.10, 0.16, 0.22, 1)
        self._bg_success = (0.08, 0.24, 0.14, 1)
        self._bg_warning = (0.24, 0.18, 0.08, 1)
        self._bg_error = (0.24, 0.12, 0.12, 1)

        with self.canvas.before:
            self._bg_color = Color(*self._bg_info)
            self._bg_rect = RoundedRectangle(radius=[dp(12)])

        with self.canvas.after:
            self._border_color = Color(0.20, 0.24, 0.30, 1)
            self._border_line = Line(
                rounded_rectangle=(0, 0, 0, 0, dp(12)),
                width=1.0,
            )

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

        self.status_icon = Image(
            source="app/assets/icons/onaylandi.png",
            size_hint=(None, None),
            size=(dp(22), dp(22)),
            opacity=0,
            allow_stretch=True,
            keep_ratio=True,
        )
        self.add_widget(self.status_icon)

        self.label = Label(
            text=self._m("app_ready", "Hazır."),
            halign="left",
            valign="middle",
            color=(0.88, 0.94, 1, 1),
            font_size="13sp",
            shorten=True,
            shorten_from="right",
        )
        self.label.bind(size=self._sync_label_size)
        self.add_widget(self.label)

    # =========================================================
    # DIL
    # =========================================================
    def _m(self, anahtar: str, default: str = "") -> str:
        try:
            return str(self.services.metin(anahtar, default) or default or anahtar)
        except Exception:
            return str(default or anahtar)

    def refresh_language(self) -> None:
        try:
            mevcut = str(self.label.text or "").strip()

            info_varsayilanlari = {
                "Hazır.",
                "Hazır",
                "Ready.",
                "Ready",
                "Bereit.",
                "Bereit",
            }
            warning_varsayilanlari = {
                "Uyarı",
                "Warning",
                "Warnung",
            }
            success_varsayilanlari = {
                "İşlem başarılı",
                "Operation successful",
                "Vorgang erfolgreich",
            }
            error_varsayilanlari = {
                "Bir hata oluştu",
                "An error occurred",
                "Ein Fehler ist aufgetreten",
            }

            if self._last_tone == "info":
                if not mevcut or mevcut in info_varsayilanlari:
                    self.label.text = self._m("app_ready", "Hazır.")
            elif self._last_tone == "warning":
                if not mevcut or mevcut in warning_varsayilanlari:
                    self.label.text = self._m("warning", "Uyarı")
            elif self._last_tone == "success":
                if not mevcut or mevcut in success_varsayilanlari:
                    self.label.text = self._m(
                        "processing_successful",
                        "İşlem başarılı",
                    )
            elif self._last_tone == "error":
                if not mevcut or mevcut in error_varsayilanlari:
                    self.label.text = self._m(
                        "an_error_occurred",
                        "Bir hata oluştu",
                    )
        except Exception:
            pass

    # =========================================================
    # INTERNAL
    # =========================================================
    def _update_canvas(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._border_line.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(12),
        )

    def _sync_label_size(self, widget, size):
        widget.text_size = (size[0], None)

    def _cancel_pulse_stop_event(self):
        try:
            if self._pulse_stop_event is not None:
                self._pulse_stop_event.cancel()
        except Exception:
            pass
        self._pulse_stop_event = None

    def _stop_pulse(self):
        self._cancel_pulse_stop_event()
        try:
            if self._pulse_anim is not None:
                self._pulse_anim.cancel(self.status_icon)
        except Exception:
            pass
        self._pulse_anim = None

        try:
            self.status_icon.opacity = 1 if self.status_icon.source else 0
            self.status_icon.size = (dp(22), dp(22))
        except Exception:
            pass

    def _start_pulse(self, seconds: float | None = None):
        self._stop_pulse()
        try:
            self.status_icon.opacity = 1
            self.status_icon.size = (dp(22), dp(22))
            anim = (
                Animation(opacity=0.68, size=(dp(26), dp(26)), duration=0.45)
                + Animation(opacity=1.0, size=(dp(22), dp(22)), duration=0.45)
            )
            anim.repeat = seconds is None
            anim.start(self.status_icon)
            self._pulse_anim = anim

            if seconds is not None:
                self._pulse_stop_event = Clock.schedule_once(
                    lambda *_: self._stop_pulse(),
                    max(0.1, float(seconds)),
                )
        except Exception:
            self.status_icon.opacity = 1

    def _hide_icon(self):
        self._stop_pulse()
        self.status_icon.opacity = 0

    # =========================================================
    # PUBLIC
    # =========================================================
    def set_text(self, text: str):
        self.label.text = str(text or "")

    def set_info(self, text: str):
        self._last_tone = "info"
        self.set_text(text)
        self._hide_icon()
        self._bg_color.rgba = self._bg_info
        self._border_color.rgba = (0.20, 0.24, 0.30, 1)
        self.label.color = (0.88, 0.94, 1, 1)

    def set_neutral(self):
        self.set_info(self._m("app_ready", "Hazır."))

    def set_success(self, text: str, pulse_seconds: float = 6.0):
        self._last_tone = "success"
        self.set_text(text)
        self._bg_color.rgba = self._bg_success
        self._border_color.rgba = (0.14, 0.30, 0.20, 1)
        self.label.color = (0.76, 1.00, 0.82, 1)
        self._start_pulse(seconds=pulse_seconds)

    def set_warning(self, text: str):
        self._last_tone = "warning"
        self.set_text(text)
        self._hide_icon()
        self._bg_color.rgba = self._bg_warning
        self._border_color.rgba = (0.34, 0.24, 0.08, 1)
        self.label.color = (1.00, 0.92, 0.72, 1)

    def set_error(self, text: str):
        self._last_tone = "error"
        self.set_text(text)
        self._hide_icon()
        self._bg_color.rgba = self._bg_error
        self._border_color.rgba = (0.34, 0.14, 0.14, 1)
        self.label.color = (1, 0.78, 0.78, 1)


class SadeKodAlani(KodPaneli):
    def __init__(
        self,
        readonly=False,
        hint_text="",
        services: ServicesYoneticisi | None = None,
        hint_text_key: str = "",
        **kwargs,
    ):
        super().__init__(
            orientation="vertical",
            padding=dp(4),
            bg=INPUT_BG,
            border=(0.18, 0.24, 0.34, 1),
            **kwargs,
        )

        self.services = services or ServicesYoneticisi()
        self.hint_text_key = str(hint_text_key or "").strip()
        self._default_hint_text = str(hint_text or "")

        self.editor = KodEditoru(readonly=readonly, hint_text=hint_text)
        self.add_widget(self.editor)

    # =========================================================
    # DIL
    # =========================================================
    def _m(self, anahtar: str, default: str = "") -> str:
        try:
            return str(self.services.metin(anahtar, default) or default or anahtar)
        except Exception:
            return str(default or anahtar)

    def refresh_language(self) -> None:
        try:
            if self.hint_text_key:
                yeni_hint = self._m(self.hint_text_key, self._default_hint_text)
            else:
                yeni_hint = self._default_hint_text

            self.set_hint_text(yeni_hint)
        except Exception:
            pass

    # =========================================================
    # PUBLIC
    # =========================================================
    @property
    def text(self):
        return self.editor.text

    @text.setter
    def text(self, value):
        self.editor.text = str(value or "")
        self.editor.scroll_to_top()

    def set_hint_text(self, text: str) -> None:
        self._default_hint_text = str(text or "")
        try:
            self.editor.set_hint_text(self._default_hint_text)
        except Exception:
            try:
                self.editor.hint_text = self._default_hint_text
            except Exception:
                pass

    def scroll_to_top(self):
        self.editor.scroll_to_top()

    def set_error_line(self, line_no: int):
        self.editor.set_error_line(line_no)

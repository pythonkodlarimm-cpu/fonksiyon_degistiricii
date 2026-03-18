# -*- coding: utf-8 -*-
from __future__ import annotations

import time

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

from app.ui.icon_yardimci import icon_path


class _DokunmatikAksiyonBildirimi(ButtonBehavior, BoxLayout):
    def __init__(self, on_single_tap=None, on_double_tap=None, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(58),
            padding=(dp(12), dp(9)),
            spacing=dp(10),
            **kwargs,
        )

        self.on_single_tap = on_single_tap
        self.on_double_tap = on_double_tap
        self._last_tap_ts = 0.0
        self._pulse_anim = None
        self._hide_event = None

        self._bg_success = (0.08, 0.24, 0.14, 0.98)
        self._bg_info = (0.08, 0.13, 0.20, 0.98)
        self._bg_warning = (0.24, 0.18, 0.08, 0.98)
        self._bg_error = (0.24, 0.12, 0.12, 0.98)

        with self.canvas.before:
            self._bg_color = Color(*self._bg_success)
            self._bg_rect = RoundedRectangle(radius=[dp(14)])

        with self.canvas.after:
            self._border_color = Color(0.18, 0.40, 0.22, 1)
            self._border_line = Line(
                rounded_rectangle=(0, 0, 0, 0, dp(14)),
                width=1.2,
            )

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

        self.icon = Image(
            source="app/assets/icons/onaylandi.png",
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            opacity=1,
            allow_stretch=True,
            keep_ratio=True,
        )
        self.add_widget(self.icon)

        self.text_wrap = BoxLayout(
            orientation="vertical",
            spacing=dp(1),
        )

        self.title_label = Label(
            text="Güncelleme tamamlandı",
            color=(0.92, 1.0, 0.94, 1),
            font_size="14sp",
            bold=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(22),
            shorten=True,
            shorten_from="right",
        )
        self.title_label.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], size[1])))
        self.text_wrap.add_widget(self.title_label)

        self.body_label = Label(
            text="Yeni fonksiyon kaydedildi.",
            color=(0.84, 0.96, 0.88, 1),
            font_size="11sp",
            halign="left",
            valign="middle",
            shorten=True,
            shorten_from="right",
        )
        self.body_label.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))
        self.text_wrap.add_widget(self.body_label)

        self.add_widget(self.text_wrap)

        self.hint_label = Label(
            text="Dokun",
            color=(0.76, 0.96, 0.82, 0.92),
            font_size="11sp",
            halign="right",
            valign="middle",
            size_hint_x=None,
            width=dp(48),
        )
        self.hint_label.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        self.add_widget(self.hint_label)

        self.opacity = 0
        self.disabled = True

    def _update_canvas(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._border_line.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(14),
        )

    def _cancel_hide_event(self):
        try:
            if self._hide_event is not None:
                self._hide_event.cancel()
        except Exception:
            pass
        self._hide_event = None

    def _stop_pulse(self):
        try:
            if self._pulse_anim is not None:
                self._pulse_anim.cancel(self.icon)
        except Exception:
            pass
        self._pulse_anim = None

        try:
            self.icon.opacity = 1
            self.icon.size = (dp(24), dp(24))
        except Exception:
            pass

    def _start_pulse(self):
        self._stop_pulse()
        try:
            anim = (
                Animation(opacity=0.70, size=(dp(28), dp(28)), duration=0.42)
                + Animation(opacity=1.0, size=(dp(24), dp(24)), duration=0.42)
            )
            anim.repeat = True
            anim.start(self.icon)
            self._pulse_anim = anim
        except Exception:
            pass

    def _set_visual(self, tone: str, title: str, text: str, icon_name: str, tappable: bool):
        tone_key = str(tone or "success").strip().lower()

        if tone_key == "info":
            self._bg_color.rgba = self._bg_info
            self._border_color.rgba = (0.18, 0.28, 0.38, 1)
            title_color = (0.88, 0.94, 1, 1)
            body_color = (0.76, 0.84, 0.92, 1)
            hint_color = (0.72, 0.86, 1, 0.95)
        elif tone_key == "warning":
            self._bg_color.rgba = self._bg_warning
            self._border_color.rgba = (0.38, 0.28, 0.10, 1)
            title_color = (1.0, 0.94, 0.80, 1)
            body_color = (1.0, 0.88, 0.72, 1)
            hint_color = (1.0, 0.92, 0.72, 0.95)
        elif tone_key == "error":
            self._bg_color.rgba = self._bg_error
            self._border_color.rgba = (0.40, 0.18, 0.18, 1)
            title_color = (1.0, 0.86, 0.86, 1)
            body_color = (1.0, 0.78, 0.78, 1)
            hint_color = (1.0, 0.84, 0.84, 0.95)
        else:
            self._bg_color.rgba = self._bg_success
            self._border_color.rgba = (0.18, 0.40, 0.22, 1)
            title_color = (0.92, 1.0, 0.94, 1)
            body_color = (0.84, 0.96, 0.88, 1)
            hint_color = (0.76, 0.96, 0.82, 0.95)

        self.title_label.text = str(title or "").strip() or "Bildirim"
        self.title_label.color = title_color
        self.body_label.text = str(text or "").strip() or ""
        self.body_label.color = body_color
        self.hint_label.text = "Dokun" if tappable else ""
        self.hint_label.color = hint_color

        resolved = ""
        if icon_name:
            try:
                resolved = icon_path(icon_name)
            except Exception:
                resolved = ""

        if resolved:
            self.icon.source = resolved
            try:
                self.icon.reload()
            except Exception:
                pass

    def show(self, title: str, text: str, icon_name="onaylandi.png", tone="success", duration=4.0, tappable=False):
        self._cancel_hide_event()
        self._set_visual(
            tone=tone,
            title=title,
            text=text,
            icon_name=icon_name,
            tappable=tappable,
        )
        self.disabled = False
        self._start_pulse()

        try:
            Animation.cancel_all(self, "opacity")
        except Exception:
            pass

        try:
            self.opacity = 0
            Animation(opacity=1.0, duration=0.16).start(self)
        except Exception:
            self.opacity = 1.0

        self._hide_event = Clock.schedule_once(
            lambda *_: self.hide(),
            max(0.8, float(duration or 4.0)),
        )

    def hide(self):
        self._cancel_hide_event()

        def _finish(*_args):
            self._stop_pulse()
            self.opacity = 0
            self.disabled = True

        try:
            Animation.cancel_all(self, "opacity")
        except Exception:
            pass

        try:
            anim = Animation(opacity=0.0, duration=0.18)
            anim.bind(on_complete=lambda *_: _finish())
            anim.start(self)
        except Exception:
            _finish()

    def hide_immediately(self):
        self._cancel_hide_event()
        self._stop_pulse()
        try:
            Animation.cancel_all(self, "opacity")
        except Exception:
            pass
        self.opacity = 0
        self.disabled = True

    def on_press(self):
        now = time.time()
        fark = now - self._last_tap_ts
        self._last_tap_ts = now

        if fark <= 0.35:
            try:
                if self.on_double_tap is not None:
                    self.on_double_tap()
            except Exception:
                pass
            return

        Clock.schedule_once(self._dispatch_single_tap, 0.18)

    def _dispatch_single_tap(self, *_args):
        try:
            if self.on_single_tap is not None and not self.disabled and self.opacity > 0:
                self.on_single_tap()
        except Exception:
            pass


class EditorAksiyonBildirimi(BoxLayout):
    """Yeni kod alanına yakın konumlanan, detaylı ve tıklanabilir bildirim barı."""

    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(0),
            opacity=0,
            **kwargs,
        )

        self._on_tap = None
        self.notice = _DokunmatikAksiyonBildirimi(
            on_single_tap=self._handle_single_tap,
            on_double_tap=self._handle_double_tap,
        )
        self.add_widget(self.notice)

    def _handle_single_tap(self):
        try:
            if self._on_tap is not None:
                self._on_tap()
        except Exception:
            pass

    def _handle_double_tap(self):
        self.hide_immediately()

    def show(self, title: str, text: str, icon_name="onaylandi.png", tone="success", duration=4.0, on_tap=None):
        self._on_tap = on_tap
        self.height = dp(58)
        self.opacity = 1
        self.notice.show(
            title=title,
            text=text,
            icon_name=icon_name,
            tone=tone,
            duration=duration,
            tappable=bool(on_tap),
        )

    def hide(self):
        self.notice.hide()

        def _finish(*_args):
            self.height = dp(0)
            self.opacity = 0
            self._on_tap = None

        Clock.schedule_once(_finish, 0.22)

    def hide_immediately(self):
        self.notice.hide_immediately()
        self.height = dp(0)
        self.opacity = 0
        self._on_tap = None
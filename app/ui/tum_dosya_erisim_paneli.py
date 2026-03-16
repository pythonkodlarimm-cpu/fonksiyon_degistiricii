# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paneli.py

ROL:
- Android'de tüm dosya erişimi durumunu kullanıcıya göstermek
- Gerekirse kullanıcıyı ilgili ayar ekranına yönlendirmek
- Açık / kapalı durumu büyük ikon ile vurgulamak
- Kapalı durumda sürekli pulse ile dikkat çekmek
- Açık durumda kısa süre pulse gösterip sonra sakinleştirmek
- Aksiyon ikonu ile erişim açma / kapatma yönlendirmesi yapmak

MİMARİ:
- Kendi görünümünü kendi çizer
- Root sadece ekrana ekler
- Android özel izin servisi ile konuşur

SURUM: 3
TARIH: 2026-03-16
IMZA: FY.
"""

from __future__ import annotations

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color
from kivy.graphics import RoundedRectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.utils import platform

from app.ui.iconlu_baslik import IconluBaslik
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY


class TiklanabilirIcon(ButtonBehavior, Image):
    pass


class TumDosyaErisimPaneli(BoxLayout):
    def __init__(self, on_status_changed=None, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(198),
            spacing=dp(8),
            padding=(dp(8), dp(8), dp(8), dp(8)),
            **kwargs,
        )

        self.on_status_changed = on_status_changed

        self.header = None
        self.status_icon = None
        self.info_label = None
        self.action_open_icon = None
        self.action_close_icon = None

        self._pulse_anim = None
        self._stop_pulse_event = None
        self._last_status = None
        self._action_icon_visible_width = dp(84)

        self._build_ui()
        self.refresh_status()

    # ---------------------------------------------------------
    # debug
    # ---------------------------------------------------------
    def _debug(self, message: str) -> None:
        try:
            print("[TUM_DOSYA_ERISIM]", str(message))
        except Exception:
            pass

    # ---------------------------------------------------------
    # ui
    # ---------------------------------------------------------
    def _build_ui(self) -> None:
        with self.canvas.before:
            self._bg_color = Color(0.10, 0.13, 0.18, 1)
            self._bg_rect = RoundedRectangle(radius=[dp(14)])

        self.bind(pos=self._update_canvas, size=self._update_canvas)

        self.header = IconluBaslik(
            text="Tüm Dosya Erişimi",
            icon_name="folder_open.png",
            height_dp=30,
            font_size="15sp",
            color=TEXT_PRIMARY,
        )
        self.add_widget(self.header)

        status_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(86),
            spacing=dp(8),
        )

        left_spacer = Label(size_hint_x=1)
        right_spacer = Label(size_hint_x=1)

        self.status_icon = TiklanabilirIcon(
            source="app/assets/icons/erisim_kapali.png",
            size_hint=(None, None),
            size=(dp(70), dp(70)),
            allow_stretch=True,
            keep_ratio=True,
            opacity=1,
        )
        self.status_icon.bind(on_release=self._handle_status_icon_click)

        status_row.add_widget(left_spacer)
        status_row.add_widget(self.status_icon)
        status_row.add_widget(right_spacer)
        self.add_widget(status_row)

        self.info_label = Label(
            text="Durum kontrol ediliyor...",
            size_hint_y=None,
            height=dp(30),
            color=TEXT_MUTED,
            font_size="12sp",
            halign="center",
            valign="middle",
        )
        self.info_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
        self.add_widget(self.info_label)

        action_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            spacing=dp(10),
        )

        self.action_open_icon = TiklanabilirIcon(
            source="app/assets/icons/erisimi_ac_aksiyon.png",
            size_hint=(None, None),
            size=(dp(44), dp(44)),
            allow_stretch=True,
            keep_ratio=True,
            opacity=1,
        )
        self.action_open_icon.bind(on_release=self._handle_open_action)

        self.action_close_icon = TiklanabilirIcon(
            source="app/assets/icons/erisimi_kapat_aksiyon.png",
            size_hint=(None, None),
            size=(dp(44), dp(44)),
            allow_stretch=True,
            keep_ratio=True,
            opacity=1,
        )
        self.action_close_icon.bind(on_release=self._handle_close_action)

        self._action_open_wrap = BoxLayout(
            orientation="horizontal",
            size_hint=(None, None),
            size=(self._action_icon_visible_width, dp(48)),
        )
        self._action_open_wrap.add_widget(Label(size_hint_x=1))
        self._action_open_wrap.add_widget(self.action_open_icon)
        self._action_open_wrap.add_widget(Label(size_hint_x=1))

        self._action_close_wrap = BoxLayout(
            orientation="horizontal",
            size_hint=(None, None),
            size=(self._action_icon_visible_width, dp(48)),
        )
        self._action_close_wrap.add_widget(Label(size_hint_x=1))
        self._action_close_wrap.add_widget(self.action_close_icon)
        self._action_close_wrap.add_widget(Label(size_hint_x=1))

        action_row.add_widget(Label(size_hint_x=1))
        action_row.add_widget(self._action_open_wrap)
        action_row.add_widget(self._action_close_wrap)
        action_row.add_widget(Label(size_hint_x=1))

        self.add_widget(action_row)
        self._update_canvas()

    def _update_canvas(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    # ---------------------------------------------------------
    # pulse
    # ---------------------------------------------------------
    def _cancel_stop_event(self):
        try:
            if self._stop_pulse_event is not None:
                self._stop_pulse_event.cancel()
        except Exception:
            pass
        self._stop_pulse_event = None

    def _stop_pulse(self):
        self._cancel_stop_event()

        try:
            if self._pulse_anim is not None:
                self._pulse_anim.cancel(self.status_icon)
        except Exception:
            pass

        self._pulse_anim = None

        try:
            self.status_icon.opacity = 1
            self.status_icon.size = (dp(70), dp(70))
        except Exception:
            pass

    def _start_pulse_forever(self):
        self._stop_pulse()
        try:
            self.status_icon.opacity = 1
            self.status_icon.size = (dp(70), dp(70))
            anim = (
                Animation(opacity=0.70, size=(dp(82), dp(82)), duration=0.55)
                + Animation(opacity=1.00, size=(dp(70), dp(70)), duration=0.55)
            )
            anim.repeat = True
            anim.start(self.status_icon)
            self._pulse_anim = anim
        except Exception:
            pass

    def _start_pulse_for_seconds(self, seconds: float):
        self._stop_pulse()
        try:
            self.status_icon.opacity = 1
            self.status_icon.size = (dp(70), dp(70))
            anim = (
                Animation(opacity=0.78, size=(dp(80), dp(80)), duration=0.50)
                + Animation(opacity=1.00, size=(dp(70), dp(70)), duration=0.50)
            )
            anim.repeat = True
            anim.start(self.status_icon)
            self._pulse_anim = anim
            self._stop_pulse_event = Clock.schedule_once(
                lambda *_: self._stop_pulse(),
                max(0.1, float(seconds)),
            )
        except Exception:
            pass

    # ---------------------------------------------------------
    # visibility helpers
    # ---------------------------------------------------------
    def _set_wrap_visible(self, wrap, visible: bool) -> None:
        if wrap is None:
            return

        try:
            wrap.opacity = 1 if visible else 0
        except Exception:
            pass

        try:
            wrap.size_hint_x = None
        except Exception:
            pass

        try:
            wrap.width = self._action_icon_visible_width if visible else 0.01
        except Exception:
            pass

        try:
            wrap.disabled = not visible
        except Exception:
            pass

    def _show_open_action(self):
        self._set_wrap_visible(self._action_open_wrap, True)
        self._set_wrap_visible(self._action_close_wrap, False)

    def _show_close_action(self):
        self._set_wrap_visible(self._action_open_wrap, False)
        self._set_wrap_visible(self._action_close_wrap, True)

    # ---------------------------------------------------------
    # state ui
    # ---------------------------------------------------------
    def _set_info(self, text: str) -> None:
        self.info_label.text = str(text or "")

    def _apply_closed_state(self):
        try:
            self.status_icon.source = "app/assets/icons/erisim_kapali.png"
        except Exception:
            pass

        self._bg_color.rgba = (0.20, 0.12, 0.12, 1)
        self.info_label.color = (1.0, 0.78, 0.78, 1)
        self._show_open_action()
        self._start_pulse_forever()

    def _apply_open_state(self):
        try:
            self.status_icon.source = "app/assets/icons/erisim_acik.png"
        except Exception:
            pass

        self._bg_color.rgba = (0.08, 0.22, 0.14, 1)
        self.info_label.color = (0.78, 1.0, 0.84, 1)
        self._show_close_action()
        self._start_pulse_for_seconds(10.0)

    def _apply_non_android_state(self):
        try:
            self.status_icon.source = "app/assets/icons/erisim_kapali.png"
        except Exception:
            pass

        self._bg_color.rgba = (0.10, 0.13, 0.18, 1)
        self.info_label.color = TEXT_MUTED
        self._show_open_action()
        self._stop_pulse()

    # ---------------------------------------------------------
    # service actions
    # ---------------------------------------------------------
    def _open_settings(self) -> None:
        if platform != "android":
            self._set_info("Bu ayar yalnızca Android'de kullanılabilir.")
            return

        try:
            from app.services.android_ozel_izin_servisi import (
                tum_dosya_erisim_ayarlari_ac,
            )

            tum_dosya_erisim_ayarlari_ac()
            self._set_info(
                "Ayar ekranı açıldı. İzin değişikliğinden sonra geri dön."
            )
        except Exception as exc:
            self._set_info(f"Ayar ekranı açılamadı: {exc}")
            self._debug(f"Ayar ekranı açılamadı: {exc}")

    # ---------------------------------------------------------
    # public refresh
    # ---------------------------------------------------------
    def refresh_status(self) -> None:
        if platform != "android":
            self._last_status = False
            self._apply_non_android_state()
            self._set_info("Android dışında tüm dosya erişimi kullanılmaz.")
            return

        try:
            from app.services.android_ozel_izin_servisi import (
                tum_dosya_erisim_izni_var_mi,
            )

            durum = bool(tum_dosya_erisim_izni_var_mi())
            onceki = self._last_status
            self._last_status = durum

            if durum:
                self._apply_open_state()
                self._set_info("Tüm dosya erişimi açık.")
            else:
                self._apply_closed_state()
                self._set_info("Tüm dosya erişimi kapalı. Açmak için ikona bas.")

            if self.on_status_changed:
                self.on_status_changed(durum)

            self._debug(f"Tüm dosya erişimi durumu: {durum} | önceki: {onceki}")

        except Exception as exc:
            self._last_status = False
            self._apply_closed_state()
            self._set_info(f"İzin durumu okunamadı: {exc}")
            self._debug(f"İzin durumu okunamadı: {exc}")

    # ---------------------------------------------------------
    # click handlers
    # ---------------------------------------------------------
    def _handle_status_icon_click(self, *_args) -> None:
        self._open_settings()

    def _handle_open_action(self, *_args) -> None:
        self._open_settings()

    def _handle_close_action(self, *_args) -> None:
        self._open_settings()

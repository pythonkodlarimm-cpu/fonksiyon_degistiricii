# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paneli.py

ROL:
- Ana ekranda sadece menu.png gösterir
- Menüye basınca erişim popup açar
- Açık/Kapalı duruma göre ikon + yönlendirme gösterir
- Menü ve aksiyon ikonlarında glow/pulse animasyon uygular
- Popup içinde rengarenk animasyonlu separator gösterir
- Aksiyon alanında büyük, ortalanmış ve tıklanabilir setting_on / setting_off ikonu kullanır

API 34 UYUMLULUK NOTU:
- Android izin kontrolü lazy import ile yapılır
- Android değilse kontrollü fallback uygulanır
- Popup akışı sade tutulur, ana ekranda sadece menu.png görünür

SURUM: 18
TARIH: 2026-03-17
IMZA: FY.
"""

from __future__ import annotations

import math

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.utils import platform

from app.ui.kart import Kart
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY


class TiklanabilirIcon(ButtonBehavior, Image):
    pass


class AnimatedSeparator(BoxLayout):
    """
    Popup içinde kullanılan renkli animasyonlu çizgi.
    """

    def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(6),
            **kwargs,
        )

        self._phase = 0.0
        self._segment_count = 7
        self._segment_colors = []
        self._segment_rects = []
        self._anim_event = None

        with self.canvas.before:
            for _ in range(self._segment_count):
                color = Color(1, 1, 1, 1)
                rect = RoundedRectangle(radius=[dp(4)])
                self._segment_colors.append(color)
                self._segment_rects.append(rect)

        self.bind(pos=self._update_graphics, size=self._update_graphics)
        self._update_graphics()
        self._start_animation()

    def _update_graphics(self, *_args):
        if self._segment_count <= 0:
            return

        bosluk = dp(3)
        toplam_bosluk = bosluk * (self._segment_count - 1)
        parca_genislik = max(1.0, (self.width - toplam_bosluk) / self._segment_count)

        x = self.x
        for rect in self._segment_rects:
            rect.pos = (x, self.y)
            rect.size = (parca_genislik, self.height)
            x += parca_genislik + bosluk

    def _animate(self, dt):
        self._phase += dt * 3.2

        for i, color in enumerate(self._segment_colors):
            p = self._phase + (i * 0.55)

            r = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(p + 0.0))
            g = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(p + 2.1))
            b = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(p + 4.2))

            color.rgba = (r, g, b, 1)

    def _start_animation(self):
        self._stop_animation()
        self._anim_event = Clock.schedule_interval(self._animate, 1 / 24)

    def _stop_animation(self):
        try:
            if self._anim_event is not None:
                self._anim_event.cancel()
        except Exception:
            pass
        self._anim_event = None

    def on_parent(self, _instance, parent):
        if parent is None:
            self._stop_animation()
        elif self._anim_event is None:
            self._start_animation()


class TumDosyaErisimPaneli(Kart):
    def __init__(self, on_status_changed=None, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            padding=(dp(10), dp(10)),
            bg=(0.08, 0.11, 0.16, 1),
            border=(0.18, 0.21, 0.27, 1),
            radius=12,
            **kwargs,
        )

        self.on_status_changed = on_status_changed

        self.menu_icon = None
        self._last_status = None

        self._menu_anim = None
        self._popup_action_anim = None

        self._current_popup = None
        self._current_popup_action_icon = None

        self._build_ui()
        self.refresh_status()
        self._start_menu_glow()

    # =========================================================
    # DEBUG
    # =========================================================
    def _debug(self, message: str) -> None:
        try:
            print("[TUM_DOSYA_ERISIM]", str(message))
        except Exception:
            pass

    # =========================================================
    # UI
    # =========================================================
    def _build_ui(self):
        self.menu_icon = TiklanabilirIcon(
            source="app/assets/icons/menu.png",
            size_hint=(None, None),
            size=(dp(36), dp(36)),
            opacity=1,
            allow_stretch=True,
            keep_ratio=True,
        )
        self.menu_icon.bind(on_release=self._open_menu)
        self.add_widget(self.menu_icon)

    # =========================================================
    # DURUM
    # =========================================================
    def refresh_status(self):
        onceki = self._last_status

        if platform != "android":
            self._last_status = False
        else:
            try:
                from app.services.android_ozel_izin_servisi import (
                    tum_dosya_erisim_izni_var_mi,
                )

                self._last_status = bool(tum_dosya_erisim_izni_var_mi())
            except Exception as exc:
                self._last_status = None
                self._debug(f"Durum okuma hatası: {exc}")

        try:
            if self.on_status_changed and onceki != self._last_status:
                self.on_status_changed(bool(self._last_status))
        except Exception:
            pass

    # =========================================================
    # ANIMATIONS
    # =========================================================
    def _stop_menu_glow(self) -> None:
        try:
            if self._menu_anim is not None and self.menu_icon is not None:
                self._menu_anim.cancel(self.menu_icon)
        except Exception:
            pass

        self._menu_anim = None

        try:
            if self.menu_icon is not None:
                self.menu_icon.opacity = 1
                self.menu_icon.size = (dp(36), dp(36))
        except Exception:
            pass

    def _start_menu_glow(self) -> None:
        self._stop_menu_glow()
        try:
            anim = (
                Animation(opacity=0.72, size=(dp(40), dp(40)), duration=0.60)
                + Animation(opacity=1.0, size=(dp(36), dp(36)), duration=0.60)
            )
            anim.repeat = True
            anim.start(self.menu_icon)
            self._menu_anim = anim
        except Exception:
            pass

    def _stop_popup_action_glow(self) -> None:
        try:
            if (
                self._popup_action_anim is not None
                and self._current_popup_action_icon is not None
            ):
                self._popup_action_anim.cancel(self._current_popup_action_icon)
        except Exception:
            pass

        self._popup_action_anim = None

        try:
            if self._current_popup_action_icon is not None:
                self._current_popup_action_icon.opacity = 1
                self._current_popup_action_icon.size = (dp(88), dp(88))
        except Exception:
            pass

    def _start_popup_action_glow(self) -> None:
        self._stop_popup_action_glow()

        try:
            if self._current_popup_action_icon is None:
                return

            anim = (
                Animation(opacity=0.74, size=(dp(96), dp(96)), duration=0.55)
                + Animation(opacity=1.0, size=(dp(88), dp(88)), duration=0.55)
            )
            anim.repeat = True
            anim.start(self._current_popup_action_icon)
            self._popup_action_anim = anim
        except Exception:
            pass

    # =========================================================
    # POPUP
    # =========================================================
    def _open_menu(self, *_args):
        self.refresh_status()

        if self._last_status is True:
            durum_text = "Tüm Dosya Erişimi Açık"
            action_icon = "app/assets/icons/setting_on.png"
            durum_color = (0.26, 1.0, 0.42, 1)
            action_desc = "Erişimi kapatmak için aşağıdaki simgeye dokunun."
        elif self._last_status is False:
            durum_text = "Tüm Dosya Erişimi Kapalı"
            action_icon = "app/assets/icons/setting_off.png"
            durum_color = (1.0, 0.38, 0.38, 1)
            action_desc = "Erişimi açmak için aşağıdaki simgeye dokunun."
        else:
            durum_text = "Durum Bilinmiyor"
            action_icon = "app/assets/icons/warning.png"
            durum_color = (1.0, 0.82, 0.36, 1)
            action_desc = "Durum okunamadı. Aşağıdaki simge ile ayar ekranını açabilirsiniz."

        content = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
        )

        title = Label(
            text="Erişim İşlemleri",
            color=TEXT_PRIMARY,
            font_size="19sp",
            bold=True,
            size_hint_y=None,
            height=dp(30),
            halign="center",
            valign="middle",
        )
        title.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        content.add_widget(title)

        durum = Label(
            text=durum_text,
            color=durum_color,
            font_size="17sp",
            bold=True,
            size_hint_y=None,
            height=dp(28),
            halign="center",
            valign="middle",
        )
        durum.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        content.add_widget(durum)

        separator = AnimatedSeparator()
        content.add_widget(separator)

        action_wrap = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(162),
            spacing=dp(10),
        )

        self._current_popup_action_icon = TiklanabilirIcon(
            source=action_icon,
            size_hint=(None, None),
            size=(dp(88), dp(88)),
            opacity=1,
            allow_stretch=True,
            keep_ratio=True,
        )

        icon_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(102),
        )
        icon_row.add_widget(Label(size_hint_x=1))
        icon_row.add_widget(self._current_popup_action_icon)
        icon_row.add_widget(Label(size_hint_x=1))

        desc_label = Label(
            text=action_desc,
            color=TEXT_PRIMARY,
            font_size="14sp",
            size_hint_y=None,
            height=dp(44),
            halign="center",
            valign="middle",
        )
        desc_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )

        action_wrap.add_widget(icon_row)
        action_wrap.add_widget(desc_label)

        content.add_widget(action_wrap)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.90, None),
            height=dp(318),
            auto_dismiss=True,
            separator_height=0,
        )
        self._current_popup = popup

        self._current_popup_action_icon.bind(
            on_release=lambda *_: self._handle_action(popup)
        )
        popup.bind(on_open=lambda *_: self._start_popup_action_glow())
        popup.bind(on_dismiss=lambda *_: self._on_popup_dismiss())

        popup.open()

    def _on_popup_dismiss(self) -> None:
        self._stop_popup_action_glow()
        self._current_popup = None
        self._current_popup_action_icon = None

    # =========================================================
    # ACTION
    # =========================================================
    def _handle_action(self, popup):
        if platform == "android":
            try:
                from app.services.android_ozel_izin_servisi import (
                    tum_dosya_erisim_ayarlari_ac,
                )

                tum_dosya_erisim_ayarlari_ac()
            except Exception as exc:
                self._debug(f"Ayar açma hatası: {exc}")
        else:
            self._debug("Android dışı ortamda ayar ekranı açılamaz.")

        try:
            popup.dismiss()
        except Exception:
            pass

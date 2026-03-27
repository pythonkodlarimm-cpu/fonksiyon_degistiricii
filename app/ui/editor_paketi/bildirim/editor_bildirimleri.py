# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/bildirim/editor_bildirimleri.py

ROL:
- Editör paneline yakın konumlanan geçici aksiyon bildirimlerini göstermek
- Tek dokunma / çift dokunma davranışını yönetmek
- Başarı, bilgi, uyarı ve hata tonlarında görsel geri bildirim sağlamak
- Hata durumunda detaylı, kopyalanabilir popup gösterebilmek
- Aktif dile göre görünür metinleri üretmek ve yenilemek
- Yapıştırma gibi editör aksiyonlarında tekrar kullanılabilir bildirim katmanı sunmak

MİMARİ:
- Bildirim alt paketinin iç görsel bileşenini içerir
- Üst katman bu modüle doğrudan değil, bildirim/yoneticisi.py üzerinden erişmelidir
- Editör içi inline bildirim davranışını UI tarafında izole eder
- Kullanıcıya görünen metinler services üzerinden alınabilir
- Dil yenilemede aktif başlık, ipucu ve popup metinleri güvenli şekilde güncellenir

SURUM: 6
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations

import time

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

from app.services.yoneticisi import ServicesYoneticisi
from app.ui.icon_yardimci import icon_path


class _DokunmatikAksiyonBildirimi(ButtonBehavior, BoxLayout):
    def __init__(
        self,
        on_single_tap=None,
        on_double_tap=None,
        services: ServicesYoneticisi | None = None,
        **kwargs,
    ):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(58),
            padding=(dp(12), dp(9)),
            spacing=dp(10),
            **kwargs,
        )

        self.services = services or ServicesYoneticisi()

        self.on_single_tap = on_single_tap
        self.on_double_tap = on_double_tap
        self._last_tap_ts = 0.0

        self._pulse_anim = None
        self._hide_event = None

        self._last_title_key = ""
        self._last_title_default = ""
        self._last_body_key = ""
        self._last_body_default = ""
        self._last_title_text = ""
        self._last_body_text = ""
        self._last_tappable = False

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
            text=self._m("notification", "Bildirim"),
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
        self.title_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], size[1]))
        )
        self.text_wrap.add_widget(self.title_label)

        self.body_label = Label(
            text="",
            color=(0.84, 0.96, 0.88, 1),
            font_size="11sp",
            halign="left",
            valign="middle",
            shorten=True,
            shorten_from="right",
        )
        self.body_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
        self.text_wrap.add_widget(self.body_label)

        self.add_widget(self.text_wrap)

        self.hint_label = Label(
            text="",
            color=(0.76, 0.96, 0.82, 0.92),
            font_size="11sp",
            halign="right",
            valign="middle",
            size_hint_x=None,
            width=dp(60),
        )
        self.hint_label.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        self.add_widget(self.hint_label)

        self.opacity = 0
        self.disabled = True

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
            if self._last_title_key:
                self.title_label.text = self._m(
                    self._last_title_key,
                    self._last_title_default or self._last_title_text,
                )
        except Exception:
            pass

        try:
            if self._last_body_key:
                self.body_label.text = self._m(
                    self._last_body_key,
                    self._last_body_default or self._last_body_text,
                )
        except Exception:
            pass

        try:
            self.hint_label.text = self._m("tap", "Dokun") if self._last_tappable else ""
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

    def _resolve_localized_text(
        self,
        direct_text: str,
        text_key: str = "",
        default_text: str = "",
    ) -> str:
        temiz_key = str(text_key or "").strip()
        if temiz_key:
            return self._m(temiz_key, default_text or direct_text or "")
        return str(direct_text or default_text or "")

    def _set_visual(
        self,
        tone: str,
        title: str,
        text: str,
        icon_name: str,
        tappable: bool,
        title_key: str = "",
        title_default: str = "",
        text_key: str = "",
        text_default: str = "",
    ):
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

        final_title = self._resolve_localized_text(
            direct_text=title,
            text_key=title_key,
            default_text=title_default or self._m("notification", "Bildirim"),
        ).strip() or self._m("notification", "Bildirim")

        final_body = self._resolve_localized_text(
            direct_text=text,
            text_key=text_key,
            default_text=text_default or "",
        ).strip()

        self._last_title_key = str(title_key or "").strip()
        self._last_title_default = str(title_default or "").strip()
        self._last_body_key = str(text_key or "").strip()
        self._last_body_default = str(text_default or "").strip()
        self._last_title_text = final_title
        self._last_body_text = final_body
        self._last_tappable = bool(tappable)

        self.title_label.text = final_title
        self.title_label.color = title_color
        self.body_label.text = final_body
        self.body_label.color = body_color
        self.hint_label.text = self._m("tap", "Dokun") if tappable else ""
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

    # =========================================================
    # PUBLIC
    # =========================================================
    def show(
        self,
        title: str,
        text: str,
        icon_name="onaylandi.png",
        tone="success",
        duration=4.0,
        tappable=False,
        title_key: str = "",
        title_default: str = "",
        text_key: str = "",
        text_default: str = "",
    ):
        self._cancel_hide_event()
        self._set_visual(
            tone=tone,
            title=title,
            text=text,
            icon_name=icon_name,
            tappable=tappable,
            title_key=title_key,
            title_default=title_default,
            text_key=text_key,
            text_default=text_default,
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
    """
    Yeni kod alanına yakın konumlanan, detaylı ve tıklanabilir bildirim barı.
    """

    def __init__(
        self,
        services: ServicesYoneticisi | None = None,
        **kwargs,
    ):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(0),
            opacity=0,
            **kwargs,
        )

        self.services = services or ServicesYoneticisi()

        self._on_tap = None
        self._popup_ref = None
        self._detailed_error_text = ""

        self._popup_title = self._m("error_title", "Hata Detayı")
        self._popup_title_key = "error_title"
        self._popup_title_default = "Hata Detayı"

        self.notice = _DokunmatikAksiyonBildirimi(
            on_single_tap=self._handle_single_tap,
            on_double_tap=self._handle_double_tap,
            services=self.services,
        )
        self.add_widget(self.notice)

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
            self.notice.refresh_language()
        except Exception:
            pass

        try:
            if self._popup_title_key:
                self._popup_title = self._m(
                    self._popup_title_key,
                    self._popup_title_default or "Hata Detayı",
                )
        except Exception:
            pass

    # =========================================================
    # INTERNAL
    # =========================================================
    def _handle_single_tap(self):
        try:
            if self._has_detailed_error():
                self._show_detailed_error_popup()
                return

            if self._on_tap is not None:
                self._on_tap()
        except Exception:
            pass

    def _handle_double_tap(self):
        self.hide_immediately()

    def _set_detailed_error(
        self,
        text: str,
        title: str = "",
        title_key: str = "",
        title_default: str = "",
    ) -> None:
        self._detailed_error_text = str(text or "").strip()
        self._popup_title_key = str(title_key or "").strip() or "error_title"
        self._popup_title_default = str(title_default or "").strip() or "Hata Detayı"
        self._popup_title = (
            str(title or "").strip()
            or self._m(self._popup_title_key, self._popup_title_default)
        )

    def _clear_detailed_error(self) -> None:
        self._detailed_error_text = ""
        self._popup_title_key = "error_title"
        self._popup_title_default = "Hata Detayı"
        self._popup_title = self._m("error_title", "Hata Detayı")

    def _has_detailed_error(self) -> bool:
        return bool(str(self._detailed_error_text or "").strip())

    def _show_detailed_error_popup(self):
        if not self._has_detailed_error():
            return

        popup = None
        try:
            content = BoxLayout(
                orientation="vertical",
                spacing=dp(10),
                padding=(dp(12), dp(12), dp(12), dp(12)),
            )

            baslik = Label(
                text=str(self._popup_title or self._m("error_title", "Hata Detayı")),
                size_hint_y=None,
                height=dp(30),
                font_size="18sp",
                bold=True,
                color=(1.0, 0.42, 0.42, 1),
                halign="center",
                valign="middle",
            )
            baslik.bind(size=lambda inst, size: setattr(inst, "text_size", size))
            content.add_widget(baslik)

            alt = Label(
                text=self._m(
                    "error_copy_hint",
                    "Dosya yolu, fonksiyon, satır ve traceback metni kopyalanabilir.",
                ),
                size_hint_y=None,
                height=dp(20),
                font_size="11sp",
                color=(0.86, 0.86, 0.90, 1),
                halign="center",
                valign="middle",
            )
            alt.bind(size=lambda inst, size: setattr(inst, "text_size", size))
            content.add_widget(alt)

            scroll = ScrollView(
                do_scroll_x=True,
                do_scroll_y=True,
                bar_width=dp(8),
            )

            detay = Label(
                text=str(self._detailed_error_text or ""),
                halign="left",
                valign="top",
                size_hint_y=None,
                font_size="12sp",
                color=(0.96, 0.96, 0.98, 1),
            )
            detay.bind(
                texture_size=lambda inst, val: setattr(
                    inst,
                    "height",
                    max(dp(180), val[1]),
                )
            )
            detay.bind(
                size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
            )

            scroll.add_widget(detay)
            content.add_widget(scroll)

            button_row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(46),
                spacing=dp(8),
            )

            copy_btn = Button(
                text=self._m("copy", "Kopyala"),
                background_normal="",
                background_down="",
                background_color=(0.18, 0.42, 0.72, 1),
                color=(1, 1, 1, 1),
            )

            close_btn = Button(
                text=self._m("close", "Kapat"),
                background_normal="",
                background_down="",
                background_color=(0.24, 0.24, 0.28, 1),
                color=(1, 1, 1, 1),
            )

            def _copy(*_args):
                try:
                    Clipboard.copy(str(self._detailed_error_text or ""))
                except Exception:
                    pass

            copy_btn.bind(on_release=_copy)
            button_row.add_widget(copy_btn)
            button_row.add_widget(close_btn)
            content.add_widget(button_row)

            popup = Popup(
                title="",
                content=content,
                size_hint=(0.94, 0.84),
                auto_dismiss=True,
                separator_height=0,
            )

            self._popup_ref = popup
            close_btn.bind(on_release=lambda *_: popup.dismiss())
            popup.open()

        except Exception:
            try:
                if popup is not None:
                    popup.dismiss()
            except Exception:
                pass
            self._popup_ref = None

    # =========================================================
    # PUBLIC
    # =========================================================
    def show(
        self,
        title: str,
        text: str,
        icon_name="onaylandi.png",
        tone="success",
        duration=4.0,
        on_tap=None,
        title_key: str = "",
        title_default: str = "",
        text_key: str = "",
        text_default: str = "",
    ):
        self._on_tap = on_tap
        self.height = dp(58)
        self.opacity = 1

        temiz_tone = str(tone or "success").strip().lower()

        if temiz_tone == "error":
            self._set_detailed_error(
                text=str(text or ""),
                title=str(title or ""),
                title_key=title_key or "error_title",
                title_default=title_default or "Hata Detayı",
            )
        else:
            self._clear_detailed_error()

        self.notice.show(
            title=title,
            text=text,
            icon_name=icon_name,
            tone=tone,
            duration=duration,
            tappable=bool(on_tap) or self._has_detailed_error(),
            title_key=title_key,
            title_default=title_default,
            text_key=text_key,
            text_default=text_default,
        )

    def hide(self):
        self.notice.hide()

        def _finish(*_args):
            self.height = dp(0)
            self.opacity = 0
            self._on_tap = None
            self._clear_detailed_error()

        Clock.schedule_once(_finish, 0.22)

    def hide_immediately(self):
        self.notice.hide_immediately()
        self.height = dp(0)
        self.opacity = 0
        self._on_tap = None
        self._clear_detailed_error()

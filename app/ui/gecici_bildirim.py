# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/gecici_bildirim.py

ROL:
- Ekran üzerinde geçici bildirim gösterir
- İkon + başlık + açıklama metni taşır
- Otomatik kapanır
- Tek dokunma ile aksiyon çalıştırabilir
- Çift dokunma ile hemen kapanır
- Konuma göre gösterilebilir (alt, orta, üst)
- Hata durumunda kopyalanabilir detay popup gösterebilir
- Seçilen dilde kullanıcıya metin gösterebilir

MİMARİ:
- Sadece görünüm ve animasyon içerir
- İş mantığı servis dışından tetiklenir
- Root içine overlay olarak eklenir
- Konum ve aksiyon parametreyle dışarıdan yönetilir
- Hata popup akışı aynı katman içinde güvenli fallback ile çalışır
- Sabit metinler ServicesYoneticisi -> dil servisi üzerinden çözülebilir

API UYUMLULUK:
- Doğrudan Android API çağrısı yapmaz
- Kivy tabanlıdır
- Android API 35 ile güvenli kullanılabilir
- APK / AAB davranış farkını azaltmak için animasyon ve ikon fallback mantığı korunur

SURUM: 7
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

import time

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
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
from app.ui.kart import Kart
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY


class _DokunmatikBildirim(ButtonBehavior, Kart):
    def __init__(self, on_double_tap=None, on_single_tap=None, **kwargs):
        super().__init__(
            orientation="horizontal",
            spacing=dp(10),
            padding=(dp(12), dp(10), dp(12), dp(10)),
            size_hint=(None, None),
            size=(dp(340), dp(74)),
            bg=(0.08, 0.11, 0.16, 0.98),
            border=(0.22, 0.26, 0.33, 1),
            radius=16,
            **kwargs,
        )

        self.on_double_tap = on_double_tap
        self.on_single_tap = on_single_tap
        self._last_tap_ts = 0.0
        self._tap_sequence = 0

        self.icon = Image(
            source="",
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            opacity=0,
            allow_stretch=True,
            keep_ratio=True,
        )
        self.add_widget(self.icon)

        self.text_wrap = BoxLayout(
            orientation="vertical",
            spacing=dp(2),
        )

        self.title_label = Label(
            text="",
            color=TEXT_PRIMARY,
            halign="left",
            valign="middle",
            font_size="14sp",
            bold=True,
            size_hint_y=None,
            height=dp(22),
            shorten=True,
            shorten_from="right",
        )
        self.title_label.bind(size=self._sync_title_size)
        self.text_wrap.add_widget(self.title_label)

        self.body_label = Label(
            text="",
            color=TEXT_MUTED if TEXT_MUTED else TEXT_PRIMARY,
            halign="left",
            valign="top",
            font_size="12sp",
            shorten=True,
            shorten_from="right",
        )
        self.body_label.bind(size=self._sync_body_size)
        self.text_wrap.add_widget(self.body_label)

        self.add_widget(self.text_wrap)

    def _sync_title_size(self, widget, size):
        widget.text_size = (size[0], size[1])

    def _sync_body_size(self, widget, size):
        widget.text_size = (size[0], None)

    def set_message(
        self,
        text: str,
        icon_name: str = "",
        title: str = "",
    ) -> None:
        temiz_title = str(title or "").strip()
        temiz_text = str(text or "").strip()

        if temiz_title:
            self.title_label.text = temiz_title
            self.title_label.opacity = 1
            self.title_label.height = dp(22)
        else:
            self.title_label.text = ""
            self.title_label.opacity = 0
            self.title_label.height = dp(0)

        self.body_label.text = temiz_text

        if icon_name:
            try:
                p = icon_path(icon_name)
            except Exception:
                p = ""

            if p:
                try:
                    self.icon.source = p
                    self.icon.opacity = 1
                    self.icon.reload()
                except Exception:
                    try:
                        self.icon.source = p
                        self.icon.opacity = 1
                    except Exception:
                        pass
                return

        try:
            self.icon.source = ""
            self.icon.opacity = 0
        except Exception:
            pass

    def on_press(self):
        now = time.time()
        fark = now - self._last_tap_ts
        self._last_tap_ts = now
        self._tap_sequence += 1
        aktif_tap = self._tap_sequence

        if fark <= 0.35:
            self._tap_sequence += 1
            try:
                if self.on_double_tap is not None:
                    self.on_double_tap()
            except Exception:
                pass
            return

        Clock.schedule_once(
            lambda *_: self._dispatch_single_tap(aktif_tap),
            0.20,
        )

    def _dispatch_single_tap(self, tap_sequence, *_args):
        try:
            if tap_sequence != self._tap_sequence:
                return

            if self.on_single_tap is not None:
                self.on_single_tap()
        except Exception:
            pass


class GeciciBildirimKatmani(BoxLayout):
    """
    Konum destekli overlay bildirim katmanı.

    position değerleri:
    - "bottom"
    - "center"
    - "top"

    Hata akışı:
    - icon_name == "error" veya "warning_error" veya "hata" ise
      toast yerine detaylı popup açılır
    """

    def __init__(self, services: ServicesYoneticisi | None = None, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint=(1, 1),
            padding=(dp(10), dp(10), dp(10), dp(10)),
            **kwargs,
        )

        self.services = services or ServicesYoneticisi()

        self._hide_event = None
        self._current_anim = None
        self._current_on_tap = None
        self._current_position = "bottom"

        self.top_anchor = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(92),
        )
        self.add_widget(self.top_anchor)

        self.center_anchor = BoxLayout(
            orientation="horizontal",
            size_hint=(1, 1),
        )
        self.add_widget(self.center_anchor)

        self.bottom_anchor = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(92),
        )
        self.add_widget(self.bottom_anchor)

        self.toast = _DokunmatikBildirim(
            on_double_tap=self.hide_immediately,
            on_single_tap=self._handle_single_tap,
        )
        self.toast.opacity = 0
        self.toast.disabled = True

        self._rebuild_anchor("bottom")

    # =========================================================
    # LANGUAGE
    # =========================================================
    def _m(self, anahtar: str, default: str = "") -> str:
        try:
            return str(self.services.metin(anahtar, default) or default or anahtar)
        except Exception:
            return str(default or anahtar)

    # =========================================================
    # INTERNAL
    # =========================================================
    def _clear_anchor_widgets(self):
        for anchor in (self.top_anchor, self.center_anchor, self.bottom_anchor):
            try:
                anchor.clear_widgets()
            except Exception:
                pass

    def _rebuild_anchor(self, position: str):
        self._clear_anchor_widgets()

        sol = Label(size_hint_x=1)
        sag = Label(size_hint_x=1)

        hedef = self.bottom_anchor
        if position == "top":
            hedef = self.top_anchor
        elif position == "center":
            hedef = self.center_anchor

        hedef.add_widget(sol)
        hedef.add_widget(self.toast)
        hedef.add_widget(sag)

        self._current_position = position

    def _cancel_hide_event(self):
        try:
            if self._hide_event is not None:
                self._hide_event.cancel()
        except Exception:
            pass
        self._hide_event = None

    def _cancel_anim(self):
        try:
            if self._current_anim is not None:
                self._current_anim.cancel(self.toast)
        except Exception:
            pass
        self._current_anim = None

    def _handle_single_tap(self):
        try:
            if self.toast.disabled or self.toast.opacity <= 0:
                return

            if self._current_on_tap is not None:
                self._current_on_tap()
        except Exception:
            pass

    def _show_error_popup(self, text: str, title: str = ""):
        popup = None
        try:
            content = BoxLayout(
                orientation="vertical",
                spacing=dp(10),
                padding=dp(12),
            )

            baslik = Label(
                text=str(title or self._m("error_occurred", "Hata Oluştu")),
                color=(1, 0.42, 0.42, 1),
                font_size="18sp",
                bold=True,
                size_hint_y=None,
                height=dp(30),
                halign="center",
                valign="middle",
            )
            baslik.bind(size=lambda inst, size: setattr(inst, "text_size", size))
            content.add_widget(baslik)

            alt_baslik = Label(
                text=self._m(
                    "error_detail_copy_hint",
                    "Detaylı hata bilgisi aşağıdadır. Kopyalayabilirsiniz.",
                ),
                color=TEXT_MUTED if TEXT_MUTED else TEXT_PRIMARY,
                font_size="11sp",
                size_hint_y=None,
                height=dp(20),
                halign="center",
                valign="middle",
            )
            alt_baslik.bind(size=lambda inst, size: setattr(inst, "text_size", size))
            content.add_widget(alt_baslik)

            scroll = ScrollView(
                do_scroll_x=True,
                do_scroll_y=True,
                bar_width=dp(8),
            )

            hata_label = Label(
                text=str(text or ""),
                color=TEXT_PRIMARY,
                halign="left",
                valign="top",
                size_hint_y=None,
                font_size="12sp",
            )
            hata_label.bind(
                texture_size=lambda inst, val: setattr(inst, "height", max(dp(180), val[1]))
            )
            hata_label.bind(
                size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
            )

            scroll.add_widget(hata_label)
            content.add_widget(scroll)

            button_row = BoxLayout(
                orientation="horizontal",
                spacing=dp(8),
                size_hint_y=None,
                height=dp(46),
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
                    Clipboard.copy(str(text or ""))
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

            close_btn.bind(on_release=lambda *_: popup.dismiss())
            popup.open()

        except Exception:
            try:
                if popup is not None:
                    popup.dismiss()
            except Exception:
                pass

    # =========================================================
    # API
    # =========================================================
    def show(
        self,
        text: str,
        icon_name: str = "",
        duration: float = 2.4,
        title: str = "",
        position: str = "bottom",
        on_tap=None,
    ):
        temiz_icon = str(icon_name or "").strip().lower()

        if temiz_icon in {"error", "warning_error", "hata"}:
            self._show_error_popup(
                text=str(text or ""),
                title=str(title or self._m("error_occurred", "Hata Oluştu")),
            )
            return

        self._cancel_hide_event()
        self._cancel_anim()

        pos = str(position or "bottom").strip().lower()
        if pos not in {"bottom", "center", "top"}:
            pos = "bottom"

        if pos != self._current_position:
            self._rebuild_anchor(pos)

        self._current_on_tap = on_tap
        self.toast.set_message(
            text=text,
            icon_name=icon_name,
            title=title,
        )
        self.toast.disabled = False

        try:
            self.toast.opacity = 0
        except Exception:
            pass

        try:
            anim = Animation(opacity=1.0, duration=0.18)
            anim.start(self.toast)
            self._current_anim = anim
        except Exception:
            self.toast.opacity = 1.0

        self._hide_event = Clock.schedule_once(
            lambda *_: self.hide(),
            max(0.4, float(duration or 2.4)),
        )

    def hide(self):
        self._cancel_hide_event()
        self._cancel_anim()

        def _finish(*_args):
            try:
                self.toast.opacity = 0
                self.toast.disabled = True
                self._current_on_tap = None
            except Exception:
                pass

        try:
            anim = Animation(opacity=0.0, duration=0.18)
            anim.bind(on_complete=lambda *_: _finish())
            anim.start(self.toast)
            self._current_anim = anim
        except Exception:
            _finish()

    def hide_immediately(self):
        self._cancel_hide_event()
        self._cancel_anim()
        try:
            self.toast.opacity = 0
            self.toast.disabled = True
            self._current_on_tap = None
        except Exception:
            pass

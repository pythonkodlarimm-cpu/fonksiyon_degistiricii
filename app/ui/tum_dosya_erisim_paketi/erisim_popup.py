# -*- coding: utf-8 -*-
from __future__ import annotations

from kivy.animation import Animation
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.utils import platform

from app.ui.tema import TEXT_PRIMARY
from app.ui.tum_dosya_erisim_paketi.bilesenler import AnimatedSeparator, TiklanabilirIcon


def open_access_popup(status_value, debug=None):
    if status_value is True:
        durum_text = "Tüm Dosya Erişimi Açık"
        action_icon = "app/assets/icons/setting_on.png"
        durum_color = (0.26, 1.0, 0.42, 1)
        action_desc = "Erişimi kapatmak için aşağıdaki simgeye dokunun."
    elif status_value is False:
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

    content.add_widget(AnimatedSeparator())

    action_wrap = BoxLayout(
        orientation="vertical",
        size_hint_y=None,
        height=dp(162),
        spacing=dp(10),
    )

    icon = TiklanabilirIcon(
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
    icon_row.add_widget(icon)
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
    desc_label.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))

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

    def glow(*_args):
        try:
            anim = (
                Animation(opacity=0.74, size=(dp(96), dp(96)), duration=0.55)
                + Animation(opacity=1.0, size=(dp(88), dp(88)), duration=0.55)
            )
            anim.repeat = True
            anim.start(icon)
        except Exception:
            pass

    def action(*_args):
        if platform == "android":
            try:
                from app.services.android_ozel_izin_servisi import tum_dosya_erisim_ayarlari_ac
                tum_dosya_erisim_ayarlari_ac()
            except Exception as exc:
                if debug:
                    debug(f"Ayar açma hatası: {exc}")
        popup.dismiss()

    icon.bind(on_release=action)
    popup.bind(on_open=glow)
    popup.open()
    return popup
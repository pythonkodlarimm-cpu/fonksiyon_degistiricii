# -*- coding: utf-8 -*-
from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from app.ui.tema import TEXT_PRIMARY
from app.ui.tum_dosya_erisim_paketi.bilesenler import AnimatedSeparator, TiklanabilirIcon


def open_main_menu(open_access_popup, open_backups_popup):
    content = BoxLayout(
        orientation="vertical",
        padding=dp(16),
        spacing=dp(12),
    )

    title = Label(
        text="Menü İşlemleri",
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

    separator = AnimatedSeparator()
    content.add_widget(separator)

    buttons = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(100),
        spacing=dp(18),
    )

    erisim_wrap = BoxLayout(orientation="vertical", spacing=dp(6))
    erisim_btn = TiklanabilirIcon(
        source="app/assets/icons/settings.png",
        size_hint=(None, None),
        size=(dp(58), dp(58)),
        allow_stretch=True,
        keep_ratio=True,
    )
    erisim_lbl = Label(
        text="Erişim İşlemleri",
        color=TEXT_PRIMARY,
        font_size="12sp",
        halign="center",
        valign="middle",
    )
    erisim_lbl.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))
    erisim_icon_row = BoxLayout(size_hint_y=None, height=dp(64))
    erisim_icon_row.add_widget(Label(size_hint_x=1))
    erisim_icon_row.add_widget(erisim_btn)
    erisim_icon_row.add_widget(Label(size_hint_x=1))
    erisim_wrap.add_widget(erisim_icon_row)
    erisim_wrap.add_widget(erisim_lbl)

    yedek_wrap = BoxLayout(orientation="vertical", spacing=dp(6))
    yedek_btn = TiklanabilirIcon(
        source="app/assets/icons/yedeklenen_dosyalar.png",
        size_hint=(None, None),
        size=(dp(58), dp(58)),
        allow_stretch=True,
        keep_ratio=True,
    )
    yedek_lbl = Label(
        text="Yedeklenen Dosyalar",
        color=TEXT_PRIMARY,
        font_size="12sp",
        halign="center",
        valign="middle",
    )
    yedek_lbl.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))
    yedek_icon_row = BoxLayout(size_hint_y=None, height=dp(64))
    yedek_icon_row.add_widget(Label(size_hint_x=1))
    yedek_icon_row.add_widget(yedek_btn)
    yedek_icon_row.add_widget(Label(size_hint_x=1))
    yedek_wrap.add_widget(yedek_icon_row)
    yedek_wrap.add_widget(yedek_lbl)

    buttons.add_widget(erisim_wrap)
    buttons.add_widget(yedek_wrap)
    content.add_widget(buttons)

    popup = Popup(
        title="",
        content=content,
        size_hint=(0.92, None),
        height=dp(240),
        auto_dismiss=True,
        separator_height=0,
    )

    erisim_btn.bind(on_release=lambda *_: (popup.dismiss(), open_access_popup()))
    yedek_btn.bind(on_release=lambda *_: (popup.dismiss(), open_backups_popup()))

    popup.open()
    return popup
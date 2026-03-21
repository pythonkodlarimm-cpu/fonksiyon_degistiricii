# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/popups/menu_popup.py

ROL:
- Tüm dosya erişim paketi ana menü popup'ını göstermek
- Erişim işlemleri ve yedeklenen dosyalar akışlarına giriş sağlamak
- İkon tabanlı sade menü sunmak

MİMARİ:
- Doğrudan ortak bileşen import etmez
- Ortak yonetici üzerinden erişir
- Popup sadece UI akışını yönetir

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 3
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from app.ui.tema import TEXT_PRIMARY
from app.ui.tum_dosya_erisim_paketi.ortak.yoneticisi import (
    TumDosyaErisimOrtakYoneticisi,
)


def _ortak_yonetici():
    return TumDosyaErisimOrtakYoneticisi()


def _tiklanabilir_icon_sinifi():
    try:
        return _ortak_yonetici().tiklanabilir_icon_sinifi()
    except Exception:
        return None


def _animated_separator_widget():
    try:
        sinif = _ortak_yonetici().animated_separator_sinifi()
        return sinif()
    except Exception:
        return None


def _ikonlu_aksiyon_karti(
    icon_source: str,
    text: str,
    on_release,
):
    IconClass = _tiklanabilir_icon_sinifi()

    wrap = BoxLayout(
        orientation="vertical",
        spacing=dp(6),
    )

    if IconClass is not None:
        try:
            btn = IconClass(
                source=icon_source,
                size_hint=(None, None),
                size=(dp(58), dp(58)),
                allow_stretch=True,
                keep_ratio=True,
            )
        except Exception:
            btn = Label(size_hint=(None, None), size=(dp(58), dp(58)))
    else:
        btn = Label(size_hint=(None, None), size=(dp(58), dp(58)))

    lbl = Label(
        text=str(text or ""),
        color=TEXT_PRIMARY,
        font_size="12sp",
        halign="center",
        valign="middle",
    )
    lbl.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))

    icon_row = BoxLayout(
        size_hint_y=None,
        height=dp(64),
    )
    icon_row.add_widget(Label(size_hint_x=1))
    icon_row.add_widget(btn)
    icon_row.add_widget(Label(size_hint_x=1))

    wrap.add_widget(icon_row)
    wrap.add_widget(lbl)

    try:
        btn.bind(on_release=on_release)
    except Exception:
        pass

    return wrap


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

    separator = _animated_separator_widget()
    if separator is not None:
        content.add_widget(separator)

    buttons = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(100),
        spacing=dp(18),
    )

    popup = Popup(
        title="",
        content=content,
        size_hint=(0.92, None),
        height=dp(240),
        auto_dismiss=True,
        separator_height=0,
    )

    def _open_access(*_args):
        try:
            popup.dismiss()
        except Exception:
            pass

        try:
            if callable(open_access_popup):
                open_access_popup()
        except Exception:
            pass

    def _open_backups(*_args):
        try:
            popup.dismiss()
        except Exception:
            pass

        try:
            if callable(open_backups_popup):
                open_backups_popup()
        except Exception:
            pass

    buttons.add_widget(
        _ikonlu_aksiyon_karti(
            icon_source="app/assets/icons/settings.png",
            text="Erişim İşlemleri",
            on_release=_open_access,
        )
    )

    buttons.add_widget(
        _ikonlu_aksiyon_karti(
            icon_source="app/assets/icons/yedeklenen_dosyalar.png",
            text="Yedeklenen Dosyalar",
            on_release=_open_backups,
        )
    )

    content.add_widget(buttons)

    popup.open()
    return popup
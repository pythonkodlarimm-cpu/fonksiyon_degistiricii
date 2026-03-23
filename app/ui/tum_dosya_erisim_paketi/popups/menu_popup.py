# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/popups/menu_popup.py

ROL:
- Tüm dosya erişim paketi ana menü popup'ını göstermek
- Yedeklenen dosyalar akışına giriş sağlamak
- Dil seçimi popup akışına giriş sağlamak
- İkon tabanlı sade menü sunmak

MİMARİ:
- Doğrudan ortak bileşen import etmez
- Ortak yonetici üzerinden erişir
- Dil popup akışını kendi yöneticisi üzerinden açar
- Popup sadece UI akışını yönetir

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 5
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from app.services.yoneticisi import ServicesYoneticisi
from app.ui.dil_paketi.popup.yoneticisi import DilPopupYoneticisi
from app.ui.tema import TEXT_PRIMARY
from app.ui.tum_dosya_erisim_paketi.ortak.yoneticisi import (
    TumDosyaErisimOrtakYoneticisi,
)


def _ortak_yonetici():
    return TumDosyaErisimOrtakYoneticisi()


def _services():
    return ServicesYoneticisi()


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


def _m(anahtar: str, default: str = "") -> str:
    try:
        return str(_services().metin(anahtar, default) or default or anahtar)
    except Exception:
        return str(default or anahtar)


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


def open_main_menu(
    open_backups_popup,
    on_language_changed=None,
    services=None,
):
    servisler = services or _services()

    content = BoxLayout(
        orientation="vertical",
        padding=dp(16),
        spacing=dp(12),
    )

    title = Label(
        text=_m("settings", "Menü İşlemleri"),
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
        height=dp(220),
        auto_dismiss=True,
        separator_height=0,
    )

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

    def _open_language_popup(*_args):
        try:
            popup.dismiss()
        except Exception:
            pass

        try:
            DilPopupYoneticisi().popup_ac(
                services=servisler,
                on_language_changed=on_language_changed,
            )
        except Exception:
            pass

    buttons.add_widget(Label(size_hint_x=1))

    buttons.add_widget(
        _ikonlu_aksiyon_karti(
            icon_source="app/assets/icons/yedeklenen_dosyalar.png",
            text="Yedeklenen Dosyalar",
            on_release=_open_backups,
        )
    )

    buttons.add_widget(
        _ikonlu_aksiyon_karti(
            icon_source="app/assets/icons/dil.png",
            text=servisler.metin("language", "Dil"),
            on_release=_open_language_popup,
        )
    )

    buttons.add_widget(Label(size_hint_x=1))

    content.add_widget(buttons)

    popup.open()
    return popup

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
- Ortak yönetici üzerinden erişir
- Dil popup akışını kendi yöneticisi üzerinden açar
- Popup sadece UI akışını yönetir
- Görünen metinler services üzerinden alınabilir
- Services verilmezse güvenli fallback ile çalışır
- Hardcoded kullanıcı metni bırakılmaz

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 7
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
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY
from app.ui.tum_dosya_erisim_paketi.ortak.yoneticisi import (
    TumDosyaErisimOrtakYoneticisi,
)


def _ortak_yonetici():
    return TumDosyaErisimOrtakYoneticisi()


def _varsayilan_services():
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


def _m(services, anahtar: str, default: str = "") -> str:
    try:
        if services is not None:
            return str(services.metin(anahtar, default) or default or anahtar)
    except Exception:
        pass
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
        size_hint_x=1,
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
            btn = Label(
                text="•",
                size_hint=(None, None),
                size=(dp(58), dp(58)),
                color=TEXT_PRIMARY,
            )
    else:
        btn = Label(
            text="•",
            size_hint=(None, None),
            size=(dp(58), dp(58)),
            color=TEXT_PRIMARY,
        )

    lbl = Label(
        text=str(text or ""),
        color=TEXT_PRIMARY,
        font_size="12sp",
        halign="center",
        valign="middle",
        size_hint_y=None,
        height=dp(32),
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
    servisler = services or _varsayilan_services()

    content = BoxLayout(
        orientation="vertical",
        padding=dp(16),
        spacing=dp(12),
    )

    title = Label(
        text=_m(servisler, "settings", "Ayarlar"),
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

    subtitle = Label(
        text=_m(servisler, "menu_subtitle", "İşlem seçin"),
        color=TEXT_MUTED,
        font_size="11sp",
        size_hint_y=None,
        height=dp(18),
        halign="center",
        valign="middle",
    )
    subtitle.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    content.add_widget(subtitle)

    separator = _animated_separator_widget()
    if separator is not None:
        content.add_widget(separator)

    buttons = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(108),
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

    buttons.add_widget(
        _ikonlu_aksiyon_karti(
            icon_source="app/assets/icons/dil.png",
            text=_m(servisler, "language", "Dil"),
            on_release=_open_language_popup,
        )
    )

    buttons.add_widget(
        _ikonlu_aksiyon_karti(
            icon_source="app/assets/icons/yedeklenen_dosyalar.png",
            text=_m(servisler, "backup_files", "Yedeklenen Dosyalar"),
            on_release=_open_backups,
        )
    )

    content.add_widget(buttons)

    popup.open()
    return popup

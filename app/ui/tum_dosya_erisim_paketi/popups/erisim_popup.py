# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/popups/erisim_popup.py

ROL:
- Tüm dosya erişimi durumunu kullanıcıya popup ile göstermek
- Erişim açık / kapalı / bilinmiyor durumlarına göre görsel açıklama sunmak
- Kullanıcıyı uygun Android ayar ekranına yönlendirmek

MİMARİ:
- Doğrudan bileşen veya servis import etmez
- Ortak yonetici ve Android yoneticisi üzerinden erişir
- UI bağımlılıkları kontrollü tutulur

API UYUMLULUK:
- Android API 35 ile uyumludur
- Android dışı ortamlarda güvenli davranır
- Hata durumunda debug callback varsa bilgi geçer

SURUM: 3
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from kivy.animation import Animation
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.utils import platform

from app.ui.tema import TEXT_PRIMARY
from app.ui.tum_dosya_erisim_paketi.ortak.yoneticisi import (
    TumDosyaErisimOrtakYoneticisi,
)


def _debug_yaz(debug, message: str) -> None:
    try:
        if callable(debug):
            debug(str(message))
    except Exception:
        pass


def _ortak_yonetici():
    return TumDosyaErisimOrtakYoneticisi()


def _tiklanabilir_icon_sinifi():
    try:
        return _ortak_yonetici().tiklanabilir_icon_sinifi()
    except Exception:
        return None


def _animated_separator_sinifi():
    try:
        return _ortak_yonetici().animated_separator_sinifi()
    except Exception:
        return None


def _android_yonetici():
    try:
        from app.services.android import AndroidYoneticisi
        return AndroidYoneticisi()
    except Exception:
        return None


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

    SeparatorClass = _animated_separator_sinifi()
    if SeparatorClass is not None:
        try:
            content.add_widget(SeparatorClass())
        except Exception:
            pass

    action_wrap = BoxLayout(
        orientation="vertical",
        size_hint_y=None,
        height=dp(162),
        spacing=dp(10),
    )

    IconClass = _tiklanabilir_icon_sinifi()
    if IconClass is not None:
        try:
            icon = IconClass(
                source=action_icon,
                size_hint=(None, None),
                size=(dp(88), dp(88)),
                opacity=1,
                allow_stretch=True,
                keep_ratio=True,
            )
        except Exception:
            icon = Label(size_hint=(None, None), size=(dp(88), dp(88)))
    else:
        icon = Label(size_hint=(None, None), size=(dp(88), dp(88)))

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
            _ortak_yonetici().start_icon_glow(
                widget=icon,
                size_small_dp=88,
                size_big_dp=96,
                duration=0.55,
            )
        except Exception:
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
                android_yonetici = _android_yonetici()
                if android_yonetici is not None:
                    android_yonetici.tum_dosya_erisim_ayarlari_ac()
            except Exception as exc:
                _debug_yaz(debug, f"Ayar açma hatası: {exc}")
        popup.dismiss()

    try:
        icon.bind(on_release=action)
    except Exception:
        pass

    popup.bind(on_open=glow)
    popup.open()
    return popup
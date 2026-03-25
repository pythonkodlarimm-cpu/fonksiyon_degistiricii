# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/popups/onay_popup.py

ROL:
- Kullanıcıdan onay almak için sade popup göstermek
- Başlık, açıklama ve onay / vazgeç aksiyonlarını sunmak
- İkon tabanlı onay akışını desteklemek
- Görünen metinlerde services tabanlı dil desteğine hazır olmak

MİMARİ:
- Doğrudan ortak bileşen import etmez
- Ortak yönetici üzerinden erişir
- Popup yalnızca UI onay akışını yönetir
- services verilirse sabit metinlerde dil servisi kullanılabilir
- services verilmezse güvenli fallback ile çalışır
- Hardcoded kullanıcı metni bırakılmaz

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

from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY
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


def _m(services, anahtar: str, default: str = "") -> str:
    try:
        if services is not None:
            return str(services.metin(anahtar, default) or default or anahtar)
    except Exception:
        pass
    return str(default or anahtar)


def _aksiyon_karti(
    icon_source: str,
    text: str,
    on_release,
):
    IconClass = _tiklanabilir_icon_sinifi()

    wrap = BoxLayout(
        orientation="vertical",
        spacing=dp(4),
        size_hint_x=1,
    )

    if IconClass is not None:
        try:
            btn = IconClass(
                source=icon_source,
                size_hint=(None, None),
                size=(dp(34), dp(34)),
                allow_stretch=True,
                keep_ratio=True,
            )
        except Exception:
            btn = Label(size_hint=(None, None), size=(dp(34), dp(34)))
    else:
        btn = Label(size_hint=(None, None), size=(dp(34), dp(34)))

    lbl = Label(
        text=str(text or ""),
        color=TEXT_MUTED,
        font_size="11sp",
        halign="center",
        valign="middle",
    )
    lbl.bind(size=lambda inst, size: setattr(inst, "text_size", size))

    row = BoxLayout(
        size_hint_y=None,
        height=dp(36),
    )
    row.add_widget(Label(size_hint_x=1))
    row.add_widget(btn)
    row.add_widget(Label(size_hint_x=1))

    wrap.add_widget(row)
    wrap.add_widget(lbl)

    try:
        btn.bind(on_release=on_release)
    except Exception:
        pass

    return wrap, btn


def show_confirm_popup(
    title_text: str,
    body_text: str,
    on_confirm,
    confirm_icon: str = "delete.png",
    services=None,
):
    content = BoxLayout(
        orientation="vertical",
        padding=dp(14),
        spacing=dp(12),
    )

    title = Label(
        text=str(title_text or _m(services, "confirm_title", "Onay")),
        color=TEXT_PRIMARY,
        font_size="17sp",
        bold=True,
        size_hint_y=None,
        height=dp(28),
        halign="center",
        valign="middle",
    )
    title.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    content.add_widget(title)

    body = Label(
        text=str(body_text or ""),
        color=TEXT_PRIMARY,
        font_size="13sp",
        halign="left",
        valign="middle",
    )
    body.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))
    content.add_widget(body)

    actions = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(56),
        spacing=dp(16),
    )

    popup = Popup(
        title="",
        content=content,
        size_hint=(0.88, None),
        height=dp(220),
        auto_dismiss=True,
        separator_height=0,
    )

    def _cancel(*_args):
        try:
            popup.dismiss()
        except Exception:
            pass

    def _confirm(*_args):
        try:
            popup.dismiss()
        except Exception:
            pass

        try:
            if callable(on_confirm):
                on_confirm()
        except Exception:
            raise

    iptal_wrap, _iptal_btn = _aksiyon_karti(
        icon_source="app/assets/icons/cancel.png",
        text=_m(services, "cancel", "Vazgeç"),
        on_release=_cancel,
    )

    onay_wrap, _onay_btn = _aksiyon_karti(
        icon_source=f"app/assets/icons/{confirm_icon}",
        text=_m(services, "confirm", "Onayla"),
        on_release=_confirm,
    )

    actions.add_widget(iptal_wrap)
    actions.add_widget(onay_wrap)
    content.add_widget(actions)

    popup.open()
    return popup

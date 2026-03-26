# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/popups/indirme_sonuc_popup.py

ROL:
- Yedek indirme/kaydetme işlemi sonrası sonuç popup'ı göstermek
- Kaydedilen konumu kullanıcıya göstermek
- Görünen metinleri services tabanlı dil desteği ile üretmek
- Sade ve tek aksiyonlu kapanış akışı sunmak
- Konum açma akışını bilinçli olarak devre dışı bırakmak

MİMARİ:
- Doğrudan ortak bileşen import etmez
- Ortak yönetici üzerinden erişir
- Popup akışı sade tutulur
- services verilirse sabit metinler dil servisi üzerinden alınır
- services verilmezse güvenli fallback ile çalışır
- Hardcoded kullanıcı metni bırakılmaz
- Tek butonlu kapanış davranışı korunur
- Android / AAB / masaüstü ortamlarında aynı davranışı verir

API UYUMLULUK:
- Android API 35 ile uyumludur
- Android dışı ortamlarda güvenli fallback uygular
- Doğrudan platforma özel hata kullanıcıya taşınmaz
- Konum açma butonu bilinçli olarak kaldırılmıştır

SURUM: 6
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY
from app.ui.tum_dosya_erisim_paketi.ortak.yoneticisi import (
    TumDosyaErisimOrtakYoneticisi,
)


def _animated_separator_widget():
    try:
        sinif = TumDosyaErisimOrtakYoneticisi().animated_separator_sinifi()
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


def _safe_path_text(saved_path: str | Path) -> str:
    try:
        return str(saved_path or "").strip()
    except Exception:
        return ""


def show_download_result_popup(
    saved_path: str | Path,
    selected_by_user: bool = False,
    services=None,
):
    hedef = _safe_path_text(saved_path)

    title_text = _m(services, "operation_completed", "İşlem Tamam")

    if selected_by_user:
        body_text = (
            f"{_m(services, 'backup_saved_to_location', 'Yedek şu konuma kaydedildi:')}\n"
            f"{hedef}"
        )
    else:
        body_text = (
            f"{_m(services, 'backup_saved_to_default_location', 'Yedek varsayılan konuma kaydedildi:')}\n"
            f"{hedef}"
        )

    content = BoxLayout(
        orientation="vertical",
        padding=dp(14),
        spacing=dp(10),
    )

    title = Label(
        text=title_text,
        color=TEXT_PRIMARY,
        font_size="17sp",
        bold=True,
        size_hint_y=None,
        height=dp(26),
        halign="center",
        valign="middle",
    )
    title.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    content.add_widget(title)

    sep1 = _animated_separator_widget()
    if sep1 is not None:
        content.add_widget(sep1)

    body = Label(
        text=body_text,
        color=TEXT_MUTED,
        font_size="12sp",
        size_hint_y=None,
        height=dp(86),
        halign="center",
        valign="middle",
    )
    body.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))
    content.add_widget(body)

    sep2 = _animated_separator_widget()
    if sep2 is not None:
        content.add_widget(sep2)

    button_row = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(42),
        spacing=dp(8),
    )

    btn_ok = Button(
        text=_m(services, "ok", "Tamam"),
        background_normal="",
        background_color=(0.18, 0.18, 0.22, 1),
        color=(0.95, 0.95, 0.98, 1),
    )

    button_row.add_widget(btn_ok)
    content.add_widget(button_row)

    popup = Popup(
        title="",
        content=content,
        size_hint=(0.88, 0.34),
        auto_dismiss=True,
        separator_height=0,
    )

    def _on_ok(*_args):
        try:
            popup.dismiss()
        except Exception:
            pass

    btn_ok.bind(on_release=_on_ok)

    popup.open()
    return popup

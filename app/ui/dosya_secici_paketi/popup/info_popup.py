# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/popup/info_popup.py

ROL:
- Bilgi mesajlarını basit bir popup içinde göstermek
- Sahip widget varsa debug log bırakmak
- Dosya seçici paketinin popup katmanında sade bilgi iletişimi sağlamak

MİMARİ:
- Doğrudan Android API çağrısı yapmaz
- Kivy Popup tabanlıdır
- Güvenli metin ve popup akışı korunur
- Üst katman popup/yoneticisi.py üzerinden erişmelidir

API UYUMLULUK:
- Android 14 / API 34+ uyumlu
- Özel izin veya bridge bağımlılığı yoktur
- Platform bağımsız güvenli yardımcı UI katmanıdır

SURUM: 2
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from app.ui.tema import TEXT_PRIMARY


def show_info_popup(owner, title: str, message: str):
    try:
        if owner is not None and hasattr(owner, "_debug"):
            owner._debug(f"[INFO_POPUP] {title}: {message}")
    except Exception:
        pass

    icerik = BoxLayout(
        orientation="vertical",
        spacing=dp(10),
        padding=dp(12),
    )

    lbl = Label(
        text=str(message or ""),
        color=TEXT_PRIMARY,
        halign="left",
        valign="middle",
    )
    lbl.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))
    icerik.add_widget(lbl)

    btn = Button(
        text="Tamam",
        size_hint_y=None,
        height=dp(42),
        background_normal="",
        background_down="",
        background_color=(0.20, 0.20, 0.24, 1),
        color=TEXT_PRIMARY,
    )

    popup = Popup(
        title=str(title or ""),
        content=icerik,
        size_hint=(0.86, 0.36),
        auto_dismiss=False,
    )

    btn.bind(on_release=lambda *_: popup.dismiss())
    icerik.add_widget(btn)

    try:
        popup.open()
    except Exception:
        try:
            if owner is not None and hasattr(owner, "_debug"):
                owner._debug("[INFO_POPUP] popup açılamadı")
        except Exception:
            pass
# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/popups/yedek_goruntuleme_popup.py

ROL:
- Seçilen yedek dosyasının içeriğini popup içinde göstermek
- Yedek adını başlık olarak sunmak
- Uzun içerikleri kaydırılabilir alanda göstermek
- Görünen metinlerde services tabanlı dil desteğine hazır olmak

MİMARİ:
- Doğrudan dosya servisi import etmez
- DosyaYoneticisi üzerinden erişir
- Popup yalnızca görüntüleme akışını yönetir
- services verilirse sabit metinler dil servisi üzerinden alınabilir
- services verilmezse güvenli fallback ile çalışır
- Hardcoded kullanıcı metni bırakılmaz

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 4
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

from app.ui.tema import TEXT_PRIMARY


def _dosya_yoneticisi():
    from app.services.dosya import DosyaYoneticisi
    return DosyaYoneticisi()


def _m(services, anahtar: str, default: str = "") -> str:
    try:
        if services is not None:
            return str(services.metin(anahtar, default) or default or anahtar)
    except Exception:
        pass
    return str(default or anahtar)


def open_backup_view_popup(yedek: Path, services=None):
    try:
        icerik = _dosya_yoneticisi().read_text(yedek)
    except Exception as exc:
        icerik = (
            f"{_m(services, 'file_could_not_be_viewed', 'Dosya görüntülenemedi:')} {exc}"
        )

    content = BoxLayout(
        orientation="vertical",
        padding=dp(12),
        spacing=dp(8),
    )

    baslik = Label(
        text=str(getattr(yedek, "name", "") or _m(services, "backup", "Yedek")),
        color=TEXT_PRIMARY,
        font_size="16sp",
        bold=True,
        size_hint_y=None,
        height=dp(28),
        halign="center",
        valign="middle",
    )
    baslik.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    content.add_widget(baslik)

    body = Label(
        text=str(icerik or ""),
        color=TEXT_PRIMARY,
        halign="left",
        valign="top",
        size_hint_y=None,
    )
    body.bind(
        texture_size=lambda inst, val: setattr(inst, "height", max(dp(40), val[1]))
    )
    body.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))

    scroll = ScrollView(
        do_scroll_x=True,
        do_scroll_y=True,
    )
    scroll.add_widget(body)
    content.add_widget(scroll)

    popup = Popup(
        title="",
        content=content,
        size_hint=(0.95, 0.88),
        auto_dismiss=True,
        separator_height=0,
    )
    popup.open()
    return popup

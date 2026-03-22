# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/yedek/yedek_satiri.py

ROL:
- Tek bir yedek dosyası için liste satırı oluşturmak
- Görüntüle / indir / sil aksiyonlarını ikonlarla sunmak
- Yedek adı ve yolunu satır üzerinde göstermek

MİMARİ:
- Doğrudan ortak bileşen import etmez
- Ortak yönetici üzerinden TiklanabilirIcon erişimi alır
- UI satırı üretir, iş mantığını callback'lere bırakır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 3
TARIH: 2026-03-22
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from app.ui.kart import Kart
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY
from app.ui.tum_dosya_erisim_paketi.ortak.yoneticisi import (
    TumDosyaErisimOrtakYoneticisi,
)


def _tiklanabilir_icon_sinifi():
    try:
        return TumDosyaErisimOrtakYoneticisi().tiklanabilir_icon_sinifi()
    except Exception:
        return None


def _safe_callback(callback, yedek: Path):
    try:
        if callable(callback):
            callback(yedek)
    except Exception:
        pass


def _safe_text(value) -> str:
    try:
        return str(value or "")
    except Exception:
        return ""


def _safe_name(yedek: Path) -> str:
    try:
        return _safe_text(getattr(yedek, "name", "") or "")
    except Exception:
        return ""


def _safe_path(yedek: Path) -> str:
    try:
        return _safe_text(yedek)
    except Exception:
        return ""


def _icon_widget(icon_source: str, fallback_text: str = ""):
    IconClass = _tiklanabilir_icon_sinifi()

    if IconClass is not None:
        try:
            return IconClass(
                source=icon_source,
                size_hint=(None, None),
                size=(dp(32), dp(32)),
                allow_stretch=True,
                keep_ratio=True,
            )
        except Exception:
            pass

    return Label(
        text=fallback_text,
        size_hint=(None, None),
        size=(dp(32), dp(32)),
        color=TEXT_MUTED,
        halign="center",
        valign="middle",
        font_size="10sp",
    )


def _bind_release(widget, callback, yedek: Path):
    try:
        widget.bind(on_release=lambda *_: _safe_callback(callback, yedek))
        return
    except Exception:
        pass

    try:
        widget.bind(on_touch_down=lambda *_: (_safe_callback(callback, yedek), False)[1])
    except Exception:
        pass


def build_backup_row(yedek: Path, on_view, on_download, on_delete):
    yedek = Path(yedek)

    satir = Kart(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(66),
        padding=(dp(10), dp(8), dp(10), dp(8)),
        spacing=dp(8),
        bg=(0.10, 0.13, 0.18, 1),
        border=(0.18, 0.21, 0.27, 1),
        radius=12,
    )

    metin_wrap = BoxLayout(
        orientation="vertical",
        spacing=dp(2),
    )

    ad = Label(
        text=_safe_name(yedek),
        color=TEXT_PRIMARY,
        font_size="13sp",
        halign="left",
        valign="middle",
        size_hint_y=None,
        height=dp(22),
        shorten=True,
        shorten_from="right",
    )
    ad.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))

    yol = Label(
        text=_safe_path(yedek),
        color=TEXT_MUTED,
        font_size="10sp",
        halign="left",
        valign="middle",
        size_hint_y=None,
        height=dp(18),
        shorten=True,
        shorten_from="center",
    )
    yol.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))

    metin_wrap.add_widget(ad)
    metin_wrap.add_widget(yol)

    aksiyonlar = BoxLayout(
        orientation="horizontal",
        size_hint_x=None,
        width=dp(150),
        spacing=dp(8),
    )

    gor_btn = _icon_widget("app/assets/icons/visibility_on.png", "G")
    indir_btn = _icon_widget("app/assets/icons/download.png", "İ")
    sil_btn = _icon_widget("app/assets/icons/delete.png", "S")

    _bind_release(gor_btn, on_view, yedek)
    _bind_release(indir_btn, on_download, yedek)
    _bind_release(sil_btn, on_delete, yedek)

    aksiyonlar.add_widget(gor_btn)
    aksiyonlar.add_widget(indir_btn)
    aksiyonlar.add_widget(sil_btn)

    satir.add_widget(metin_wrap)
    satir.add_widget(aksiyonlar)
    return satir
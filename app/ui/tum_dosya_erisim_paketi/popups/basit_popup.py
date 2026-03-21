# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/popups/basit_popup.py

ROL:
- Küçük ve sade bilgi popup'ları göstermek
- Başarı / bilgi / hata mesajlarını kısa ve okunaklı biçimde sunmak
- İstenirse otomatik kapanmak

MİMARİ:
- Doğrudan bilesen import etmez
- Ortak yonetici üzerinden erişir
- UI bağımlılıkları minimize edilmiştir

SURUM: 3
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY
from app.ui.tum_dosya_erisim_paketi.ortak.yoneticisi import (
    TumDosyaErisimOrtakYoneticisi,
)


def _tiklanabilir_icon():
    try:
        return TumDosyaErisimOrtakYoneticisi().tiklanabilir_icon_sinifi()
    except Exception:
        return None


def show_simple_popup(
    title_text: str,
    body_text: str,
    icon_name: str = "onaylandi.png",
    auto_close_seconds: float | None = 1.8,
    compact: bool = True,
):
    """
    Küçük, sade popup gösterir.
    """

    content = BoxLayout(
        orientation="vertical",
        padding=dp(14),
        spacing=dp(10),
    )

    # =========================================================
    # ICON
    # =========================================================
    icon_row = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(40),
    )
    icon_row.add_widget(Label(size_hint_x=1))

    IconClass = _tiklanabilir_icon()

    if IconClass:
        try:
            icon = IconClass(
                source=f"app/assets/icons/{icon_name}",
                size_hint=(None, None),
                size=(dp(28), dp(28)),
                allow_stretch=True,
                keep_ratio=True,
            )
            icon_row.add_widget(icon)
        except Exception:
            icon_row.add_widget(Label(size_hint_x=None, width=dp(28)))
    else:
        icon_row.add_widget(Label(size_hint_x=None, width=dp(28)))

    icon_row.add_widget(Label(size_hint_x=1))
    content.add_widget(icon_row)

    # =========================================================
    # TITLE
    # =========================================================
    title = Label(
        text=str(title_text or ""),
        color=TEXT_PRIMARY,
        font_size="16sp",
        bold=True,
        size_hint_y=None,
        height=dp(24),
        halign="center",
        valign="middle",
    )
    title.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    content.add_widget(title)

    # =========================================================
    # BODY
    # =========================================================
    body = Label(
        text=str(body_text or ""),
        color=TEXT_MUTED if TEXT_MUTED else TEXT_PRIMARY,
        font_size="12sp",
        halign="center",
        valign="middle",
    )
    body.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))
    content.add_widget(body)

    # =========================================================
    # POPUP
    # =========================================================
    popup = Popup(
        title="",
        content=content,
        size_hint=(0.74, None) if compact else (0.88, None),
        height=dp(170) if compact else dp(220),
        auto_dismiss=True,
        separator_height=0,
    )

    # =========================================================
    # AUTO CLOSE
    # =========================================================
    if auto_close_seconds is not None:

        def _close(*_args):
            try:
                popup.dismiss()
            except Exception:
                pass

        popup.bind(
            on_open=lambda *_: Clock.schedule_once(
                _close,
                max(0.6, float(auto_close_seconds)),
            )
        )

    popup.open()
    return popup
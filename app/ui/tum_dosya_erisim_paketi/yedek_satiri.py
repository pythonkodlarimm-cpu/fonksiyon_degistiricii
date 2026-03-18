# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from app.ui.kart import Kart
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY
from app.ui.tum_dosya_erisim_paketi.bilesenler import TiklanabilirIcon


def build_backup_row(yedek: Path, on_view, on_download, on_delete):
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

    metin_wrap = BoxLayout(orientation="vertical", spacing=dp(2))

    ad = Label(
        text=str(getattr(yedek, "name", "") or ""),
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
        text=str(yedek),
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

    gor_btn = TiklanabilirIcon(
        source="app/assets/icons/visibility_on.png",
        size_hint=(None, None),
        size=(dp(32), dp(32)),
        allow_stretch=True,
        keep_ratio=True,
    )
    indir_btn = TiklanabilirIcon(
        source="app/assets/icons/download.png",
        size_hint=(None, None),
        size=(dp(32), dp(32)),
        allow_stretch=True,
        keep_ratio=True,
    )
    sil_btn = TiklanabilirIcon(
        source="app/assets/icons/delete.png",
        size_hint=(None, None),
        size=(dp(32), dp(32)),
        allow_stretch=True,
        keep_ratio=True,
    )

    gor_btn.bind(on_release=lambda *_: on_view(yedek))
    indir_btn.bind(on_release=lambda *_: on_download(yedek))
    sil_btn.bind(on_release=lambda *_: on_delete(yedek))

    aksiyonlar.add_widget(gor_btn)
    aksiyonlar.add_widget(indir_btn)
    aksiyonlar.add_widget(sil_btn)

    satir.add_widget(metin_wrap)
    satir.add_widget(aksiyonlar)
    return satir
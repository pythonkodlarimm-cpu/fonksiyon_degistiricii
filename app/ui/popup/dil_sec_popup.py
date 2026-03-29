# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/popup/dil_sec_popup.py

ROL:
- Uygulama dil seçimi popup'ını açar
- Mevcut dilleri alfabetik sırada listeler
- Seçilen dili servis üzerinden uygular
- Kapanış sonrası dış callback tetikler
- Dil entegrasyonuna uyumludur

MİMARİ:
- UI katmanıdır
- Dil servisinden veri alır
- Aksiyon callback dışarıdan alınır
- Geriye uyumluluk katmanı içermez

SURUM: 2
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView


def _dil_adi(item: dict[str, Any]) -> str:
    """
    Dil görünen adını güvenli biçimde çözer.
    """
    name = str(item.get("name", "") or "").strip()
    code = str(item.get("code", "") or "").strip()

    if name:
        return name
    if code:
        return code
    return "?"


def dil_sec_popup(*, services, on_degisti) -> None:
    """
    Dil seçim popup'ını açar.
    """
    dil_servisi = services.dil_servisi()
    tum_diller = list(dil_servisi.tum_diller() or [])

    if not tum_diller:
        tum_diller = [{"code": "tr", "name": "Türkçe"}]

    tum_diller = sorted(
        tum_diller,
        key=lambda item: _dil_adi(item).casefold(),
    )

    root = BoxLayout(
        orientation="vertical",
        spacing=dp(8),
        padding=dp(10),
    )

    scroll = ScrollView()
    root.add_widget(scroll)

    liste = BoxLayout(
        orientation="vertical",
        spacing=dp(8),
        size_hint_y=None,
    )
    liste.bind(minimum_height=lambda inst, val: setattr(inst, "height", val))
    scroll.add_widget(liste)

    popup_ref: dict[str, Popup | None] = {"popup": None}

    def _sec(kod: str) -> None:
        dil_servisi.dil_degistir(kod)

        popup = popup_ref["popup"]
        if popup is not None:
            popup.dismiss()

        if callable(on_degisti):
            on_degisti()

    for item in tum_diller:
        kod = str(item.get("code", "tr") or "tr")
        ad = _dil_adi(item)

        btn = Button(
            text=ad,
            size_hint_y=None,
            height=dp(48),
        )
        btn.bind(on_release=lambda _btn, secili_kod=kod: _sec(secili_kod))
        liste.add_widget(btn)

    popup = Popup(
        title=str(dil_servisi.t("select_language") or "Dil Seç"),
        content=root,
        size_hint=(0.82, 0.70),
        auto_dismiss=True,
    )
    popup_ref["popup"] = popup
    popup.open()
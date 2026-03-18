# -*- coding: utf-8 -*-
from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY
from app.ui.tum_dosya_erisim_paketi.bilesenler import TiklanabilirIcon


def show_confirm_popup(
    title_text: str,
    body_text: str,
    on_confirm,
    confirm_icon: str = "delete.png",
):
    content = BoxLayout(
        orientation="vertical",
        padding=dp(14),
        spacing=dp(12),
    )

    title = Label(
        text=str(title_text or ""),
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

    iptal_wrap = BoxLayout(orientation="vertical", spacing=dp(4))
    iptal_btn = TiklanabilirIcon(
        source="app/assets/icons/cancel.png",
        size_hint=(None, None),
        size=(dp(34), dp(34)),
        allow_stretch=True,
        keep_ratio=True,
    )
    iptal_lbl = Label(
        text="Vazgeç",
        color=TEXT_MUTED,
        font_size="11sp",
        halign="center",
        valign="middle",
    )
    iptal_lbl.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    iptal_row = BoxLayout(size_hint_y=None, height=dp(36))
    iptal_row.add_widget(Label(size_hint_x=1))
    iptal_row.add_widget(iptal_btn)
    iptal_row.add_widget(Label(size_hint_x=1))
    iptal_wrap.add_widget(iptal_row)
    iptal_wrap.add_widget(iptal_lbl)

    sil_wrap = BoxLayout(orientation="vertical", spacing=dp(4))
    sil_btn = TiklanabilirIcon(
        source=f"app/assets/icons/{confirm_icon}",
        size_hint=(None, None),
        size=(dp(34), dp(34)),
        allow_stretch=True,
        keep_ratio=True,
    )
    sil_lbl = Label(
        text="Sil",
        color=TEXT_MUTED,
        font_size="11sp",
        halign="center",
        valign="middle",
    )
    sil_lbl.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    sil_row = BoxLayout(size_hint_y=None, height=dp(36))
    sil_row.add_widget(Label(size_hint_x=1))
    sil_row.add_widget(sil_btn)
    sil_row.add_widget(Label(size_hint_x=1))
    sil_wrap.add_widget(sil_row)
    sil_wrap.add_widget(sil_lbl)

    actions.add_widget(iptal_wrap)
    actions.add_widget(sil_wrap)
    content.add_widget(actions)

    popup = Popup(
        title="",
        content=content,
        size_hint=(0.88, None),
        height=dp(220),
        auto_dismiss=True,
        separator_height=0,
    )

    iptal_btn.bind(on_release=lambda *_: popup.dismiss())

    def _confirm(*_args):
        try:
            popup.dismiss()
        except Exception:
            pass
        try:
            on_confirm()
        except Exception:
            raise

    sil_btn.bind(on_release=_confirm)

    popup.open()
    return popup
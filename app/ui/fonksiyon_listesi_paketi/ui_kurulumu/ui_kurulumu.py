# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/ui_kurulumu/ui_kurulumu.py
"""

from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from app.ui.icon_toolbar import IconToolbar
from app.ui.iconlu_baslik import IconluBaslik
from app.ui.kart import Kart
from app.ui.tema import (
    CARD_BG_DARK,
    CARD_BG_SOFT,
    INPUT_BG,
    RADIUS_MD,
    TEXT_MUTED,
    TEXT_PRIMARY,
)


def build_ui(owner) -> None:
    owner._ui_kurulumu_yoneticisi.build_header_row(owner)
    owner._ui_kurulumu_yoneticisi.build_search_box(owner)
    owner._ui_kurulumu_yoneticisi.build_list_box(owner)
    owner._ui_kurulumu_yoneticisi.build_preview_boxes(owner)

    owner._sync_list_visibility()
    owner._selected_preview_card_text_guncelle()
    owner._new_preview_card_text_guncelle()
    owner._render_items([], keep_scroll=False)


def build_header_row(owner) -> None:
    row = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(42),
        spacing=dp(8),
    )

    owner.header = IconluBaslik(
        text="Fonksiyonlar",
        icon_name="layers.png",
        height_dp=32,
        font_size="16sp",
        color=TEXT_PRIMARY,
        size_hint_x=1,
    )
    row.add_widget(owner.header)

    owner.count_label = Label(
        text="0 / 0",
        size_hint_x=None,
        width=dp(84),
        color=TEXT_MUTED,
        font_size="13sp",
        halign="right",
        valign="middle",
    )
    owner.count_label.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    owner.add_widget(row)
    row.add_widget(owner.count_label)

    owner.header_toolbar = IconToolbar(
        spacing_dp=12,
        padding_dp=2,
    )

    owner.toggle_button = owner.header_toolbar.add_tool(
        icon_name="visibility_on.png",
        text="Liste",
        on_release=owner._toggle_list_visibility,
        icon_size_dp=32,
        text_size="10sp",
        color=TEXT_MUTED,
        icon_bg=None,
    )
    owner.add_widget(owner.header_toolbar)


def build_search_box(owner) -> None:
    owner.search_wrap = Kart(
        orientation="vertical",
        size_hint_y=None,
        height=dp(52),
        padding=(0, 0),
        bg=INPUT_BG,
        border=(0.20, 0.24, 0.30, 1),
        radius=RADIUS_MD,
    )

    owner.search_input = TextInput(
        hint_text="Tüm fonksiyonları görüntüleyebilir ve arayabilirsiniz...",
        multiline=False,
        size_hint=(1, 1),
        background_normal="",
        background_active="",
        background_color=(0, 0, 0, 0),
        foreground_color=TEXT_PRIMARY,
        cursor_color=TEXT_PRIMARY,
        hint_text_color=TEXT_MUTED,
        padding=(dp(12), dp(13)),
        write_tab=False,
        font_size="14sp",
    )
    owner.search_input.bind(text=owner._on_search_text)
    owner.search_wrap.add_widget(owner.search_input)
    owner.add_widget(owner.search_wrap)


def build_table_header_label(owner, text: str, size_hint_x: float) -> Label:
    lbl = Label(
        text=text,
        size_hint_x=size_hint_x,
        color=(0.82, 0.88, 0.98, 1),
        font_size="12sp",
        halign="left",
        valign="middle",
        bold=True,
    )
    lbl.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    return lbl


def build_list_box(owner) -> None:
    owner.list_wrap = Kart(
        orientation="vertical",
        spacing=dp(8),
        size_hint_y=None,
        height=owner._expanded_list_height,
        padding=(dp(10), dp(10)),
        bg=CARD_BG_SOFT,
        border=(0.18, 0.22, 0.28, 1),
        radius=RADIUS_MD,
    )

    owner.list_info_label = Label(
        text="Tüm fonksiyonları görüntüleyebilir ve arayabilirsiniz.",
        size_hint_y=None,
        height=dp(22),
        color=TEXT_MUTED,
        font_size="12sp",
        halign="left",
        valign="middle",
        shorten=True,
        shorten_from="right",
    )
    owner.list_info_label.bind(
        size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
    )
    owner.list_wrap.add_widget(owner.list_info_label)

    owner.table_header = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(30),
        spacing=dp(10),
        padding=(dp(12), 0, dp(12), 0),
    )

    owner.table_header.add_widget(
        owner._ui_kurulumu_yoneticisi.build_table_header_label(owner, "Fonksiyon", 0.46)
    )
    owner.table_header.add_widget(
        owner._ui_kurulumu_yoneticisi.build_table_header_label(owner, "Tür", 0.14)
    )
    owner.table_header.add_widget(
        owner._ui_kurulumu_yoneticisi.build_table_header_label(owner, "Satır", 0.16)
    )
    owner.table_header.add_widget(
        owner._ui_kurulumu_yoneticisi.build_table_header_label(owner, "İmza", 0.24)
    )

    owner.list_wrap.add_widget(owner.table_header)

    owner.scroll = ScrollView(
        do_scroll_x=False,
        do_scroll_y=True,
        bar_width=dp(8),
        scroll_type=["bars", "content"],
        size_hint=(1, 1),
        effect_cls="ScrollEffect",
    )

    owner.container = BoxLayout(
        orientation="vertical",
        spacing=dp(8),
        size_hint_y=None,
    )
    owner.container.bind(minimum_height=owner.container.setter("height"))

    owner.scroll.add_widget(owner.container)
    owner.list_wrap.add_widget(owner.scroll)
    owner.add_widget(owner.list_wrap)


def build_preview_boxes(owner) -> None:
    owner.selected_preview_card = owner._ui_kurulumu_yoneticisi.build_preview_card(
        owner,
        title="Seçilen Kod Önizleme",
        icon_name="visibility_on.png",
    )
    owner.add_widget(owner.selected_preview_card)

    owner.new_preview_card = owner._ui_kurulumu_yoneticisi.build_preview_card(
        owner,
        title="Yeni Kod Önizleme",
        icon_name="edit.png",
    )
    owner.add_widget(owner.new_preview_card)


def build_preview_card(owner, title: str, icon_name: str):
    card = Kart(
        orientation="vertical",
        size_hint_y=None,
        height=dp(122),
        padding=(dp(12), dp(10)),
        spacing=dp(8),
        bg=CARD_BG_DARK,
        border=(0.18, 0.21, 0.27, 1),
        radius=RADIUS_MD,
    )

    head = IconluBaslik(
        text=title,
        icon_name=icon_name,
        height_dp=28,
        font_size="13sp",
        color=TEXT_PRIMARY,
    )
    card.add_widget(head)

    label = Label(
        text="Henüz önizleme yok.",
        color=TEXT_MUTED,
        font_size="13sp",
        halign="left",
        valign="top",
        shorten=False,
    )
    label.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    card.add_widget(label)

    card._preview_label = label
    return card
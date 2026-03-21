# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/render_akisi/render_akisi.py
"""

from __future__ import annotations

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.label import Label


def make_empty_label(owner) -> Label:
    bos = Label(
        text="Gösterilecek fonksiyon yok.",
        size_hint_y=None,
        height=dp(56),
        halign="left",
        valign="middle",
        color=owner._text_muted_color(),
        font_size="13sp",
    )
    bos.bind(
        size=lambda inst, size: setattr(
            inst,
            "text_size",
            (size[0] - dp(8), size[1]),
        )
    )
    return bos


def refresh_trigger(owner, *_args):
    try:
        if owner.container is not None:
            owner.container.height = max(owner.container.minimum_height, dp(1))
            owner.container.do_layout()
    except Exception:
        pass

    try:
        if owner.scroll is not None:
            owner.scroll.do_layout()
    except Exception:
        pass

    try:
        if owner.list_wrap is not None:
            owner.list_wrap.do_layout()
            owner.list_wrap.canvas.ask_update()
    except Exception:
        pass

    try:
        owner.do_layout()
        owner.canvas.ask_update()
    except Exception:
        pass


def render_items(owner, items, keep_scroll: bool = False) -> None:
    print("_render_items CALISTI =", len(items))

    owner.clear_items()
    count = 0

    SatirSinifi = owner._satir_yoneticisi.satir_sinifi()
    print("SATIR SINIFI =", SatirSinifi)

    for item in items:
        count += 1
        is_selected = (
            owner.selected_item is not None
            and owner._item_key(item) == owner._item_key(owner.selected_item)
        )

        row = SatirSinifi(
            item=item,
            on_press_row=owner._select,
            on_error=owner._report_error,
            is_selected=is_selected,
        )
        owner.container.add_widget(row)

    if count == 0:
        owner.container.add_widget(owner._render_akisi_yoneticisi.make_empty_label(owner))

    try:
        owner.container.height = max(owner.container.minimum_height, dp(1))
    except Exception:
        pass

    toplam = len(owner.all_items)
    if owner.count_label is not None:
        owner.count_label.text = f"{count} / {toplam}"

    try:
        owner.container.do_layout()
    except Exception:
        pass

    try:
        if owner.list_wrap is not None:
            owner.list_wrap.do_layout()
    except Exception:
        pass

    try:
        owner.do_layout()
    except Exception:
        pass

    if keep_scroll and owner.selected_item is not None:
        Clock.schedule_once(owner._selected_itemi_gorunur_tut, 0)
    else:
        Clock.schedule_once(owner._scroll_top, 0)

    Clock.schedule_once(owner._refresh_trigger, 0)
    Clock.schedule_once(owner._refresh_trigger, 0.05)


def scroll_top(owner, *_args):
    try:
        if owner.scroll is not None:
            owner.scroll.scroll_y = 1
    except Exception as exc:
        owner._report_error(exc, title="Fonksiyon Listesi Scroll Hatası")


def selected_itemi_gorunur_tut(owner, *_args):
    try:
        if owner.scroll is None:
            return

        if not owner.filtered_items or owner.selected_item is None:
            owner.scroll.scroll_y = 1
            return

        hedef_index = -1
        hedef_key = owner._item_key(owner.selected_item)

        for i, item in enumerate(owner.filtered_items):
            if owner._item_key(item) == hedef_key:
                hedef_index = i
                break

        if hedef_index < 0:
            owner.scroll.scroll_y = 1
            return

        toplam = len(owner.filtered_items)
        if toplam <= 1:
            owner.scroll.scroll_y = 1
            return

        oran = 1.0 - (hedef_index / max(1, toplam - 1))
        owner.scroll.scroll_y = max(0.0, min(1.0, oran))
    except Exception:
        try:
            if owner.scroll is not None:
                owner.scroll.scroll_y = 1
        except Exception:
            pass
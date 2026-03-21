# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/gorunum_akisi/gorunum_akisi.py
"""

from __future__ import annotations

from kivy.clock import Clock


def set_toggle_icon(owner, icon_name: str) -> None:
    if owner.toggle_button is None:
        return

    icon_widget = getattr(owner.toggle_button, "icon", None)
    if icon_widget is None:
        return

    from app.ui.icon_yardimci import icon_path

    yol = icon_path(icon_name)
    if not yol:
        return

    icon_widget.source = yol
    try:
        icon_widget.reload()
    except Exception:
        pass


def update_toggle_icon(owner) -> None:
    if owner.is_list_expanded:
        owner._gorunum_akisi_yoneticisi.set_toggle_icon(owner, "visibility_on.png")
    else:
        owner._gorunum_akisi_yoneticisi.set_toggle_icon(owner, "visibility_off.png")


def toggle_list_visibility(owner, *_args) -> None:
    owner.is_list_expanded = not owner.is_list_expanded
    owner._gorunum_akisi_yoneticisi.sync_list_visibility(owner)
    Clock.schedule_once(owner._scroll_top, 0)
    Clock.schedule_once(owner._refresh_trigger, 0)


def sync_list_visibility(owner) -> None:
    if (
        owner.list_wrap is None
        or owner.list_info_label is None
        or owner.scroll is None
        or owner.table_header is None
    ):
        return

    if owner.is_list_expanded:
        owner.list_wrap.height = owner._expanded_list_height
        owner.list_info_label.text = (
            "Tüm fonksiyonlar geniş listede görüntülenebilir ve aranabilir."
        )
    else:
        owner.list_wrap.height = owner._compact_list_height
        owner.list_info_label.text = (
            "Dar görünüm açık. Yine kaydırarak birkaç fonksiyon görebilirsiniz."
        )

    owner.scroll.disabled = False
    owner.scroll.opacity = 1
    owner.scroll.size_hint_y = 1
    owner.table_header.opacity = 1

    owner._gorunum_akisi_yoneticisi.update_toggle_icon(owner)
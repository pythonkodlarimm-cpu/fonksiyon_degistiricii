# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/render_akisi/render_akisi.py

ROL:
- Fonksiyon listesi panelinin render akışını yönetmek
- Boş liste etiketi üretmek
- Satırları güvenli biçimde oluşturup listeye basmak
- Render sonrası görünüm ve scroll tazelemesini yürütmek
- Seçili öğeyi görünür tutmak
- Aktif dile göre görünür metinleri üretmek

MİMARİ:
- Render akışı burada tutulur
- Üst katman bu modüle doğrudan değil, render_akisi/yoneticisi.py üzerinden erişmelidir
- Satır üretimi doğrudan sınıf çağrısı ile değil, satır yöneticisi üzerinden yapılır
- Görünen metinler owner._m(...) üzerinden çözülür
- Fail-soft yaklaşım korunur

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 3
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.label import Label


def make_empty_label(owner) -> Label:
    bos = Label(
        text=owner._m("function_list_empty", "Gösterilecek fonksiyon yok."),
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
            (max(0, size[0] - dp(8)), size[1]),
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
    try:
        print("_render_items CALISTI =", len(list(items or [])))
    except Exception:
        pass

    owner.clear_items()
    count = 0

    for item in list(items or []):
        try:
            count += 1

            is_selected = (
                owner.selected_item is not None
                and owner._item_key(item) == owner._item_key(owner.selected_item)
            )

            row = owner._satir_yoneticisi.satir_olustur(
                item=item,
                on_press_row=owner._select,
                on_error=owner._report_error,
                is_selected=is_selected,
                services=getattr(owner, "services", None),
            )

            if row is not None and owner.container is not None:
                owner.container.add_widget(row)
        except Exception as exc:
            try:
                owner._report_error(
                    exc,
                    title=owner._m(
                        "function_list_render_error",
                        "Fonksiyon Listesi Render Hatası",
                    ),
                )
            except Exception:
                pass

    if count == 0 and owner.container is not None:
        try:
            owner.container.add_widget(
                owner._render_akisi_yoneticisi.make_empty_label(owner)
            )
        except Exception:
            pass

    try:
        if owner.container is not None:
            owner.container.height = max(owner.container.minimum_height, dp(1))
    except Exception:
        pass

    try:
        owner._refresh_count_label()
    except Exception:
        try:
            toplam = len(owner.all_items or [])
            if owner.count_label is not None:
                text_value = owner._m(
                    "function_count_filtered",
                    "{filtered} / {total} fonksiyon",
                )
                owner.count_label.text = (
                    text_value.replace("{filtered}", str(count))
                    .replace("{total}", str(toplam))
                )
        except Exception:
            pass

    try:
        if owner.container is not None:
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

    try:
        if keep_scroll and owner.selected_item is not None:
            Clock.schedule_once(owner._selected_itemi_gorunur_tut, 0)
        else:
            Clock.schedule_once(owner._scroll_top, 0)
    except Exception:
        pass

    try:
        Clock.schedule_once(owner._refresh_trigger, 0)
        Clock.schedule_once(owner._refresh_trigger, 0.05)
    except Exception:
        pass


def scroll_top(owner, *_args):
    try:
        if owner.scroll is not None:
            owner.scroll.scroll_y = 1
    except Exception as exc:
        try:
            owner._report_error(
                exc,
                title=owner._m(
                    "function_list_scroll_error",
                    "Fonksiyon Listesi Scroll Hatası",
                ),
            )
        except Exception:
            pass


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
            try:
                if owner._item_key(item) == hedef_key:
                    hedef_index = i
                    break
            except Exception:
                continue

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

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi.py

ROL:
- Taranan fonksiyonları listeler
- Arama / filtreleme yapar
- Seçilen fonksiyonu üst katmana bildirir
- Göz ikonu ile listeyi açıp kapatır
- Seçilen kod ve yeni kod için kısa önizleme gösterir

MİMARİ:
- Kendi görselini kendi çizer
- Root sadece veri ve callback verir
- Liste görünürlüğü burada yönetilir
"""

from __future__ import annotations

from typing import Iterable

from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from app.ui.iconlu_baslik import IconluBaslik
from app.ui.iconlu_buton import IconluButon
from app.ui.tema import (
    ACCENT,
    CARD_BG,
    CARD_BG_DARK,
    CARD_BG_SOFT,
    INPUT_BG,
    RADIUS_MD,
    TEXT_MUTED,
    TEXT_PRIMARY,
)


class _PanelKart(BoxLayout):
    def __init__(self, bg=(0.14, 0.14, 0.17, 1), radius=16, **kwargs):
        super().__init__(**kwargs)
        self._bg = tuple(bg)
        self._radius = float(radius)

        with self.canvas.before:
            self._bg_color = Color(*self._bg)
            self._bg_rect = RoundedRectangle(radius=[dp(self._radius)])

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

    def _update_canvas(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size


class FonksiyonListesi(BoxLayout):
    def __init__(self, on_select, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(620),
            **kwargs,
        )

        self.on_select = on_select
        self.all_items = []
        self.filtered_items = []
        self.selected_item = None
        self.is_list_visible = True

        self._selected_preview_text = ""
        self._new_preview_text = ""

        self._build_ui()

    # =========================================================
    # UI
    # =========================================================
    def _build_ui(self) -> None:
        self._build_header_row()
        self._build_search_box()
        self._build_list_box()
        self._build_preview_boxes()
        self._sync_list_visibility()

    def _build_header_row(self) -> None:
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8),
        )

        self.header = IconluBaslik(
            text="Fonksiyonlar",
            icon_name="layers.png",
            height_dp=34,
            font_size="16sp",
            color=TEXT_PRIMARY,
            size_hint_x=1,
        )
        row.add_widget(self.header)

        self.toggle_button = IconluButon(
            text="",
            icon_name="visibility_on.png",
            bg=ACCENT,
            size_hint=(None, None),
            size=(dp(54), dp(54)),
            height_dp=54,
            icon_width_dp=22,
        )
        self.toggle_button.bind(on_release=self._toggle_list_visibility)
        row.add_widget(self.toggle_button)

        self.add_widget(row)

    def _build_search_box(self) -> None:
        self.search_wrap = _PanelKart(
            orientation="vertical",
            size_hint_y=None,
            height=dp(48),
            padding=(0, 0),
            bg=INPUT_BG,
            radius=RADIUS_MD,
        )

        self.search_input = TextInput(
            hint_text="Fonksiyon ara...",
            multiline=False,
            size_hint=(1, 1),
            background_normal="",
            background_active="",
            background_color=(0, 0, 0, 0),
            foreground_color=TEXT_PRIMARY,
            cursor_color=TEXT_PRIMARY,
            hint_text_color=TEXT_MUTED,
            padding=(dp(12), dp(12)),
            write_tab=False,
            font_size="14sp",
        )
        self.search_input.bind(text=self._on_search_text)
        self.search_wrap.add_widget(self.search_input)
        self.add_widget(self.search_wrap)

    def _build_list_box(self) -> None:
        self.list_wrap = _PanelKart(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(230),
            padding=(dp(8), dp(8)),
            bg=CARD_BG_SOFT,
            radius=RADIUS_MD,
        )

        self.list_info_label = Label(
            text="Taranan fonksiyonlar aşağıda listelenir.",
            size_hint_y=None,
            height=dp(20),
            color=TEXT_MUTED,
            font_size="12sp",
            halign="left",
            valign="middle",
            shorten=True,
            shorten_from="right",
        )
        self.list_info_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
        self.list_wrap.add_widget(self.list_info_label)

        self.scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8),
            scroll_type=["bars", "content"],
            size_hint=(1, 1),
        )

        self.container = GridLayout(
            cols=1,
            spacing=dp(8),
            padding=(0, dp(2), 0, dp(2)),
            size_hint_y=None,
        )
        self.container.bind(minimum_height=self.container.setter("height"))

        self.scroll.add_widget(self.container)
        self.list_wrap.add_widget(self.scroll)
        self.add_widget(self.list_wrap)

    def _build_preview_boxes(self) -> None:
        self.selected_preview_card = self._build_preview_card(
            title="Seçilen Kod Önizleme",
            icon_name="visibility_on.png",
        )
        self.add_widget(self.selected_preview_card)

        self.new_preview_card = self._build_preview_card(
            title="Yeni Kod Önizleme",
            icon_name="edit.png",
        )
        self.add_widget(self.new_preview_card)

    def _build_preview_card(self, title: str, icon_name: str):
        card = _PanelKart(
            orientation="vertical",
            size_hint_y=None,
            height=dp(118),
            padding=(dp(12), dp(10)),
            spacing=dp(8),
            bg=CARD_BG_DARK,
            radius=RADIUS_MD,
        )

        head = IconluBaslik(
            text=title,
            icon_name=icon_name,
            height_dp=28,
            font_size="14sp",
            color=TEXT_PRIMARY,
        )
        card.add_widget(head)

        label = Label(
            text="Henüz önizleme yok.",
            color=TEXT_MUTED,
            font_size="13sp",
            halign="left",
            valign="top",
        )
        label.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        card.add_widget(label)

        card._preview_label = label
        return card

    # =========================================================
    # PUBLIC API
    # =========================================================
    def clear_items(self) -> None:
        self.container.clear_widgets()
        self.container.height = dp(1)

    def set_items(self, items: Iterable) -> None:
        onceki_secim = self.selected_item
        self.all_items = list(items or [])
        self.filtered_items = self._apply_filter(self.search_input.text)
        self.selected_item = self._restore_selected_item(onceki_secim)
        self._render_items(self.filtered_items, keep_scroll=False)

    def set_selected_preview(self, text: str) -> None:
        self._selected_preview_text = str(text or "")
        self._selected_preview_card_text_guncelle()

    def set_new_preview(self, text: str) -> None:
        self._new_preview_text = str(text or "")
        self._new_preview_card_text_guncelle()

    # =========================================================
    # PREVIEW
    # =========================================================
    def _preview_from_text(self, text: str, max_lines: int = 5) -> str:
        metin = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
        satirlar = [satir.rstrip() for satir in metin.split("\n")]

        temiz = []
        for satir in satirlar:
            if not temiz and not satir.strip():
                continue
            temiz.append(satir)

        if not temiz:
            return "Henüz önizleme yok."

        out = temiz[:max_lines]
        if len(temiz) > max_lines:
            out.append("...")

        return "\n".join(out)

    def _selected_preview_card_text_guncelle(self) -> None:
        try:
            self.selected_preview_card._preview_label.text = self._preview_from_text(
                self._selected_preview_text,
                max_lines=5,
            )
        except Exception:
            pass

    def _new_preview_card_text_guncelle(self) -> None:
        try:
            self.new_preview_card._preview_label.text = self._preview_from_text(
                self._new_preview_text,
                max_lines=5,
            )
        except Exception:
            pass

    # =========================================================
    # SELECTION
    # =========================================================
    def _item_key(self, item) -> tuple:
        if item is None:
            return ("", "", "", 0, 0)

        return (
            str(getattr(item, "path", "") or ""),
            str(getattr(item, "name", "") or ""),
            str(getattr(item, "kind", "") or ""),
            int(getattr(item, "lineno", 0) or 0),
            int(getattr(item, "end_lineno", 0) or 0),
        )

    def _restore_selected_item(self, old_item):
        if old_item is None:
            return None

        old_key = self._item_key(old_item)

        for item in self.all_items:
            if self._item_key(item) == old_key:
                return item

        old_path = str(getattr(old_item, "path", "") or "")
        old_name = str(getattr(old_item, "name", "") or "")

        for item in self.all_items:
            if (
                str(getattr(item, "path", "") or "") == old_path
                and str(getattr(item, "name", "") or "") == old_name
            ):
                return item

        return None

    # =========================================================
    # SEARCH
    # =========================================================
    def _normalize_query_tokens(self, value: str) -> list[str]:
        q = str(value or "").strip().lower()
        if not q:
            return []
        return [parca for parca in q.split() if parca]

    def _item_search_text(self, item) -> str:
        path = str(getattr(item, "path", "") or "").lower()
        name = str(getattr(item, "name", "") or "").lower()
        kind = str(getattr(item, "kind", "") or "").lower()
        signature = str(getattr(item, "signature", "") or "").lower()
        lineno = str(getattr(item, "lineno", "") or "")
        end_lineno = str(getattr(item, "end_lineno", "") or "")

        alanlar = [
            path,
            name,
            kind,
            signature,
            lineno,
            end_lineno,
            f"{lineno}-{end_lineno}",
            f"satır {lineno}-{end_lineno}",
            f"satir {lineno}-{end_lineno}",
        ]
        return " | ".join(alanlar)

    def _item_matches_query(self, item, tokens: list[str]) -> bool:
        if not tokens:
            return True

        haystack = self._item_search_text(item)
        return all(token in haystack for token in tokens)

    def _apply_filter(self, value: str):
        tokens = self._normalize_query_tokens(value)
        if not tokens:
            return list(self.all_items)

        filtered = []
        for item in self.all_items:
            if self._item_matches_query(item, tokens):
                filtered.append(item)
        return filtered

    # =========================================================
    # RENDER
    # =========================================================
    def _button_text(self, item) -> str:
        path = str(getattr(item, "path", "") or "")
        kind = str(getattr(item, "kind", "") or "")
        lineno = int(getattr(item, "lineno", 0) or 0)
        end_lineno = int(getattr(item, "end_lineno", 0) or 0)
        signature = str(getattr(item, "signature", "") or "").strip()

        satir = f"{kind}  •  Satır: {lineno}-{end_lineno}"

        if signature:
            return f"{path}\n{satir}\n{signature}"
        return f"{path}\n{satir}"

    def _button_height(self, item) -> float:
        signature = str(getattr(item, "signature", "") or "").strip()
        if signature:
            return dp(92)
        return dp(72)

    def _make_item_button(self, item, is_selected: bool) -> Button:
        btn = Button(
            text=self._button_text(item),
            size_hint_y=None,
            height=self._button_height(item),
            halign="left",
            valign="middle",
            background_normal="",
            background_down="",
            background_color=(0.20, 0.34, 0.52, 1) if is_selected else CARD_BG,
            color=TEXT_PRIMARY,
            font_size="13sp",
            bold=False,
        )
        btn.bind(size=self._sync_text_size)
        btn.bind(on_release=lambda _btn, current=item: self._select(current))
        return btn

    def _make_empty_label(self) -> Label:
        bos = Label(
            text="Gösterilecek fonksiyon yok.",
            size_hint_y=None,
            height=dp(56),
            halign="left",
            valign="middle",
            color=TEXT_MUTED,
            font_size="13sp",
        )
        bos.bind(size=self._sync_label_size)
        return bos

    def _render_items(self, items, keep_scroll: bool = False) -> None:
        self.clear_items()
        count = 0

        if self.is_list_visible:
            for item in items:
                count += 1
                is_selected = (
                    self.selected_item is not None
                    and self._item_key(item) == self._item_key(self.selected_item)
                )
                self.container.add_widget(self._make_item_button(item, is_selected))

            if count == 0:
                self.container.add_widget(self._make_empty_label())

        toplam = len(self.all_items)
        self.header.set_text(f"Fonksiyonlar ({count}/{toplam})")

        if self.is_list_visible:
            if keep_scroll and self.selected_item is not None:
                Clock.schedule_once(self._selected_itemi_gorunur_tut, 0)
            else:
                Clock.schedule_once(self._scroll_top, 0)

    def _sync_text_size(self, widget, size):
        widget.text_size = (size[0] - dp(18), size[1] - dp(12))

    def _sync_label_size(self, widget, size):
        widget.text_size = (size[0] - dp(8), size[1])

    def _scroll_top(self, *_args):
        try:
            self.scroll.scroll_y = 1
        except Exception:
            pass

    def _selected_itemi_gorunur_tut(self, *_args):
        try:
            if not self.filtered_items or self.selected_item is None:
                self.scroll.scroll_y = 1
                return

            hedef_index = -1
            hedef_key = self._item_key(self.selected_item)

            for i, item in enumerate(self.filtered_items):
                if self._item_key(item) == hedef_key:
                    hedef_index = i
                    break

            if hedef_index < 0:
                self.scroll.scroll_y = 1
                return

            toplam = len(self.filtered_items)
            if toplam <= 1:
                self.scroll.scroll_y = 1
                return

            oran = 1.0 - (hedef_index / max(1, toplam - 1))
            self.scroll.scroll_y = max(0.0, min(1.0, oran))
        except Exception:
            try:
                self.scroll.scroll_y = 1
            except Exception:
                pass

    # =========================================================
    # VISIBILITY
    # =========================================================
    def _toggle_list_visibility(self, *_args):
        self.is_list_visible = not self.is_list_visible
        self._sync_list_visibility()
        self._render_items(self.filtered_items, keep_scroll=False)

    def _sync_list_visibility(self) -> None:
        if self.is_list_visible:
            self.list_wrap.height = dp(230)
            self.list_info_label.text = "Taranan fonksiyonlar aşağıda listelenir."
            self.scroll.disabled = False
            self.scroll.opacity = 1
            try:
                self.toggle_button.set_colors(bg=ACCENT)
            except Exception:
                pass
        else:
            self.list_wrap.height = dp(52)
            self.list_info_label.text = "Liste kapalı. Göz ikonuna basarak aç."
            self.scroll.disabled = True
            self.scroll.opacity = 0
            try:
                self.toggle_button.set_colors(bg=CARD_BG)
            except Exception:
                pass

    # =========================================================
    # EVENTS
    # =========================================================
    def _select(self, item) -> None:
        self.selected_item = item
        self._render_items(self.filtered_items, keep_scroll=True)

        try:
            self.set_selected_preview(str(getattr(item, "source", "") or ""))
        except Exception:
            pass

        if self.on_select:
            self.on_select(item)

    def _on_search_text(self, _instance, value: str) -> None:
        self.filtered_items = self._apply_filter(value)
        self._render_items(self.filtered_items, keep_scroll=True)
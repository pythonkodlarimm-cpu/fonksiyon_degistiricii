# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi.py

ROL:
- Taranan fonksiyonları listeler
- Arama / filtreleme yapar
- Seçilen fonksiyonu üst katmana bildirir
- Göz ikonu ile listeyi geniş / dar görünüm arasında değiştirir
- Seçilen kod ve yeni kod için kısa önizleme gösterir

MİMARİ:
- Kendi görselini kendi çizer
- Root sadece veri ve callback verir
- Liste görünürlüğü burada yönetilir
- Üst aksiyon alanında icon_toolbar kullanılır

API 34 UYUMLULUK NOTU:
- Bu dosya doğrudan Android API çağrısı yapmaz
- Kivy tabanlı liste ve arama akışı platform bağımsızdır
- Büyük liste / dar liste davranışı güvenli şekilde yönetilir

SURUM: 10
TARIH: 2026-03-17
IMZA: FY.
"""

from __future__ import annotations

from typing import Iterable

from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from app.ui.icon_toolbar import IconToolbar
from app.ui.iconlu_baslik import IconluBaslik
from app.ui.kart import Kart
from app.ui.tema import (
    CARD_BG,
    CARD_BG_DARK,
    CARD_BG_SOFT,
    INPUT_BG,
    RADIUS_MD,
    TEXT_MUTED,
    TEXT_PRIMARY,
)


class FonksiyonSatiri(ButtonBehavior, BoxLayout):
    def __init__(self, item, on_press_row, is_selected=False, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(78),
            padding=(dp(12), dp(10)),
            spacing=dp(10),
            **kwargs,
        )

        self.item = item
        self.on_press_row = on_press_row
        self.is_selected = bool(is_selected)

        with self.canvas.before:
            self._bg_color = Color(*(self._selected_bg() if self.is_selected else self._normal_bg()))
            self._bg_rect = RoundedRectangle(radius=[dp(RADIUS_MD)])

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

        self._build_ui()

    def _normal_bg(self):
        return CARD_BG

    def _selected_bg(self):
        return (0.20, 0.34, 0.52, 1)

    def _pressed_bg(self):
        if self.is_selected:
            return (0.24, 0.40, 0.60, 1)
        return (0.24, 0.28, 0.36, 1)

    def _update_canvas(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _bind_label_size(self, label: Label):
        label.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        return label

    def _safe_text(self, value, default="-") -> str:
        metin = str(value or "").strip()
        return metin if metin else default

    def _short_text(self, value: str, limit: int) -> str:
        metin = self._safe_text(value, "-")
        if len(metin) <= limit:
            return metin
        if limit <= 3:
            return metin[:limit]
        return metin[: limit - 3] + "..."

    def _display_name(self) -> str:
        qualified_name = str(getattr(self.item, "qualified_name", "") or "").strip()
        if qualified_name:
            return qualified_name
        return str(getattr(self.item, "name", "") or "-")

    def _kind_text(self) -> str:
        kind = str(getattr(self.item, "kind", "") or "").strip()
        if not kind:
            return "-"
        if kind == "function":
            return "func"
        return kind

    def _line_text(self) -> str:
        start = int(getattr(self.item, "lineno", 0) or 0)
        end = int(getattr(self.item, "end_lineno", 0) or 0)
        if start > 0 and end > 0:
            return f"{start}-{end}"
        if start > 0:
            return str(start)
        return "-"

    def _signature_text(self) -> str:
        signature = str(getattr(self.item, "signature", "") or "").strip()
        if signature:
            return self._short_text(signature, 22)

        name = str(getattr(self.item, "name", "") or "").strip()
        if name:
            return self._short_text(f"def {name}(...) ", 22).strip()

        return "-"

    def _build_ui(self):
        ad = self._bind_label_size(
            Label(
                text=self._short_text(self._display_name(), 22),
                size_hint_x=0.46,
                color=TEXT_PRIMARY,
                font_size="14sp",
                halign="left",
                valign="middle",
                shorten=True,
                shorten_from="right",
                max_lines=2,
            )
        )
        self.add_widget(ad)

        tur = self._bind_label_size(
            Label(
                text=self._kind_text(),
                size_hint_x=0.14,
                color=(0.84, 0.88, 0.96, 1),
                font_size="13sp",
                halign="center",
                valign="middle",
                shorten=True,
                shorten_from="right",
                max_lines=1,
            )
        )
        self.add_widget(tur)

        satir = self._bind_label_size(
            Label(
                text=self._line_text(),
                size_hint_x=0.16,
                color=(0.88, 0.92, 1, 1),
                font_size="13sp",
                halign="center",
                valign="middle",
                max_lines=1,
            )
        )
        self.add_widget(satir)

        imza = self._bind_label_size(
            Label(
                text=self._signature_text(),
                size_hint_x=0.24,
                color=TEXT_MUTED,
                font_size="12sp",
                halign="left",
                valign="middle",
                shorten=True,
                shorten_from="right",
                max_lines=2,
            )
        )
        self.add_widget(imza)

    def set_selected_state(self, is_selected: bool) -> None:
        self.is_selected = bool(is_selected)
        try:
            self._bg_color.rgba = self._selected_bg() if self.is_selected else self._normal_bg()
        except Exception:
            pass

    def on_press(self):
        try:
            self._bg_color.rgba = self._pressed_bg()
        except Exception:
            pass
        return super().on_press()

    def on_release(self):
        try:
            self._bg_color.rgba = self._selected_bg() if self.is_selected else self._normal_bg()
        except Exception:
            pass

        try:
            if self.on_press_row:
                self.on_press_row(self.item)
        except Exception:
            pass

        return super().on_release()


class FonksiyonListesi(BoxLayout):
    def __init__(self, on_select, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(760),
            **kwargs,
        )

        self.on_select = on_select
        self.all_items = []
        self.filtered_items = []
        self.selected_item = None
        self.is_list_expanded = True

        self._selected_preview_text = ""
        self._new_preview_text = ""

        self._expanded_list_height = dp(360)
        self._compact_list_height = dp(212)

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
        self._selected_preview_card_text_guncelle()
        self._new_preview_card_text_guncelle()
        self._render_items([], keep_scroll=False)

    def _build_header_row(self) -> None:
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(42),
            spacing=dp(8),
        )

        self.header = IconluBaslik(
            text="Fonksiyonlar",
            icon_name="layers.png",
            height_dp=32,
            font_size="16sp",
            color=TEXT_PRIMARY,
            size_hint_x=1,
        )
        row.add_widget(self.header)

        self.count_label = Label(
            text="0 / 0",
            size_hint_x=None,
            width=dp(84),
            color=TEXT_MUTED,
            font_size="13sp",
            halign="right",
            valign="middle",
        )
        self.count_label.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        row.add_widget(self.count_label)

        self.add_widget(row)

        self.header_toolbar = IconToolbar(
            spacing_dp=12,
            padding_dp=2,
        )

        self.toggle_button = self.header_toolbar.add_tool(
            icon_name="visibility_on.png",
            text="Liste",
            on_release=self._toggle_list_visibility,
            icon_size_dp=32,
            text_size="10sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )
        self.add_widget(self.header_toolbar)

    def _build_search_box(self) -> None:
        self.search_wrap = Kart(
            orientation="vertical",
            size_hint_y=None,
            height=dp(52),
            padding=(0, 0),
            bg=INPUT_BG,
            border=(0.20, 0.24, 0.30, 1),
            radius=RADIUS_MD,
        )

        self.search_input = TextInput(
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
        self.search_input.bind(text=self._on_search_text)
        self.search_wrap.add_widget(self.search_input)
        self.add_widget(self.search_wrap)

    def _build_table_header_label(self, text: str, size_hint_x: float) -> Label:
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

    def _build_list_box(self) -> None:
        self.list_wrap = Kart(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=self._expanded_list_height,
            padding=(dp(10), dp(10)),
            bg=CARD_BG_SOFT,
            border=(0.18, 0.22, 0.28, 1),
            radius=RADIUS_MD,
        )

        self.list_info_label = Label(
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
        self.list_info_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
        self.list_wrap.add_widget(self.list_info_label)

        self.table_header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(30),
            spacing=dp(10),
            padding=(dp(12), 0, dp(12), 0),
        )

        self.table_header.add_widget(self._build_table_header_label("Fonksiyon", 0.46))
        self.table_header.add_widget(self._build_table_header_label("Tür", 0.14))
        self.table_header.add_widget(self._build_table_header_label("Satır", 0.16))
        self.table_header.add_widget(self._build_table_header_label("İmza", 0.24))

        self.list_wrap.add_widget(self.table_header)

        self.scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8),
            scroll_type=["bars", "content"],
            size_hint=(1, 1),
            effect_cls="ScrollEffect",
        )

        self.container = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
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

    # =========================================================
    # PUBLIC API
    # =========================================================
    def clear_items(self) -> None:
        try:
            self.container.clear_widgets()
            self.container.height = dp(1)
        except Exception:
            pass

    def clear_selection(self) -> None:
        self.selected_item = None
        self.set_selected_preview("")

    def clear_new_preview(self) -> None:
        self.set_new_preview("")

    def clear_all(self) -> None:
        self.selected_item = None
        self.all_items = []
        self.filtered_items = []

        try:
            self.search_input.text = ""
        except Exception:
            pass

        self.clear_items()
        self.set_selected_preview("")
        self.set_new_preview("")
        self._render_items([], keep_scroll=False)

    def set_items(self, items: Iterable) -> None:
        yeni_items = list(items or [])
        onceki_secim = self.selected_item

        self.all_items = yeni_items
        self.filtered_items = self._apply_filter(self.search_input.text)

        if not self.all_items:
            self.selected_item = None
        else:
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
        qualified_name = str(getattr(item, "qualified_name", "") or "").lower()
        parent_name = str(getattr(item, "parent_name", "") or "").lower()
        lineno = str(getattr(item, "lineno", "") or "")
        end_lineno = str(getattr(item, "end_lineno", "") or "")

        alanlar = [
            path,
            name,
            kind,
            signature,
            qualified_name,
            parent_name,
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
        bos.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0] - dp(8), size[1])))
        return bos

    def _render_items(self, items, keep_scroll: bool = False) -> None:
        self.clear_items()
        count = 0

        for item in items:
            count += 1
            is_selected = (
                self.selected_item is not None
                and self._item_key(item) == self._item_key(self.selected_item)
            )

            row = FonksiyonSatiri(
                item=item,
                on_press_row=self._select,
                is_selected=is_selected,
            )
            self.container.add_widget(row)

        if count == 0:
            self.container.add_widget(self._make_empty_label())

        toplam = len(self.all_items)
        self.count_label.text = f"{count} / {toplam}"

        if keep_scroll and self.selected_item is not None:
            Clock.schedule_once(self._selected_itemi_gorunur_tut, 0)
        else:
            Clock.schedule_once(self._scroll_top, 0)

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
    def _set_toggle_icon(self, icon_name: str) -> None:
        try:
            self.toggle_button.icon.source = self.toggle_button.icon.source.replace(
                "visibility_on.png",
                icon_name,
            ).replace(
                "visibility_off.png",
                icon_name,
            )
            self.toggle_button.icon.reload()
        except Exception:
            pass

    def _update_toggle_icon(self) -> None:
        if self.is_list_expanded:
            self._set_toggle_icon("visibility_on.png")
        else:
            self._set_toggle_icon("visibility_off.png")

    def _toggle_list_visibility(self, *_args):
        self.is_list_expanded = not self.is_list_expanded
        self._sync_list_visibility()
        Clock.schedule_once(self._scroll_top, 0)

    def _sync_list_visibility(self) -> None:
        if self.is_list_expanded:
            self.list_wrap.height = self._expanded_list_height
            self.list_info_label.text = "Tüm fonksiyonlar geniş listede görüntülenebilir ve aranabilir."
        else:
            self.list_wrap.height = self._compact_list_height
            self.list_info_label.text = "Dar görünüm açık. Yine kaydırarak birkaç fonksiyon görebilirsiniz."

        self.scroll.disabled = False
        self.scroll.opacity = 1
        self.scroll.size_hint_y = 1
        self.table_header.opacity = 1

        self._update_toggle_icon()

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

        try:
            if self.on_select:
                self.on_select(item)
        except Exception:
            pass

    def _on_search_text(self, _instance, value: str) -> None:
        self.filtered_items = self._apply_filter(value)

        if self.selected_item is not None:
            hedef = None
            secim_key = self._item_key(self.selected_item)
            for item in self.filtered_items:
                if self._item_key(item) == secim_key:
                    hedef = item
                    break
            self.selected_item = hedef

        self._render_items(self.filtered_items, keep_scroll=True)

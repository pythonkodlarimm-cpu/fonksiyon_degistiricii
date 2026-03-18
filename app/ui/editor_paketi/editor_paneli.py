# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/editor_paneli.py

SURUM: 24
TARIH: 2026-03-18
IMZA: FY.
"""

from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout

from app.ui.icon_toolbar import IconToolbar
from app.ui.iconlu_baslik import IconluBaslik
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY
from app.ui.editor_paketi.editor_aksiyonlari import (
    check_new_code,
    clear_new_code,
    copy_current_to_new,
    handle_restore,
    handle_update,
)
from app.ui.editor_paketi.editor_bilesenleri import BilgiKutusu, SadeKodAlani
from app.ui.editor_paketi.editor_bildirimleri import EditorAksiyonBildirimi
from app.ui.editor_paketi.editor_dogrulama import normalize_code_text
from app.ui.editor_paketi.editor_popup_lari import (
    open_current_code_popup,
    open_new_code_editor_popup,
)
from app.ui.editor_paketi.editor_yardimcilari import (
    close_popups,
    set_status_info,
    set_status_warning,
    set_status_error,
    set_status_success,
)


class EditorPaneli(BoxLayout):
    def __init__(self, on_update=None, on_restore=None, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(10), **kwargs)

        self.on_update = on_update
        self.on_restore = on_restore
        self.current_item = None
        self._new_code_buffer = ""
        self._current_popup = None
        self._editor_popup = None

        self._build_ui()
        self._set_status_info("Hazır.", 0)

    def _build_ui(self) -> None:
        self.path_label = IconluBaslik(
            text="Seçili fonksiyon: -",
            icon_name="edit.png",
            height_dp=38,
            font_size="16sp",
            color=TEXT_PRIMARY,
        )
        self.path_label.size_hint_y = None
        self.path_label.height = dp(38)
        self.add_widget(self.path_label)

        self.error_box = BilgiKutusu()
        self.add_widget(self.error_box)

        self.add_widget(
            self._build_title_row(
                title="Mevcut Kod",
                icon_name="visibility_on.png",
                action_icon="visibility_on.png",
                action_text="Aç",
                callback=self._open_current_code_popup,
            )
        )

        self.current_code_area = SadeKodAlani(readonly=True, size_hint_y=0.34)
        self.add_widget(self.current_code_area)

        self.add_widget(
            self._build_title_row(
                title="Yeni Fonksiyon Kodu",
                icon_name="edit.png",
                action_icon="edit.png",
                action_text="Düzenle",
                callback=self._open_new_code_editor_popup,
            )
        )

        self.inline_notice = EditorAksiyonBildirimi()
        self.add_widget(self.inline_notice)

        self.new_code_area = SadeKodAlani(
            readonly=False,
            hint_text="Tam fonksiyon kodunu buraya yaz veya yapıştır.",
            size_hint_y=0.66,
        )
        self.add_widget(self.new_code_area)

        self._build_action_toolbar()

    def _build_title_row(self, title: str, icon_name: str, action_icon: str, action_text: str, callback):
        wrap = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(78),
            spacing=dp(4),
        )

        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(38),
            spacing=dp(8),
        )
        row.add_widget(
            IconluBaslik(
                text=title,
                icon_name=icon_name,
                height_dp=34,
                font_size="15sp",
                color=(0.80, 0.89, 1, 1),
                size_hint_x=1,
            )
        )
        wrap.add_widget(row)

        toolbar = IconToolbar(spacing_dp=12, padding_dp=0)
        toolbar.size_hint_y = None
        toolbar.height = dp(36)
        toolbar.add_tool(
            icon_name=action_icon,
            text=action_text,
            on_release=callback,
            icon_size_dp=34,
            text_size="11sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )
        wrap.add_widget(toolbar)
        return wrap

    def _build_action_toolbar(self) -> None:
        self.action_toolbar = IconToolbar(spacing_dp=22, padding_dp=6)
        self.action_toolbar.size_hint_y = None
        self.action_toolbar.height = dp(84)

        self.action_toolbar.add_tool(
            icon_name="clear.png",
            text="Temizle",
            on_release=self._clear_new_code,
            icon_size_dp=42,
            text_size="12sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.action_toolbar.add_tool(
            icon_name="upload.png",
            text="Güncelle",
            on_release=self._handle_update,
            icon_size_dp=42,
            text_size="12sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.action_toolbar.add_tool(
            icon_name="code_check.png",
            text="Kontrol Et",
            on_release=self._check_new_code,
            icon_size_dp=42,
            text_size="11sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.action_toolbar.add_tool(
            icon_name="file_copy.png",
            text="Kopyala",
            on_release=self._copy_current_to_new,
            icon_size_dp=42,
            text_size="12sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.action_toolbar.add_tool(
            icon_name="geri_yukle.png",
            text="Geri Yükle",
            on_release=self._handle_restore,
            icon_size_dp=42,
            text_size="11sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.add_widget(self.action_toolbar)

    def clear_selection(self) -> None:
        self.set_item(None)

    def clear_all(self) -> None:
        close_popups(self)
        self.current_item = None
        self._new_code_buffer = ""
        self.path_label.set_text("Seçili fonksiyon: -")
        self.current_code_area.text = ""
        self.new_code_area.text = ""
        self.inline_notice.hide_immediately()
        self._set_status_info("Hazır.", 0)

    def set_new_code_text(self, text: str) -> None:
        self._set_new_code(text)

    def _set_status_info(self, message="", line_no=0):
        set_status_info(self, message, line_no)

    def _set_status_warning(self, message="", line_no=0):
        set_status_warning(self, message, line_no)

    def _set_status_error(self, message="", line_no=0):
        set_status_error(self, message, line_no)

    def _set_status_success(self, message="", line_no=0):
        set_status_success(self, message, line_no)

    def _set_new_code(self, text) -> None:
        metin = normalize_code_text(text, trim_outer_blank_lines=True)
        self._new_code_buffer = metin
        self.new_code_area.text = metin
        self.new_code_area.scroll_to_top()

    def set_item(self, item) -> None:
        onceki_path = str(getattr(self.current_item, "path", "") or "")
        yeni_path = str(getattr(item, "path", "") or "")

        self.current_item = item
        self.inline_notice.hide_immediately()
        self._set_status_info("Hazır.", 0)

        if item is None:
            close_popups(self)
            self.path_label.set_text("Seçili fonksiyon: -")
            self.current_code_area.text = ""
            self.new_code_area.text = ""
            self._new_code_buffer = ""
            return

        self.path_label.set_text(f"Seçili fonksiyon: {getattr(item, 'path', '-')}")
        self.current_code_area.text = normalize_code_text(
            getattr(item, "source", ""),
            trim_outer_blank_lines=True,
        )
        self.current_code_area.scroll_to_top()

        if onceki_path != yeni_path:
            self._new_code_buffer = ""

        self.new_code_area.text = (
            normalize_code_text(self._new_code_buffer, trim_outer_blank_lines=True)
            if self._new_code_buffer.strip()
            else ""
        )
        self.new_code_area.scroll_to_top()

    def _copy_current_to_new(self, *_args):
        return copy_current_to_new(self, *_args)

    def _clear_new_code(self, *_args):
        return clear_new_code(self, *_args)

    def _check_new_code(self, *_args):
        return check_new_code(self, *_args)

    def _handle_update(self, *_args):
        return handle_update(self, *_args)

    def _handle_restore(self, *_args):
        return handle_restore(self, *_args)

    def _open_current_code_popup(self, *_args):
        return open_current_code_popup(self, *_args)

    def _open_new_code_editor_popup(self, *_args):
        return open_new_code_editor_popup(self, *_args)
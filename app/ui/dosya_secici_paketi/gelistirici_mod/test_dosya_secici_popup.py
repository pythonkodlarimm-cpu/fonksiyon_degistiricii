# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/gelistirici_mod/test_dosya_secici_popup.py
"""

from __future__ import annotations

from pathlib import Path

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY


class TestDosyaSeciciPopup(Popup):
    def __init__(self, on_select=None, start_dir: str | None = None, **kwargs):
        super().__init__(**kwargs)

        self.title = ""
        self.separator_height = 0
        self.auto_dismiss = True
        self.size_hint = (0.94, 0.86)

        self.on_select = on_select
        self.current_dir = self._resolve_start_dir(start_dir)

        self.path_label = None
        self.up_button = None
        self.refresh_button = None
        self.scroll = None
        self.list_box = None

        self.content = self._build_content()
        self._refresh_list()

    def _resolve_start_dir(self, start_dir: str | None) -> Path:
        try:
            if start_dir:
                aday = Path(str(start_dir).strip()).expanduser()
                if aday.exists() and aday.is_dir():
                    return aday
        except Exception:
            pass

        try:
            return Path.cwd()
        except Exception:
            return Path(".")

    def _build_content(self):
        root = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=(dp(12), dp(12), dp(12), dp(12)),
        )

        title = Label(
            text="Test Dosya Seçici",
            color=TEXT_PRIMARY,
            font_size="18sp",
            bold=True,
            size_hint_y=None,
            height=dp(28),
            halign="center",
            valign="middle",
        )
        title.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        root.add_widget(title)

        self.path_label = Label(
            text="",
            color=TEXT_MUTED,
            font_size="11sp",
            size_hint_y=None,
            height=dp(36),
            halign="center",
            valign="middle",
            shorten=True,
            shorten_from="left",
        )
        self.path_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
        root.add_widget(self.path_label)

        top_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(42),
            spacing=dp(8),
        )

        self.up_button = Button(
            text="Yukarı",
            background_normal="",
            background_down="",
            background_color=(0.18, 0.18, 0.22, 1),
            color=(1, 1, 1, 1),
        )
        self.up_button.bind(on_release=lambda *_: self._go_up())
        top_row.add_widget(self.up_button)

        self.refresh_button = Button(
            text="Yenile",
            background_normal="",
            background_down="",
            background_color=(0.18, 0.28, 0.40, 1),
            color=(1, 1, 1, 1),
        )
        self.refresh_button.bind(on_release=lambda *_: self._refresh_list())
        top_row.add_widget(self.refresh_button)

        root.add_widget(top_row)

        self.scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8),
        )

        self.list_box = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
        )
        self.list_box.bind(minimum_height=self.list_box.setter("height"))

        self.scroll.add_widget(self.list_box)
        root.add_widget(self.scroll)

        return root

    def _safe_iterdir(self):
        try:
            entries = list(self.current_dir.iterdir())
        except Exception:
            return [], []

        klasorler = []
        dosyalar = []

        for entry in entries:
            try:
                if entry.is_dir():
                    klasorler.append(entry)
                elif entry.is_file() and entry.suffix.lower() == ".py":
                    dosyalar.append(entry)
            except Exception:
                pass

        klasorler.sort(key=lambda p: p.name.lower())
        dosyalar.sort(key=lambda p: p.name.lower())
        return klasorler, dosyalar

    def _refresh_list(self):
        try:
            self.path_label.text = str(self.current_dir)
        except Exception:
            if self.path_label is not None:
                self.path_label.text = "Klasör okunamadı"

        try:
            self.list_box.clear_widgets()
        except Exception:
            pass

        klasorler, dosyalar = self._safe_iterdir()

        if not klasorler and not dosyalar:
            bos = Label(
                text="Gösterilecek .py dosyası veya klasör bulunamadı.",
                color=TEXT_MUTED,
                size_hint_y=None,
                height=dp(42),
                halign="center",
                valign="middle",
            )
            bos.bind(size=lambda inst, size: setattr(inst, "text_size", size))
            self.list_box.add_widget(bos)
            return

        for klasor in klasorler:
            btn = Button(
                text=f"[Klasör] {klasor.name}",
                size_hint_y=None,
                height=dp(46),
                background_normal="",
                background_down="",
                background_color=(0.18, 0.22, 0.28, 1),
                color=(1, 1, 1, 1),
                halign="left",
                valign="middle",
            )
            btn.bind(
                size=lambda inst, size: setattr(inst, "text_size", (size[0] - dp(16), size[1]))
            )
            btn.bind(on_release=lambda *_args, p=klasor: self._open_dir(p))
            self.list_box.add_widget(btn)

        for dosya in dosyalar:
            btn = Button(
                text=dosya.name,
                size_hint_y=None,
                height=dp(46),
                background_normal="",
                background_down="",
                background_color=(0.16, 0.30, 0.20, 1),
                color=(1, 1, 1, 1),
                halign="left",
                valign="middle",
            )
            btn.bind(
                size=lambda inst, size: setattr(inst, "text_size", (size[0] - dp(16), size[1]))
            )
            btn.bind(on_release=lambda *_args, p=dosya: self._select_file(p))
            self.list_box.add_widget(btn)

    def _open_dir(self, path: Path):
        try:
            if path.exists() and path.is_dir():
                self.current_dir = path
        except Exception:
            pass
        self._refresh_list()

    def _go_up(self):
        try:
            parent = self.current_dir.parent
            if parent != self.current_dir and parent.exists():
                self.current_dir = parent
        except Exception:
            pass
        self._refresh_list()

    def _select_file(self, path: Path):
        try:
            if self.on_select is not None:
                self.on_select(str(path))
        finally:
            try:
                self.dismiss()
            except Exception:
                pass
# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ayarlar_popup.py

ROL:
- Kullanıcının uygulama dilini seçmesini sağlar
"""

from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner

from app.i18n.dil_yoneticisi import dil_yoneticisi, t


class AyarlarPopup(Popup):
    def __init__(self, on_saved=None, **kwargs):
        super().__init__(**kwargs)

        self.on_saved = on_saved

        self.title = t("settings_title")
        self.size_hint = (0.88, 0.42)
        self.separator_height = dp(1)

        root = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(12),
        )

        self.language_spinner = Spinner(
            text=dil_yoneticisi.language_label(dil_yoneticisi.get_language()),
            values=(
                t("language_turkish"),
                t("language_english"),
            ),
            size_hint_y=None,
            height=dp(48),
        )

        btn_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48),
        )

        btn_save = Button(
            text=t("save"),
        )
        btn_cancel = Button(
            text=t("cancel"),
        )

        btn_save.bind(on_release=self._save)
        btn_cancel.bind(on_release=lambda *_: self.dismiss())

        btn_row.add_widget(btn_save)
        btn_row.add_widget(btn_cancel)

        root.add_widget(self.language_spinner)
        root.add_widget(btn_row)

        self.content = root

    def _selected_language_code(self) -> str:
        text = str(self.language_spinner.text or "").strip()

        if text == t("language_english"):
            return "en"

        return "tr"

    def _save(self, *_args):
        code = self._selected_language_code()
        dil_yoneticisi.set_language(code, save=True)

        if self.on_saved:
            try:
                self.on_saved(code)
            except Exception:
                pass

        self.dismiss()
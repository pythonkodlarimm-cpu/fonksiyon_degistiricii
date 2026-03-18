# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/test_dosya_secici.py

ROL:
- Geliştirme modunda test amaçlı yerel .py dosyası seçmek
- Popup üzerinden hızlı seçim yapmak
- Seçilen dosya yolunu callback ile üst katmana iletmek

NOT:
- Bu bileşen yalnızca test/geliştirme amaçlıdır
- APK içindeki normal picker akışının yerine geçmez
"""

from __future__ import annotations

from pathlib import Path

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.popup import Popup


class TestDosyaSeciciPopup(Popup):
    def __init__(self, on_select=None, **kwargs):
        super().__init__(**kwargs)

        self.on_select = on_select
        self.title = "Test Dosya Seç"
        self.size_hint = (0.95, 0.95)
        self.auto_dismiss = False
        self.separator_height = dp(1)

        self.chooser = None
        self.path_label = None

        self._build_ui()

    # =========================================================
    # DEBUG
    # =========================================================
    def _debug(self, message: str) -> None:
        try:
            print("[TEST_DOSYA_SECICI]", str(message))
        except Exception:
            pass

    # =========================================================
    # HELPERS
    # =========================================================
    def _initial_path(self) -> str:
        adaylar = [
            Path.cwd(),
            Path("/storage/emulated/0"),
            Path.home(),
        ]

        for aday in adaylar:
            try:
                if aday.exists() and aday.is_dir():
                    return str(aday)
            except Exception:
                pass

        return "."

    # =========================================================
    # UI
    # =========================================================
    def _build_ui(self) -> None:
        root = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(10),
        )

        self.path_label = Label(
            text="Python test dosyası seçin",
            size_hint_y=None,
            height=dp(26),
            halign="left",
            valign="middle",
            font_size="13sp",
        )
        self.path_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], size[1]))
        )
        root.add_widget(self.path_label)

        self.chooser = FileChooserListView(
            path=self._initial_path(),
            filters=["*.py"],
            dirselect=False,
        )
        self.chooser.bind(path=self._on_path_changed)
        self.chooser.bind(selection=self._on_selection_changed)
        root.add_widget(self.chooser)

        alt = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=dp(8),
        )

        btn_iptal = Button(
            text="İptal",
            size_hint_x=0.4,
        )
        btn_iptal.bind(on_release=lambda *_: self.dismiss())

        btn_sec = Button(
            text="Seç",
            size_hint_x=0.6,
        )
        btn_sec.bind(on_release=self._sec)

        alt.add_widget(btn_iptal)
        alt.add_widget(btn_sec)

        root.add_widget(alt)
        self.content = root

        try:
            self._path_label_guncelle()
        except Exception:
            pass

    # =========================================================
    # LABEL
    # =========================================================
    def _path_label_guncelle(self) -> None:
        try:
            mevcut_yol = str(getattr(self.chooser, "path", "") or "").strip()
        except Exception:
            mevcut_yol = ""

        try:
            secim = getattr(self.chooser, "selection", []) or []
            if secim:
                secili = str(secim[0] or "").strip()
                if secili:
                    self.path_label.text = f"Seçili: {secili}"
                    return
        except Exception:
            pass

        self.path_label.text = f"Klasör: {mevcut_yol}" if mevcut_yol else "Python test dosyası seçin"

    # =========================================================
    # EVENTS
    # =========================================================
    def _on_path_changed(self, *_args) -> None:
        self._path_label_guncelle()

    def _on_selection_changed(self, *_args) -> None:
        self._path_label_guncelle()

    def _sec(self, *_args) -> None:
        try:
            secim = self.chooser.selection or []
        except Exception:
            secim = []

        if not secim:
            self._debug("Dosya seçilmedi")
            self._path_label_guncelle()
            return

        yol = str(secim[0] or "").strip()
        if not yol:
            self._debug("Seçilen yol boş")
            return

        try:
            path_obj = Path(yol)
            if not path_obj.exists() or not path_obj.is_file():
                self._debug(f"Geçersiz dosya seçimi: {yol}")
                return

            if path_obj.suffix.lower() != ".py":
                self._debug(f".py olmayan dosya seçildi: {yol}")
                return
        except Exception as exc:
            self._debug(f"Path doğrulama hatası: {exc}")
            return

        self._debug(f"Dosya seçildi: {yol}")

        try:
            if self.on_select:
                self.on_select(yol)
        finally:
            self.dismiss()
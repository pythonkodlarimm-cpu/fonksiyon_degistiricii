# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/replace_karar_popup.py

ROL:
- Fonksiyon güncelleme öncesi gelişmiş karar popup'ı
- Full replace ve preserve_children modlarını kullanıcıya açıklamak
- Seçilen fonksiyon ve alt fonksiyon isimlerini dinamik göstermek

SURUM: 3
TARIH: 2026-03-18
IMZA: FY.
"""

from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView


class ReplaceKararPopup(Popup):
    def __init__(
        self,
        servis,
        *,
        function_name: str = "",
        function_path: str = "",
        child_count: int = 0,
        child_names: list[str] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.title = ""
        self.size_hint = (0.94, 0.84)
        self.separator_height = 0
        self.auto_dismiss = True

        self.servis = servis
        self.function_name = str(function_name or "").strip() or "Bilinmeyen Fonksiyon"
        self.function_path = str(function_path or "").strip()
        self.child_count = max(0, int(child_count or 0))
        self.child_names = list(child_names or [])

        self.content = self._build_content()

    # =========================================================
    # UI HELPERS
    # =========================================================
    def _build_label(
        self,
        text: str,
        *,
        font_size: str = "13sp",
        bold: bool = False,
        color=(1, 1, 1, 1),
        markup: bool = False,
    ) -> Label:
        lbl = Label(
            text=str(text or ""),
            font_size=font_size,
            bold=bold,
            color=color,
            halign="left",
            valign="top",
            size_hint_y=None,
            markup=markup,
        )
        lbl.bind(
            width=lambda inst, value: setattr(inst, "text_size", (max(1, value), None)),
            texture_size=lambda inst, size: setattr(inst, "height", max(dp(22), size[1] + dp(4))),
        )
        return lbl

    def _build_block(self, title: str, title_color, body_text: str, button_text: str, button_color, on_press):
        block = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            padding=(dp(10), dp(10), dp(10), dp(10)),
        )
        block.bind(minimum_height=block.setter("height"))

        block.add_widget(
            self._build_label(
                title,
                font_size="17sp",
                bold=True,
                color=title_color,
            )
        )

        block.add_widget(
            self._build_label(
                body_text,
                font_size="12sp",
                color=(0.92, 0.92, 0.96, 1),
            )
        )

        btn = Button(
            text=button_text,
            size_hint_y=None,
            height=dp(48),
            background_normal="",
            background_down="",
            background_color=button_color,
            color=(1, 1, 1, 1),
            bold=True,
            font_size="14sp",
        )
        btn.bind(on_release=on_press)
        block.add_widget(btn)

        block.height = max(dp(150), block.minimum_height)
        return block

    def _child_names_text(self) -> str:
        if not self.child_names:
            return "Yok"

        satirlar = []
        for index, name in enumerate(self.child_names, start=1):
            satirlar.append(f"{index}. {name}")
        return "\n".join(satirlar)

    # =========================================================
    # CONTENT
    # =========================================================
    def _build_content(self):
        outer = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=(dp(12), dp(12), dp(12), dp(12)),
        )

        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8),
            scroll_type=["bars", "content"],
        )

        root = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None,
        )
        root.bind(minimum_height=root.setter("height"))

        root.add_widget(
            self._build_label(
                f"Fonksiyon Güncelleme Kararı",
                font_size="19sp",
                bold=True,
                color=(0.95, 0.97, 1, 1),
            )
        )

        root.add_widget(
            self._build_label(
                f"Seçilen Fonksiyon: {self.function_name}",
                font_size="16sp",
                bold=True,
                color=(0.92, 0.96, 1, 1),
            )
        )

        if self.function_path:
            root.add_widget(
                self._build_label(
                    f"Yol: {self.function_path}",
                    font_size="11sp",
                    color=(0.74, 0.78, 0.86, 1),
                )
            )

        root.add_widget(
            self._build_label(
                f"Alt fonksiyon sayısı: {self.child_count}",
                font_size="14sp",
                bold=True,
                color=(1.0, 0.84, 0.38, 1) if self.child_count > 0 else (0.72, 0.95, 0.80, 1),
            )
        )

        if self.child_count > 0:
            root.add_widget(
                self._build_label(
                    "Etkilenebilecek alt fonksiyonlar:",
                    font_size="13sp",
                    bold=True,
                    color=(1.0, 0.90, 0.56, 1),
                )
            )
            root.add_widget(
                self._build_label(
                    self._child_names_text(),
                    font_size="12sp",
                    color=(0.90, 0.92, 0.98, 1),
                )
            )

        root.add_widget(
            self._build_label(
                self.servis.risk_notu(self.child_count),
                font_size="12sp",
                color=(1.0, 0.72, 0.72, 1) if self.child_count > 0 else (0.76, 0.92, 0.80, 1),
            )
        )

        root.add_widget(
            self._build_label(
                "Nasıl güncellemek istediğinizi seçin:",
                font_size="14sp",
                bold=True,
                color=(0.94, 0.96, 1, 1),
            )
        )

        full_text = self.servis.full_aciklama(self.child_count)
        if self.child_names:
            full_text += "\n\nBu modda aşağıdaki alt fonksiyonlar yeni kod içinde yoksa kaldırılır:\n"
            full_text += self._child_names_text()

        preserve_text = self.servis.preserve_aciklama(self.child_count)
        if self.child_names:
            preserve_text += "\n\nBu modda aşağıdaki alt fonksiyonlar korunmaya çalışılır:\n"
            preserve_text += self._child_names_text()

        root.add_widget(
            self._build_block(
                "1) Komple Değiştir",
                (1.0, 0.82, 0.82, 1),
                full_text,
                "Komple Değiştir",
                (0.46, 0.18, 0.18, 1),
                self._full,
            )
        )

        root.add_widget(
            self._build_block(
                "2) Alt Fonksiyonları Koru",
                (0.78, 0.97, 0.82, 1),
                preserve_text,
                "Alt Fonksiyonları Koru",
                (0.16, 0.42, 0.24, 1),
                self._preserve,
            )
        )

        btn_cancel = Button(
            text="İptal",
            size_hint_y=None,
            height=dp(46),
            background_normal="",
            background_down="",
            background_color=(0.22, 0.25, 0.33, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size="14sp",
        )
        btn_cancel.bind(on_release=self._cancel)
        root.add_widget(btn_cancel)

        scroll.add_widget(root)
        outer.add_widget(scroll)
        return outer

    # =========================================================
    # EVENTS
    # =========================================================
    def _full(self, *_args):
        try:
            self.servis.sec_full()
        finally:
            self.dismiss()

    def _preserve(self, *_args):
        try:
            self.servis.sec_preserve()
        finally:
            self.dismiss()

    def _cancel(self, *_args):
        try:
            self.servis.iptal()
        finally:
            self.dismiss()
# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici.py

ROL:
- Dosya seçici UI organizatörü
- Seç / Yenile aksiyonlarını yönetir
- Platform fark etmeksizin uygulama içi özel picker kullanır
- Seçilen dosyayı üst katmana bildirir

MİMARİ:
- UI burada
- Picker sınıfı lazy import ile yüklenir
- Ağır modüller uygulama açılışında yüklenmez
- Gerçek picker nesnesi sadece kullanıcı "Seç" butonuna basınca oluşturulur

DAVRANIŞ:
- Android ve masaüstünde aynı özel picker çalışır
- Kullanıcı klasör içinde gezinir
- .py dosyasını seçince otomatik tarama başlar
- Ayrı "Tara" aksiyonu yoktur

SURUM: 17
TARIH: 2026-03-15
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from app.ui.icon_toolbar import IconToolbar
from app.ui.iconlu_baslik import IconluBaslik
from app.ui.tema import INPUT_BG, TEXT_MUTED, TEXT_PRIMARY


class DosyaSecici(BoxLayout):
    """
    Dosya seçme ve otomatik tarama paneli.

    Özellikler:
    - seçili dosya yolunu gösterir
    - uygulama içi özel picker ile dosya seçer
    - seçim sonrası taramayı otomatik başlatır
    - yenile akışını dış callback'e devreder
    """

    def __init__(self, on_scan, on_refresh=None, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(156),
            spacing=dp(8),
            **kwargs,
        )

        self.on_scan = on_scan
        self.on_refresh = on_refresh

        self._last_selected_path = ""
        self._internal_picker = None

        self._build_ui()

    # =========================================================
    # DEBUG
    # =========================================================
    def _debug(self, message: str) -> None:
        try:
            print("[DOSYA_SECICI]", str(message))
        except Exception:
            pass

    # =========================================================
    # LAZY IMPORT
    # =========================================================
    def _show_info_popup(self, title: str, message: str) -> None:
        from app.ui.dosya_secici_paketi.info_popup import show_info_popup

        show_info_popup(
            owner=self,
            title=title,
            message=message,
        )

    def _get_internal_picker(self):
        if self._internal_picker is None:
            from app.ui.dosya_secici_paketi.desktop_picker import DesktopPicker

            self._internal_picker = DesktopPicker(
                owner=self,
                on_selected=self._after_picker_selected,
            )
            self._debug("Internal picker lazy oluşturuldu")

        return self._internal_picker

    # =========================================================
    # UI
    # =========================================================
    def _build_ui(self) -> None:
        self._build_header()
        self._build_path_box()
        self._build_action_row()

    def _build_header(self) -> None:
        self.header = IconluBaslik(
            text="Python Dosyası",
            icon_name="schema.png",
            height_dp=30,
            font_size="15sp",
            color=TEXT_PRIMARY,
        )
        self.add_widget(self.header)

    def _build_path_box(self) -> None:
        self.path_input = TextInput(
            hint_text="Python dosyası seç...",
            multiline=False,
            readonly=True,
            size_hint_y=None,
            height=dp(46),
            background_normal="",
            background_active="",
            background_color=INPUT_BG,
            foreground_color=TEXT_PRIMARY,
            cursor_color=TEXT_PRIMARY,
            padding=(dp(12), dp(12)),
            font_size="14sp",
        )
        self.add_widget(self.path_input)

        self.path_hint = Label(
            text="Seçilen dosya burada görünecek",
            size_hint_y=None,
            height=dp(16),
            color=TEXT_MUTED,
            font_size="12sp",
            halign="left",
            valign="middle",
            shorten=True,
            shorten_from="right",
        )
        self.path_hint.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
        self.add_widget(self.path_hint)

    def _build_action_row(self) -> None:
        toolbar = IconToolbar(
            spacing_dp=24,
            padding_dp=8,
        )

        toolbar.add_tool(
            icon_name="folder_open.png",
            text="Seç",
            on_release=self._open_selector,
            icon_size_dp=42,
            text_size="12sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        toolbar.add_tool(
            icon_name="refresh.png",
            text="Yenile",
            on_release=self._handle_refresh,
            icon_size_dp=42,
            text_size="12sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.add_widget(toolbar)

    # =========================================================
    # PUBLIC API
    # =========================================================
    def get_path(self) -> str:
        text_path = self.path_input.text.strip()
        if text_path:
            return text_path
        return str(self._last_selected_path or "").strip()

    def set_path(self, value: str) -> None:
        temiz = str(value or "").strip()
        self.path_input.text = temiz
        self.path_hint.text = temiz if temiz else "Seçilen dosya burada görünecek"
        self._last_selected_path = temiz
        self._debug(f"Path set edildi: {temiz}")

    # =========================================================
    # ACTIONS
    # =========================================================
    def _handle_refresh(self, *_args):
        yol = self.get_path()
        self._debug(f"Yenile tetiklendi: {yol}")

        if self.on_refresh:
            self.on_refresh(yol)
        elif self.on_scan:
            self.on_scan(yol)

    def _open_selector(self, *_args):
        self._debug("Özel dosya seçici açılıyor")
        picker = self._get_internal_picker()
        picker.open_popup()

    # =========================================================
    # PICKER CALLBACK
    # =========================================================
    def _after_picker_selected(self, selection) -> None:
        path_str = str(getattr(selection, "path", "") or "").strip()
        self._debug(f"Seçim sonucu geldi: {path_str}")

        if not path_str:
            self._show_info_popup(
                "Dosya Seçici",
                "Seçilen dosya yolu alınamadı.",
            )
            return

        try:
            p = Path(path_str)
            if not p.exists() or not p.is_file():
                self._show_info_popup(
                    "Dosya Seçici",
                    f"Seçilen dosya bulunamadı:\n{path_str}",
                )
                return
        except Exception as exc:
            self._show_info_popup(
                "Dosya Seçici",
                f"Dosya doğrulanamadı:\n{exc}",
            )
            return

        self.set_path(path_str)

        def _run_scan(_dt):
            final_path = self.get_path()
            self._debug(f"Otomatik tarama başlıyor: {final_path}")

            if not final_path:
                self._show_info_popup(
                    "Tarama Hatası",
                    "Dosya yolu boş olduğu için tarama başlatılamadı.",
                )
                return

            try:
                if self.on_scan:
                    self.on_scan(final_path)
            except Exception as exc:
                self._show_info_popup(
                    "Tarama Hatası",
                    f"Dosya seçildi ama tarama başlatılamadı:\n{exc}",
                )

        Clock.schedule_once(_run_scan, 0)

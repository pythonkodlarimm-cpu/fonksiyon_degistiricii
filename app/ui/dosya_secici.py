# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici.py

ROL:
- Dosya seçici UI organizatörü
- Seç / Yenile aksiyonlarını yönetir
- Platforma göre uygun picker'ı çağırır
- Seçilen belgeyi üst katmana bildirir

MİMARİ:
- UI burada
- Android'de gerçek sistem picker kullanılır
- Diğer ortamlarda iç picker kullanılır
- Picker sınıfları lazy import ile yüklenir
- Ağır modüller uygulama açılışında yüklenmez

DAVRANIŞ:
- Android'de ACTION_OPEN_DOCUMENT ile tek dosya seçilir
- Dosya uzantısı burada kısıtlanmaz
- Seçim sonrası otomatik tarama başlar
- Yenile akışında son seçilen belge kimliği tekrar kullanılır

SURUM: 22
TARIH: 2026-03-16
IMZA: FY.
"""

from __future__ import annotations

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.utils import platform

from app.ui.icon_toolbar import IconToolbar
from app.ui.iconlu_baslik import IconluBaslik
from app.ui.tema import INPUT_BG, TEXT_MUTED, TEXT_PRIMARY


class DosyaSecici(BoxLayout):
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

        self._desktop_picker = None
        self._android_document_picker = None

        self._selection = None
        self._last_identifier = ""
        self._last_display_name = ""

        self._build_ui()

    def _debug(self, message: str) -> None:
        try:
            print("[DOSYA_SECICI]", str(message))
        except Exception:
            pass

    def _show_info_popup(self, title: str, message: str) -> None:
        from app.ui.dosya_secici_paketi.info_popup import show_info_popup

        show_info_popup(
            owner=self,
            title=title,
            message=message,
        )

    def _get_desktop_picker(self):
        if self._desktop_picker is None:
            from app.ui.dosya_secici_paketi import get_desktop_picker_class

            DesktopPicker = get_desktop_picker_class()
            self._desktop_picker = DesktopPicker(
                owner=self,
                on_selected=self._after_picker_selected,
            )
            self._debug("DesktopPicker lazy oluşturuldu")

        return self._desktop_picker

    def _get_android_document_picker(self):
        if self._android_document_picker is None:
            from app.ui.dosya_secici_paketi import get_android_document_picker_class

            AndroidDocumentPicker = get_android_document_picker_class()
            self._android_document_picker = AndroidDocumentPicker(
                owner=self,
                on_selected=self._after_picker_selected,
            )
            self._debug("AndroidDocumentPicker lazy oluşturuldu")

        return self._android_document_picker

    def _build_ui(self) -> None:
        self.header = IconluBaslik(
            text="Belge / Kod Dosyası",
            icon_name="schema.png",
            height_dp=30,
            font_size="15sp",
            color=TEXT_PRIMARY,
        )
        self.add_widget(self.header)

        self.path_input = TextInput(
            hint_text="Dosya seç...",
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
            text="Seçilen belge burada görünecek",
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

        self.toolbar = IconToolbar(
            spacing_dp=24,
            padding_dp=8,
        )

        self.toolbar.add_tool(
            icon_name="folder_open.png",
            text="Seç",
            on_release=self._open_selector,
            icon_size_dp=42,
            text_size="12sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.toolbar.add_tool(
            icon_name="refresh.png",
            text="Yenile",
            on_release=self._handle_refresh,
            icon_size_dp=42,
            text_size="12sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.add_widget(self.toolbar)

    def _selection_identifier(self, selection) -> str:
        if selection is None:
            return ""

        try:
            return str(selection.preferred_identifier() or "").strip()
        except Exception:
            pass

        try:
            uri = str(getattr(selection, "uri", "") or "").strip()
            if uri:
                return uri
        except Exception:
            pass

        try:
            path = str(getattr(selection, "local_path", "") or "").strip()
            if path:
                return path
        except Exception:
            pass

        return ""

    def _selection_display_text(self, selection) -> str:
        if selection is None:
            return ""

        try:
            name = str(selection.preferred_display_name() or "").strip()
            if name:
                return name
        except Exception:
            pass

        try:
            name = str(getattr(selection, "display_name", "") or "").strip()
            if name:
                return name
        except Exception:
            pass

        return self._selection_identifier(selection)

    def get_path(self) -> str:
        if self._selection is not None:
            identifier = self._selection_identifier(self._selection)
            if identifier:
                return identifier

        text_path = self.path_input.text.strip()
        if text_path:
            return text_path

        return str(self._last_identifier or "").strip()

    def get_selection(self):
        return self._selection

    def get_display_name(self) -> str:
        return str(self._last_display_name or "").strip()

    def set_path(self, value: str) -> None:
        temiz = str(value or "").strip()
        self.path_input.text = temiz
        self.path_hint.text = temiz if temiz else "Seçilen belge burada görünecek"
        self._last_identifier = temiz
        if temiz and not self._last_display_name:
            self._last_display_name = temiz
        self._debug(f"Identifier set edildi: {temiz}")

    def set_selection(self, selection) -> None:
        self._selection = selection

        identifier = self._selection_identifier(selection)
        display_text = self._selection_display_text(selection)

        self.path_input.text = identifier
        self.path_hint.text = display_text if display_text else "Seçilen belge burada görünecek"

        self._last_identifier = identifier
        self._last_display_name = display_text

        self._debug(
            "Selection set edildi | "
            f"source={getattr(selection, 'source', '')} "
            f"identifier={identifier} "
            f"display={display_text}"
        )

    def clear_selection(self) -> None:
        self._selection = None
        self.path_input.text = ""
        self.path_hint.text = "Seçilen belge burada görünecek"
        self._last_identifier = ""
        self._last_display_name = ""

    def _handle_refresh(self, *_args):
        identifier = self.get_path()
        self._debug(f"Yenile tetiklendi: {identifier}")

        if not identifier:
            self._show_info_popup(
                "Yenileme",
                "Önce bir belge seçmelisiniz.",
            )
            return

        if self.on_refresh:
            self.on_refresh(identifier)
        elif self.on_scan:
            self.on_scan(identifier)

    def _open_selector(self, *_args):
        self._debug("Dosya seçici açılıyor")

        if platform == "android":
            picker = self._get_android_document_picker()
            picker.open_picker()
        else:
            picker = self._get_desktop_picker()
            picker.open_popup()

    def _after_picker_selected(self, selection) -> None:
        identifier = self._selection_identifier(selection)
        self._debug(f"Seçim sonucu geldi: {identifier}")

        if not identifier:
            self._show_info_popup(
                "Dosya Seçici",
                "Seçilen dosya kimliği alınamadı.",
            )
            return

        self.set_selection(selection)

        def _run_scan(_dt):
            final_identifier = self.get_path()
            self._debug(f"Otomatik tarama başlıyor: {final_identifier}")

            if not final_identifier:
                self._show_info_popup(
                    "Tarama Hatası",
                    "Dosya kimliği boş olduğu için tarama başlatılamadı.",
                )
                return

            try:
                if self.on_scan:
                    self.on_scan(final_identifier)
            except Exception as exc:
                self._show_info_popup(
                    "Tarama Hatası",
                    f"Dosya seçildi ama tarama başlatılamadı:\n{exc}",
                )

        Clock.schedule_once(_run_scan, 0)

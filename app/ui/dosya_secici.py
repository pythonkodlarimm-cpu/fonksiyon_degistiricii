# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici.py

ROL:
- Dosya seçici UI organizatörü
- Seç / Fonksiyonları Göster aksiyonlarını yönetir
- Platforma göre uygun picker'ı çağırır
- Seçilen belgeyi üst katmana bildirir

MİMARİ:
- UI burada
- Android'de gerçek sistem picker kullanılır
- Diğer ortamlarda iç picker kullanılır
- Picker sınıfları lazy import ile yüklenir
- Ağır modüller uygulama açılışında yüklenmez

DAVRANIŞ:
- Başlangıçta yalnızca büyük Dosya Seç ikonu görünür
- Dosya seçildikten sonra Fonksiyonları Göster ikonu görünür
- Dosya seçimi sonrası tarama arka planda otomatik tetiklenir
- Güvenilirlik için otomatik tetikleme birden fazla kez kısa aralıkla denenir

SURUM: 25
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

        self.header = None
        self.path_input = None
        self.path_hint = None
        self.toolbar = None
        self.select_tool = None
        self.refresh_tool = None

        self._refresh_tool_visible_width = dp(118)
        self._select_tool_visible_width = dp(128)

        self._build_ui()
        self._update_refresh_visibility()

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

    # =========================================================
    # UI
    # =========================================================
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
            spacing_dp=28,
            padding_dp=8,
        )

        self.select_tool = self.toolbar.add_tool(
            icon_name="dosya_sec.png",
            text="Dosya Seç",
            on_release=self._handle_select_pressed,
            icon_size_dp=56,
            text_size="13sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.refresh_tool = self.toolbar.add_tool(
            icon_name="fonksiyon_listesinde_goster.png",
            text="Fonksiyonları Göster",
            on_release=self._handle_refresh,
            icon_size_dp=44,
            text_size="10sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.add_widget(self.toolbar)

        try:
            self.select_tool.size_hint_x = None
            self.select_tool.width = self._select_tool_visible_width
        except Exception:
            pass

    # =========================================================
    # ICON VISIBILITY
    # =========================================================
    def _has_selection(self) -> bool:
        if self._selection is not None:
            try:
                if str(self._selection_identifier(self._selection) or "").strip():
                    return True
            except Exception:
                pass

        if str(self._last_identifier or "").strip():
            return True

        try:
            if str(self.path_input.text or "").strip():
                return True
        except Exception:
            pass

        return False

    def _set_tool_visible(self, widget, visible: bool, width: float) -> None:
        if widget is None:
            return

        try:
            widget.disabled = not visible
        except Exception:
            pass

        try:
            widget.opacity = 1 if visible else 0
        except Exception:
            pass

        try:
            widget.size_hint_x = None
        except Exception:
            pass

        try:
            widget.width = width if visible else 0.01
        except Exception:
            pass

    def _update_refresh_visibility(self) -> None:
        self._set_tool_visible(
            self.refresh_tool,
            self._has_selection(),
            self._refresh_tool_visible_width,
        )

    # =========================================================
    # SELECTION HELPERS
    # =========================================================
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

    # =========================================================
    # PUBLIC API
    # =========================================================
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

        self._update_refresh_visibility()
        self._debug(f"Identifier set edildi: {temiz}")

    def set_selection(self, selection) -> None:
        self._selection = selection

        identifier = self._selection_identifier(selection)
        display_text = self._selection_display_text(selection)

        self.path_input.text = identifier
        self.path_hint.text = display_text if display_text else "Seçilen belge burada görünecek"

        self._last_identifier = identifier
        self._last_display_name = display_text

        self._update_refresh_visibility()

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
        self._update_refresh_visibility()

    # =========================================================
    # ACTIONS
    # =========================================================
    def _handle_select_pressed(self, *_args):
        self._open_selector()

    def _handle_refresh(self, *_args):
        identifier = self.get_path()
        self._debug(f"Fonksiyonları göster tetiklendi: {identifier}")

        if not identifier:
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

    # =========================================================
    # AUTO TRIGGER
    # =========================================================
    def _trigger_scan_attempt(self, reason: str) -> None:
        final_identifier = self.get_path()
        self._debug(f"Otomatik tetikleme ({reason}): {final_identifier}")

        if not final_identifier:
            return

        try:
            if self.on_scan:
                self.on_scan(final_identifier)
        except Exception as exc:
            self._debug(f"Otomatik tetikleme hatası ({reason}): {exc}")

    def _auto_trigger_scan_sequence(self) -> None:
        Clock.schedule_once(lambda *_: self._trigger_scan_attempt("hemen"), 0)
        Clock.schedule_once(lambda *_: self._trigger_scan_attempt("kisa_gecikme"), 0.12)
        Clock.schedule_once(lambda *_: self._trigger_scan_attempt("ikinci_gecikme"), 0.35)

    # =========================================================
    # PICKER CALLBACK
    # =========================================================
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
        self._auto_trigger_scan_sequence()

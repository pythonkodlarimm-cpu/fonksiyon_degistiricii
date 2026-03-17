# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici.py

ROL:
- Dosya seçici UI organizatörü
- Dosya Seç aksiyonunu yönetir
- Platforma göre uygun picker'ı çağırır
- Seçilen belgeyi üst katmana bildirir

MİMARİ:
- UI burada
- Android'de gerçek sistem picker kullanılır
- Diğer ortamlarda iç picker kullanılır
- Picker sınıfları lazy import ile yüklenir
- Ağır modüller uygulama açılışında yüklenmez

DAVRANIŞ:
- Uygulama açılışında büyük Dosya Seç ikonu görünür
- Dosya Seç ile picker açılır
- Dosya seçildikten sonra otomatik tarama tetiklenir
- Ham URI ekranda ana metin olarak gösterilmez
- Dosya adı ve kısa durum bilgisi öne çıkarılır

API 34 UYUMLULUK NOTU:
- Android tarafında sistem picker yalnızca lazy import ile çağrılır
- Dosya seçimi sonrası identifier ve display name güvenli şekilde normalize edilir
- Paket içindeki DocumentSelection / picker yapısıyla uyumludur

SURUM: 31
TARIH: 2026-03-17
IMZA: FY.
"""

from __future__ import annotations

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.utils import platform

from app.ui.icon_toolbar import IconToolbar
from app.ui.iconlu_baslik import IconluBaslik
from app.ui.kart import Kart
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY


class DosyaSecici(Kart):
    def __init__(self, on_scan, on_refresh=None, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(210),
            spacing=dp(12),
            padding=(dp(14), dp(12), dp(14), dp(14)),
            bg=(0.08, 0.11, 0.16, 1),
            border=(0.18, 0.21, 0.27, 1),
            radius=16,
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
        self.file_name_label = None
        self.file_detail_label = None
        self.status_hint_label = None
        self.toolbar = None
        self.select_tool = None

        self._build_ui()
        self._refresh_summary()

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
        self.header.size_hint_y = None
        self.header.height = dp(30)
        self.add_widget(self.header)

        summary_wrap = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(62),
            spacing=dp(4),
        )

        self.file_name_label = Label(
            text="Dosya seçilmedi",
            color=TEXT_PRIMARY,
            font_size="17sp",
            bold=True,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(26),
            shorten=True,
            shorten_from="right",
        )
        self.file_name_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
        summary_wrap.add_widget(self.file_name_label)

        self.file_detail_label = Label(
            text="Seçilen belge bilgisi burada görünür.",
            color=TEXT_MUTED,
            font_size="11sp",
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(16),
            shorten=True,
            shorten_from="right",
        )
        self.file_detail_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
        summary_wrap.add_widget(self.file_detail_label)

        self.status_hint_label = Label(
            text="Belge seçmeniz bekleniyor.",
            color=(0.76, 0.82, 0.92, 1),
            font_size="11sp",
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(16),
            shorten=True,
            shorten_from="right",
        )
        self.status_hint_label.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
        summary_wrap.add_widget(self.status_hint_label)

        self.add_widget(summary_wrap)

        toolbar_wrap = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(86),
        )
        toolbar_wrap.add_widget(Label(size_hint_x=1))

        self.toolbar = IconToolbar(
            spacing_dp=0,
            padding_dp=0,
        )
        self.toolbar.size_hint = (None, None)
        self.toolbar.size = (dp(170), dp(86))

        self.select_tool = self.toolbar.add_tool(
            icon_name="dosya_sec.png",
            text="Dosya Seç",
            on_release=self._handle_select_pressed,
            icon_size_dp=68,
            text_size="14sp",
            color=TEXT_PRIMARY,
            icon_bg=None,
        )

        try:
            self.select_tool.size_hint_x = None
            self.select_tool.width = dp(170)
        except Exception:
            pass

        toolbar_wrap.add_widget(self.toolbar)
        toolbar_wrap.add_widget(Label(size_hint_x=1))

        self.add_widget(toolbar_wrap)

    # =========================================================
    # STATE HELPERS
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

        return ""

    def _short_identifier(self, value: str, limit: int = 52) -> str:
        metin = str(value or "").strip()
        if len(metin) <= limit:
            return metin
        if limit < 10:
            return metin[:limit]

        sol = max(8, limit // 2 - 2)
        sag = max(8, limit - sol - 3)
        return f"{metin[:sol]}...{metin[-sag:]}"

    def _has_selection(self) -> bool:
        if self._selection is not None and self._selection_identifier(self._selection):
            return True

        if str(self._last_identifier or "").strip():
            return True

        return False

    def _refresh_summary(self) -> None:
        if not self._has_selection():
            self.file_name_label.text = "Dosya seçilmedi"
            self.file_detail_label.text = "Seçilen belge bilgisi burada görünür."
            self.status_hint_label.text = "Belge seçmeniz bekleniyor."
            self.status_hint_label.color = (0.76, 0.82, 0.92, 1)
            return

        display_name = str(self._last_display_name or "").strip()
        identifier = str(self._last_identifier or "").strip()

        self.file_name_label.text = display_name if display_name else "Seçilen belge hazır"
        self.file_detail_label.text = (
            self._short_identifier(identifier) if identifier else "Belge kimliği yok"
        )
        self.status_hint_label.text = "Belge seçildi • Tarama otomatik başlatılır."
        self.status_hint_label.color = (0.72, 0.94, 0.78, 1)

    # =========================================================
    # PUBLIC API
    # =========================================================
    def get_path(self) -> str:
        if self._selection is not None:
            identifier = self._selection_identifier(self._selection)
            if identifier:
                return identifier

        return str(self._last_identifier or "").strip()

    def get_selection(self):
        return self._selection

    def get_display_name(self) -> str:
        return str(self._last_display_name or "").strip()

    def set_path(self, value: str) -> None:
        temiz = str(value or "").strip()
        self._last_identifier = temiz
        self._refresh_summary()
        self._debug(f"Identifier set edildi: {temiz}")

    def set_selection(self, selection) -> None:
        self._selection = selection

        identifier = self._selection_identifier(selection)
        display_text = self._selection_display_text(selection)

        self._last_identifier = identifier
        self._last_display_name = display_text

        self._refresh_summary()

        self._debug(
            "Selection set edildi | "
            f"source={getattr(selection, 'source', '')} "
            f"identifier={identifier} "
            f"display={display_text}"
        )

    def clear_selection(self) -> None:
        self._selection = None
        self._last_identifier = ""
        self._last_display_name = ""
        self._refresh_summary()

    # =========================================================
    # ACTIONS
    # =========================================================
    def _handle_select_pressed(self, *_args):
        self._open_selector()

    def _open_selector(self, *_args):
        self._debug("Dosya seçici açılıyor")

        try:
            if platform == "android":
                self._get_android_document_picker().open_picker()
            else:
                self._get_desktop_picker().open_popup()
        except Exception as exc:
            self._debug(f"Seçici açma hatası: {exc}")
            self._show_info_popup(
                "Dosya Seçici",
                f"Seçici açılamadı: {exc}",
            )

    # =========================================================
    # AUTO TRIGGER
    # =========================================================
    def _trigger_scan_attempt(self, reason: str) -> None:
        final_identifier = self.get_path()
        self._debug(f"Otomatik tetikleme ({reason}): {final_identifier}")

        if not final_identifier and self._selection is None:
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

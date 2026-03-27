# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/panel/editor_paneli.py

ROL:
- Editör panelinin ana UI organizatörüdür
- Mevcut kod, yeni kod ve aksiyon alanlarını bir araya getirir
- Aksiyon, bildirim, popup, doğrulama ve yardımcı akışları ilgili yöneticiler üzerinden yürütür
- Büyük kod içeriklerinde UI donmasını azaltmak için içerik yüklemeyi güvenli biçimde erteler
- Üst katmanların editör iç yapısını bilmeden metin okuyup yazabilmesi için public text API sağlar
- Aktif dile göre görünür metinleri üretir ve yeniler

MİMARİ:
- Alt modüllere doğrudan erişmez
- İlgili alt paket yöneticileri ile konuşur
- UI burada, iş akışı yöneticiler ve alt modüllerdedir
- set_item akışı tek ertelenmiş yükleme ile stabil tutulur
- Root ve diğer üst katmanlar public API üzerinden içerik okuyup yazabilir
- Widget hazır değilken veya item eksik gelirse güvenli fallback uygulanır

SURUM: 35
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout

from app.services.yoneticisi import ServicesYoneticisi
from app.ui.icon_toolbar import IconToolbar
from app.ui.iconlu_baslik import IconluBaslik
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY


class EditorPaneli(BoxLayout):
    def __init__(
        self,
        on_update=None,
        on_restore=None,
        services: ServicesYoneticisi | None = None,
        **kwargs,
    ):
        super().__init__(orientation="vertical", spacing=dp(10), **kwargs)

        self.on_update = on_update
        self.on_restore = on_restore
        self.services = services

        self.current_item = None
        self._new_code_buffer = ""
        self._current_popup = None
        self._editor_popup = None

        self.path_label = None
        self.error_box = None
        self.current_title = None
        self.new_title = None
        self.current_open_tool = None
        self.new_edit_tool = None
        self.current_code_area = None
        self.inline_notice = None
        self.new_code_area = None
        self.action_toolbar = None

        self._tool_clear = None
        self._tool_update = None
        self._tool_check = None
        self._tool_copy = None
        self._tool_paste = None
        self._tool_restore = None

        self._pending_set_item_event = None
        self._set_item_serial = 0

        self._build_ui()
        self.refresh_language()
        self._set_status_info(self._m("app_ready", "Hazır."), 0)

    # =========================================================
    # DIL
    # =========================================================
    def _get_services(self) -> ServicesYoneticisi:
        if self.services is not None:
            return self.services

        try:
            parent = self.parent
            while parent is not None:
                services = getattr(parent, "services", None)
                if services is not None:
                    self.services = services
                    return services
                parent = getattr(parent, "parent", None)
        except Exception:
            pass

        self.services = ServicesYoneticisi()
        return self.services

    def _m(self, anahtar: str, default: str = "") -> str:
        try:
            return str(
                self._get_services().metin(anahtar, default) or default or anahtar
            )
        except Exception:
            return str(default or anahtar)

    def refresh_language(self) -> None:
        try:
            self._refresh_path_label_language()
        except Exception:
            pass

        try:
            self._refresh_title_widgets_language()
        except Exception:
            pass

        try:
            self._refresh_code_areas_language()
        except Exception:
            pass

        try:
            if self.error_box is not None and hasattr(self.error_box, "refresh_language"):
                self.error_box.refresh_language()
        except Exception:
            pass

        try:
            if self.inline_notice is not None and hasattr(self.inline_notice, "refresh_language"):
                self.inline_notice.refresh_language()
        except Exception:
            pass

        try:
            self._refresh_action_toolbar_language()
        except Exception:
            pass

    def _refresh_path_label_language(self) -> None:
        if self.path_label is None:
            return

        try:
            if self.current_item is None:
                self.path_label.set_text(
                    self._m("selected_function", "Seçili fonksiyon: -")
                )
            else:
                self.path_label.set_text(
                    f"{self._selected_function_prefix()}: {self._item_path_text(self.current_item)}"
                )
        except Exception:
            pass

    def _refresh_title_widgets_language(self) -> None:
        self._set_text_on_widget(
            self.current_title,
            self._m("current_code", "Mevcut Kod"),
        )
        self._set_text_on_widget(
            self.new_title,
            self._m("new_function_code", "Yeni Fonksiyon Kodu"),
        )
        self._set_text_on_widget(
            self.current_open_tool,
            self._m("open", "Aç"),
        )
        self._set_text_on_widget(
            self.new_edit_tool,
            self._m("edit", "Düzenle"),
        )

    def _refresh_code_areas_language(self) -> None:
        try:
            if self.current_code_area is not None:
                if hasattr(self.current_code_area, "refresh_language") and callable(
                    self.current_code_area.refresh_language
                ):
                    self.current_code_area.refresh_language()
                else:
                    self._set_hint_text_on_widget(
                        self.current_code_area,
                        self._m("preview_empty", "Henüz önizleme yok."),
                    )
        except Exception:
            pass

        try:
            if self.new_code_area is not None:
                if hasattr(self.new_code_area, "refresh_language") and callable(
                    self.new_code_area.refresh_language
                ):
                    self.new_code_area.refresh_language()
                else:
                    self._set_hint_text_on_widget(
                        self.new_code_area,
                        self._m(
                            "new_function_hint",
                            "Tam fonksiyon kodunu buraya yaz veya yapıştır.",
                        ),
                    )
        except Exception:
            pass

    def _refresh_action_toolbar_language(self) -> None:
        tool_map = [
            (self._tool_clear, "clear", "Temizle"),
            (self._tool_update, "update", "Güncelle"),
            (self._tool_check, "check", "Kontrol Et"),
            (self._tool_copy, "copy", "Kopyala"),
            (self._tool_paste, "paste", "Yapıştır"),
            (self._tool_restore, "restore", "Geri Yükle"),
        ]

        for tool, key, default in tool_map:
            self._set_text_on_widget(tool, self._m(key, default))

    # =========================================================
    # YONETICILER
    # =========================================================
    def _aksiyon(self):
        from app.ui.editor_paketi.aksiyon import AksiyonYoneticisi
        return AksiyonYoneticisi()

    def _bilesenler(self):
        from app.ui.editor_paketi.bilesenler import BilesenlerYoneticisi
        return BilesenlerYoneticisi()

    def _bildirim(self):
        from app.ui.editor_paketi.bildirim import BildirimYoneticisi
        return BildirimYoneticisi()

    def _dogrulama(self):
        from app.ui.editor_paketi.dogrulama import DogrulamaYoneticisi
        return DogrulamaYoneticisi()

    def _popup(self):
        from app.ui.editor_paketi.popup import PopupYoneticisi
        return PopupYoneticisi()

    def _yardimci(self):
        from app.ui.editor_paketi.yardimci import YardimciYoneticisi
        return YardimciYoneticisi()

    # =========================================================
    # UI
    # =========================================================
    def _build_ui(self) -> None:
        self.path_label = IconluBaslik(
            text=self._m("selected_function", "Seçili fonksiyon: -"),
            icon_name="edit.png",
            height_dp=38,
            font_size="16sp",
            color=TEXT_PRIMARY,
        )
        self.path_label.size_hint_y = None
        self.path_label.height = dp(38)
        self.add_widget(self.path_label)

        self.error_box = self._bilesenler().bilgi_kutusu_olustur(
            services=self._get_services()
        )
        self.add_widget(self.error_box)

        self.add_widget(
            self._build_title_row(
                title_key="current_code",
                title_default="Mevcut Kod",
                icon_name="visibility_on.png",
                action_icon="visibility_on.png",
                action_text_key="open",
                action_text_default="Aç",
                callback=self._open_current_code_popup,
                row_type="current",
            )
        )

        self.current_code_area = self._bilesenler().sade_kod_alani_olustur(
            readonly=True,
            hint_text=self._m("preview_empty", "Henüz önizleme yok."),
            hint_text_key="preview_empty",
            services=self._get_services(),
            size_hint_y=0.34,
        )
        self.add_widget(self.current_code_area)

        self.add_widget(
            self._build_title_row(
                title_key="new_function_code",
                title_default="Yeni Fonksiyon Kodu",
                icon_name="edit.png",
                action_icon="edit.png",
                action_text_key="edit",
                action_text_default="Düzenle",
                callback=self._open_new_code_editor_popup,
                row_type="new",
            )
        )

        self.inline_notice = self._bildirim().bildirim_olustur()
        self.add_widget(self.inline_notice)

        self.new_code_area = self._bilesenler().sade_kod_alani_olustur(
            readonly=False,
            hint_text=self._m(
                "new_function_hint",
                "Tam fonksiyon kodunu buraya yaz veya yapıştır.",
            ),
            hint_text_key="new_function_hint",
            services=self._get_services(),
            size_hint_y=0.66,
        )
        self.add_widget(self.new_code_area)

        self._build_action_toolbar()

    def _build_title_row(
        self,
        title_key: str,
        title_default: str,
        icon_name: str,
        action_icon: str,
        action_text_key: str,
        action_text_default: str,
        callback,
        row_type: str = "",
    ):
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

        title_widget = IconluBaslik(
            text=self._m(title_key, title_default),
            icon_name=icon_name,
            height_dp=34,
            font_size="15sp",
            color=(0.80, 0.89, 1, 1),
            size_hint_x=1,
        )
        row.add_widget(title_widget)
        wrap.add_widget(row)

        toolbar = IconToolbar(spacing_dp=12, padding_dp=0)
        toolbar.size_hint_y = None
        toolbar.height = dp(36)
        action_tool = toolbar.add_tool(
            icon_name=action_icon,
            text=self._m(action_text_key, action_text_default),
            on_release=callback,
            icon_size_dp=34,
            text_size="11sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )
        wrap.add_widget(toolbar)

        if row_type == "current":
            self.current_title = title_widget
            self.current_open_tool = action_tool
        elif row_type == "new":
            self.new_title = title_widget
            self.new_edit_tool = action_tool

        return wrap

    def _build_action_toolbar(self) -> None:
        self.action_toolbar = IconToolbar(spacing_dp=18, padding_dp=6)
        self.action_toolbar.size_hint_y = None
        self.action_toolbar.height = dp(84)

        self._tool_clear = self.action_toolbar.add_tool(
            icon_name="clear.png",
            text=self._m("clear", "Temizle"),
            on_release=self._clear_new_code,
            icon_size_dp=42,
            text_size="12sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self._tool_update = self.action_toolbar.add_tool(
            icon_name="upload.png",
            text=self._m("update", "Güncelle"),
            on_release=self._handle_update,
            icon_size_dp=42,
            text_size="12sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self._tool_check = self.action_toolbar.add_tool(
            icon_name="code_check.png",
            text=self._m("check", "Kontrol Et"),
            on_release=self._check_new_code,
            icon_size_dp=42,
            text_size="11sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self._tool_copy = self.action_toolbar.add_tool(
            icon_name="file_copy.png",
            text=self._m("copy", "Kopyala"),
            on_release=self._copy_current_to_new,
            icon_size_dp=42,
            text_size="12sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self._tool_paste = self.action_toolbar.add_tool(
            icon_name="yapistir.png",
            text=self._m("paste", "Yapıştır"),
            on_release=self._paste_new_code,
            icon_size_dp=42,
            text_size="12sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self._tool_restore = self.action_toolbar.add_tool(
            icon_name="geri_yukle.png",
            text=self._m("restore", "Geri Yükle"),
            on_release=self._handle_restore,
            icon_size_dp=42,
            text_size="11sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.add_widget(self.action_toolbar)

    # =========================================================
    # PUBLIC TEMIZLEME
    # =========================================================
    def clear_selection(self) -> None:
        self.set_item(None)

    def clear_all(self) -> None:
        self._cancel_pending_set_item()

        try:
            self._yardimci().close_popups(self)
        except Exception:
            pass

        self.current_item = None
        self._new_code_buffer = ""

        self._set_text_on_widget(
            self.path_label,
            self._m("selected_function", "Seçili fonksiyon: -"),
        )

        self._set_text_on_widget(self.current_code_area, "")
        self._set_text_on_widget(self.new_code_area, "")

        try:
            if self.inline_notice is not None:
                self.inline_notice.hide_immediately()
        except Exception:
            pass

        self.refresh_language()
        self._set_status_info(self._m("app_ready", "Hazır."), 0)

    def set_new_code_text(self, text: str) -> None:
        self._set_new_code(text)

    # =========================================================
    # PUBLIC TEXT API
    # =========================================================
    def get_text(self) -> str:
        try:
            return str(self.new_code_area.text or "")
        except Exception:
            return ""

    def set_text(self, text: str) -> None:
        try:
            self._set_new_code(text)
        except Exception:
            try:
                if self.new_code_area is not None:
                    self.new_code_area.text = str(text or "")
            except Exception:
                pass

    def get_current_text(self) -> str:
        try:
            return str(self.current_code_area.text or "")
        except Exception:
            return ""

    # =========================================================
    # STATUS
    # =========================================================
    def _set_status_info(self, message="", line_no=0):
        self._yardimci().set_status_info(self, message, line_no)

    def _set_status_warning(self, message="", line_no=0):
        self._yardimci().set_status_warning(self, message, line_no)

    def _set_status_error(self, message="", line_no=0):
        self._yardimci().set_status_error(self, message, line_no)

    def _set_status_success(self, message="", line_no=0):
        self._yardimci().set_status_success(self, message, line_no)

    # =========================================================
    # INTERNAL
    # =========================================================
    def _cancel_pending_set_item(self) -> None:
        try:
            if self._pending_set_item_event is not None:
                self._pending_set_item_event.cancel()
        except Exception:
            pass
        self._pending_set_item_event = None

    def _item_path_text(self, item) -> str:
        if item is None:
            return "-"

        for attr_name in ("path", "name", "signature"):
            try:
                value = str(getattr(item, attr_name, "") or "").strip()
                if value:
                    return value
            except Exception:
                pass

        return "-"

    def _item_source_text(self, item) -> str:
        if item is None:
            return ""

        try:
            return str(getattr(item, "source", "") or "")
        except Exception:
            return ""

    def _widgetler_hazir_mi(self) -> bool:
        return bool(
            self.path_label is not None
            and self.current_code_area is not None
            and self.new_code_area is not None
            and self.inline_notice is not None
        )

    def _selected_function_prefix(self) -> str:
        text_value = self._m("selected_function", "Seçili fonksiyon: -")
        if ":" in text_value:
            return text_value.split(":", 1)[0].strip()
        return text_value.strip() or self._m("selected_prefix", "Seçildi")

    def _set_text_on_widget(self, widget, text: str) -> None:
        if widget is None:
            return

        try:
            if hasattr(widget, "set_text") and callable(widget.set_text):
                widget.set_text(str(text or ""))
                return
        except Exception:
            pass

        try:
            if hasattr(widget, "text"):
                widget.text = str(text or "")
        except Exception:
            pass

    def _set_hint_text_on_widget(self, widget, text: str) -> None:
        if widget is None:
            return

        try:
            if hasattr(widget, "set_hint_text") and callable(widget.set_hint_text):
                widget.set_hint_text(str(text or ""))
                return
        except Exception:
            pass

        try:
            if hasattr(widget, "hint_text"):
                widget.hint_text = str(text or "")
        except Exception:
            pass

    # =========================================================
    # KOD
    # =========================================================
    def _set_new_code(self, text) -> None:
        metin = self._dogrulama().normalize_code_text(
            text,
            trim_outer_blank_lines=True,
        )
        self._new_code_buffer = metin

        try:
            if self.new_code_area is not None:
                self.new_code_area.text = metin
                self.new_code_area.scroll_to_top()
                return
        except Exception:
            pass

        try:
            if self.new_code_area is not None:
                self.new_code_area.text = metin
        except Exception:
            pass

    def set_item(self, item) -> None:
        self._cancel_pending_set_item()
        self._set_item_serial += 1
        aktif_serial = int(self._set_item_serial)

        onceki_path = self._item_path_text(self.current_item)
        yeni_path = self._item_path_text(item)

        self.current_item = item

        try:
            if self.inline_notice is not None:
                self.inline_notice.hide_immediately()
        except Exception:
            pass

        self._set_status_info(self._m("app_ready", "Hazır."), 0)

        if item is None:
            try:
                self._yardimci().close_popups(self)
            except Exception:
                pass

            self._set_text_on_widget(
                self.path_label,
                self._m("selected_function", "Seçili fonksiyon: -"),
            )
            self._set_text_on_widget(self.current_code_area, "")
            self._set_text_on_widget(self.new_code_area, "")

            self._new_code_buffer = ""
            self.refresh_language()
            return

        self._set_text_on_widget(
            self.path_label,
            f"{self._selected_function_prefix()}: {yeni_path}",
        )

        if onceki_path != yeni_path:
            self._new_code_buffer = ""

        source_raw = self._item_source_text(item)
        new_buffer_raw = str(self._new_code_buffer or "")

        def _apply(_dt):
            if aktif_serial != int(self._set_item_serial):
                return

            if self.current_item is not item:
                return

            if not self._widgetler_hazir_mi():
                self._pending_set_item_event = Clock.schedule_once(_apply, 0.05)
                return

            try:
                current_text = self._dogrulama().normalize_code_text(
                    source_raw,
                    trim_outer_blank_lines=True,
                )
            except Exception:
                current_text = source_raw

            try:
                if new_buffer_raw.strip():
                    new_text = self._dogrulama().normalize_code_text(
                        new_buffer_raw,
                        trim_outer_blank_lines=True,
                    )
                else:
                    new_text = ""
            except Exception:
                new_text = new_buffer_raw

            self._set_text_on_widget(self.current_code_area, str(current_text or ""))
            self._set_text_on_widget(self.new_code_area, str(new_text or ""))

            try:
                self.current_code_area.scroll_to_top()
            except Exception:
                try:
                    self.current_code_area.scroll_y = 1
                except Exception:
                    pass

            try:
                self.new_code_area.scroll_to_top()
            except Exception:
                try:
                    self.new_code_area.scroll_y = 1
                except Exception:
                    pass

            try:
                self.refresh_language()
            except Exception:
                pass

            self._pending_set_item_event = None

        self._pending_set_item_event = Clock.schedule_once(_apply, 0.02)

    # =========================================================
    # AKSIYONLAR
    # =========================================================
    def _copy_current_to_new(self, *_args):
        return self._aksiyon().copy_current_to_new(self, *_args)

    def _paste_new_code(self, *_args):
        return self._aksiyon().paste_new_code(self, *_args)

    def _clear_new_code(self, *_args):
        return self._aksiyon().clear_new_code(self, *_args)

    def _check_new_code(self, *_args):
        return self._aksiyon().check_new_code(self, *_args)

    def _handle_update(self, *_args):
        return self._aksiyon().handle_update(self, *_args)

    def _handle_restore(self, *_args):
        return self._aksiyon().handle_restore(self, *_args)

    # =========================================================
    # POPUP
    # =========================================================
    def _open_current_code_popup(self, *_args):
        return self._popup().open_current_code_popup(self, *_args)

    def _open_new_code_editor_popup(self, *_args):
        return self._popup().open_new_code_editor_popup(self, *_args)

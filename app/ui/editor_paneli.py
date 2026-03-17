# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paneli.py

ROL:
- Seçilen fonksiyonun mevcut kodunu gösterir
- Yeni fonksiyon kodunu düzenletir
- Popup üzerinden geniş edit desteği verir
- Güncelleme öncesi temel doğrulama ve hata gösterimi yapar
- Son yedekten geri yükleme aksiyonunu tetikler
- Geçici bildirim servisi ile kısa aksiyon geri bildirimi üretir

NOT:
- Satır numarası kullanılmaz
- Kod en üst satırdan başlatılır
- Dış boş satırlar otomatik temizlenir
- Başarılı doğrulamada yeşil bilgi kutusu + pulse icon gösterilir

API 34 UYUMLULUK NOTU:
- Bu dosya doğrudan Android bridge çağrısı yapmaz
- AST, popup ve editör akışı platform bağımsızdır
- UI reset / scroll / popup kapanışları daha güvenli hale getirilmiştir

SURUM: 22
TARIH: 2026-03-17
IMZA: FY.
"""

from __future__ import annotations

import ast

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color
from kivy.graphics import Line
from kivy.graphics import RoundedRectangle
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.codeinput import CodeInput
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from pygments.lexers import PythonLexer

from app.services.gecici_bildirim_servisi import gecici_bildirim_servisi
from app.ui.icon_toolbar import IconToolbar
from app.ui.iconlu_baslik import IconluBaslik
from app.ui.tema import ACCENT, INPUT_BG, RADIUS_MD, TEXT_MUTED, TEXT_PRIMARY


# =========================================================
# BASE EDITOR
# =========================================================
class KodEditoru(CodeInput):
    """Temel Python editörü."""

    error_line = NumericProperty(0)

    def __init__(self, readonly=False, hint_text="", **kwargs):
        self.hint_text = str(hint_text or "")

        kwargs.setdefault("lexer", PythonLexer())
        kwargs.setdefault("readonly", readonly)
        kwargs.setdefault("multiline", True)
        kwargs.setdefault("do_wrap", False)
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_active", "")
        kwargs.setdefault("background_color", (0.07, 0.09, 0.12, 1))
        kwargs.setdefault("foreground_color", (0.96, 0.97, 1, 1))
        kwargs.setdefault("cursor_color", (1, 1, 1, 1))
        kwargs.setdefault("selection_color", (0.20, 0.35, 0.55, 0.45))
        kwargs.setdefault("font_size", "16sp")
        kwargs.setdefault("padding", (dp(12), dp(4), dp(12), dp(8)))
        kwargs.setdefault("write_tab", False)
        kwargs.setdefault("tab_width", 4)
        kwargs.setdefault("scroll_from_swipe", True)
        kwargs.setdefault("size_hint", (1, 1))
        kwargs.setdefault("style_name", "monokai")

        super().__init__(**kwargs)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        try:
            key = keycode[1]
        except Exception:
            return super().keyboard_on_key_down(window, keycode, text, modifiers)

        if not self.readonly and key == "enter":
            self._insert_auto_indent()
            return True

        if not self.readonly and key == "tab":
            self.insert_text("    ")
            return True

        return super().keyboard_on_key_down(window, keycode, text, modifiers)

    def _insert_auto_indent(self):
        try:
            _cursor_col, cursor_row = self.cursor
            lines = self.text.split("\n")
            current_line = lines[cursor_row] if 0 <= cursor_row < len(lines) else ""
            current_indent = current_line[: len(current_line) - len(current_line.lstrip(" "))]
            extra_indent = "    " if current_line.rstrip().endswith(":") else ""
            self.insert_text("\n" + current_indent + extra_indent)
        except Exception:
            self.insert_text("\n")

    def reset_view_to_top(self):
        try:
            self.cursor = (0, 0)
        except Exception:
            pass

        try:
            self.scroll_x = 0
        except Exception:
            pass

        try:
            self.scroll_y = 1
        except Exception:
            pass

    def scroll_to_top(self):
        self.reset_view_to_top()
        Clock.schedule_once(lambda *_: self.reset_view_to_top(), 0)
        Clock.schedule_once(lambda *_: self.reset_view_to_top(), 0.03)
        Clock.schedule_once(lambda *_: self.reset_view_to_top(), 0.08)

    def set_error_line(self, line_no: int):
        try:
            self.error_line = max(0, int(line_no or 0))
        except Exception:
            self.error_line = 0


# =========================================================
# PANELS
# =========================================================
class KodPaneli(BoxLayout):
    def __init__(self, bg=INPUT_BG, border=(0.18, 0.24, 0.34, 1), **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            self._bg_color = Color(*tuple(bg))
            self._bg_rect = RoundedRectangle(radius=[dp(RADIUS_MD)])

        with self.canvas.after:
            self._border_color = Color(*tuple(border))
            self._border_line = Line(
                rounded_rectangle=(0, 0, 0, 0, dp(RADIUS_MD)),
                width=1.1,
            )

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

    def _update_canvas(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._border_line.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(RADIUS_MD),
        )


class BilgiKutusu(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            padding=(dp(12), dp(8)),
            spacing=dp(10),
            **kwargs,
        )

        self._pulse_anim = None
        self._pulse_stop_event = None

        self._bg_info = (0.10, 0.16, 0.22, 1)
        self._bg_success = (0.08, 0.24, 0.14, 1)
        self._bg_warning = (0.24, 0.18, 0.08, 1)
        self._bg_error = (0.24, 0.12, 0.12, 1)

        with self.canvas.before:
            self._bg_color = Color(*self._bg_info)
            self._bg_rect = RoundedRectangle(radius=[dp(12)])

        with self.canvas.after:
            self._border_color = Color(0.20, 0.24, 0.30, 1)
            self._border_line = Line(
                rounded_rectangle=(0, 0, 0, 0, dp(12)),
                width=1.0,
            )

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

        self.status_icon = Image(
            source="app/assets/icons/onaylandi.png",
            size_hint=(None, None),
            size=(dp(22), dp(22)),
            opacity=0,
            allow_stretch=True,
            keep_ratio=True,
        )
        self.add_widget(self.status_icon)

        self.label = Label(
            text="Hazır.",
            halign="left",
            valign="middle",
            color=(0.88, 0.94, 1, 1),
            font_size="13sp",
            shorten=True,
            shorten_from="right",
        )
        self.label.bind(size=self._sync_label_size)
        self.add_widget(self.label)

    def _update_canvas(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._border_line.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(12),
        )

    def _sync_label_size(self, widget, size):
        widget.text_size = (size[0], None)

    def _cancel_pulse_stop_event(self):
        try:
            if self._pulse_stop_event is not None:
                self._pulse_stop_event.cancel()
        except Exception:
            pass
        self._pulse_stop_event = None

    def _stop_pulse(self):
        self._cancel_pulse_stop_event()
        try:
            if self._pulse_anim is not None:
                self._pulse_anim.cancel(self.status_icon)
        except Exception:
            pass
        self._pulse_anim = None

        try:
            self.status_icon.opacity = 1 if self.status_icon.source else 0
            self.status_icon.size = (dp(22), dp(22))
        except Exception:
            pass

    def _start_pulse(self, seconds: float | None = None):
        self._stop_pulse()
        try:
            self.status_icon.opacity = 1
            self.status_icon.size = (dp(22), dp(22))
            anim = (
                Animation(opacity=0.68, size=(dp(26), dp(26)), duration=0.45)
                + Animation(opacity=1.0, size=(dp(22), dp(22)), duration=0.45)
            )
            anim.repeat = seconds is None
            anim.start(self.status_icon)
            self._pulse_anim = anim

            if seconds is not None:
                self._pulse_stop_event = Clock.schedule_once(
                    lambda *_: self._stop_pulse(),
                    max(0.1, float(seconds)),
                )
        except Exception:
            self.status_icon.opacity = 1

    def _hide_icon(self):
        self._stop_pulse()
        self.status_icon.opacity = 0

    def set_text(self, text: str):
        self.label.text = str(text or "")

    def set_info(self, text: str):
        self.set_text(text)
        self._hide_icon()
        self._bg_color.rgba = self._bg_info
        self._border_color.rgba = (0.20, 0.24, 0.30, 1)
        self.label.color = (0.88, 0.94, 1, 1)

    def set_neutral(self):
        self.set_info("Hazır.")

    def set_success(self, text: str, pulse_seconds: float = 6.0):
        self.set_text(text)
        self._bg_color.rgba = self._bg_success
        self._border_color.rgba = (0.14, 0.30, 0.20, 1)
        self.label.color = (0.76, 1.00, 0.82, 1)
        self._start_pulse(seconds=pulse_seconds)

    def set_warning(self, text: str):
        self.set_text(text)
        self._hide_icon()
        self._bg_color.rgba = self._bg_warning
        self._border_color.rgba = (0.34, 0.24, 0.08, 1)
        self.label.color = (1.00, 0.92, 0.72, 1)

    def set_error(self, text: str):
        self.set_text(text)
        self._hide_icon()
        self._bg_color.rgba = self._bg_error
        self._border_color.rgba = (0.34, 0.14, 0.14, 1)
        self.label.color = (1, 0.78, 0.78, 1)


class SadeKodAlani(KodPaneli):
    def __init__(self, readonly=False, hint_text="", **kwargs):
        super().__init__(
            orientation="vertical",
            padding=dp(4),
            bg=INPUT_BG,
            border=(0.18, 0.24, 0.34, 1),
            **kwargs,
        )
        self.editor = KodEditoru(readonly=readonly, hint_text=hint_text)
        self.add_widget(self.editor)

    @property
    def text(self):
        return self.editor.text

    @text.setter
    def text(self, value):
        self.editor.text = str(value or "")
        self.editor.scroll_to_top()

    def scroll_to_top(self):
        self.editor.scroll_to_top()

    def set_error_line(self, line_no: int):
        self.editor.set_error_line(line_no)


# =========================================================
# MAIN PANEL
# =========================================================
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

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
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

        self.new_code_area = SadeKodAlani(
            readonly=False,
            hint_text="Tam fonksiyon kodunu buraya yaz veya yapıştır.",
            size_hint_y=0.66,
        )
        self.add_widget(self.new_code_area)

        self._build_action_toolbar()

    def _build_title_row(
        self,
        title: str,
        icon_name: str,
        action_icon: str,
        action_text: str,
        callback,
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

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------
    def clear_selection(self) -> None:
        self.set_item(None)

    def clear_all(self) -> None:
        self._close_popups()
        self.current_item = None
        self._new_code_buffer = ""
        self.path_label.set_text("Seçili fonksiyon: -")
        self.current_code_area.text = ""
        self.new_code_area.text = ""
        self._set_status_info("Hazır.", 0)

    def set_new_code_text(self, text: str) -> None:
        self._set_new_code(text)

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------
    def _toast(self, text: str, icon_name: str = "", duration: float = 2.2) -> None:
        try:
            gecici_bildirim_servisi.show(
                text=str(text or ""),
                icon_name=str(icon_name or ""),
                duration=float(duration or 2.2),
            )
        except Exception:
            pass

    def _close_popups(self) -> None:
        for attr in ("_current_popup", "_editor_popup"):
            popup = getattr(self, attr, None)
            if popup is not None:
                try:
                    popup.dismiss()
                except Exception:
                    pass
            setattr(self, attr, None)

    def _normalize_code_text(self, text, trim_outer_blank_lines=False) -> str:
        metin = str(text or "").replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ")

        if trim_outer_blank_lines:
            satirlar = metin.split("\n")
            while satirlar and not satirlar[0].strip():
                satirlar.pop(0)
            while satirlar and not satirlar[-1].strip():
                satirlar.pop()
            metin = "\n".join(satirlar)

        return metin

    def _first_meaningful_line(self, text: str) -> str:
        for line in self._normalize_code_text(text, trim_outer_blank_lines=True).split("\n"):
            s = line.strip()
            if s and not s.startswith("#"):
                return s
        return ""

    def _looks_like_full_function(self, text: str) -> bool:
        line = self._first_meaningful_line(text)
        return line.startswith("def ") or line.startswith("async def ")

    def _basic_parse_check(self, text: str) -> None:
        mod = ast.parse(text)
        if len(mod.body) != 1:
            raise ValueError("Yeni kod tam olarak tek bir fonksiyon içermelidir.")
        if not isinstance(mod.body[0], (ast.FunctionDef, ast.AsyncFunctionDef)):
            raise ValueError("Yeni kod yalnızca tek bir def veya async def içermelidir.")

    def _extract_line_number(self, exc) -> int:
        try:
            if getattr(exc, "lineno", None):
                return int(exc.lineno)
        except Exception:
            pass
        return 0

    def _set_status_info(self, message="", line_no=0):
        temiz = str(message or "").strip() or "Hazır."
        self.error_box.set_info(temiz)
        try:
            self.new_code_area.set_error_line(line_no)
        except Exception:
            pass

    def _set_status_warning(self, message="", line_no=0):
        temiz = str(message or "").strip() or "Uyarı."
        self.error_box.set_warning(temiz)
        try:
            self.new_code_area.set_error_line(line_no)
        except Exception:
            pass

    def _set_status_error(self, message="", line_no=0):
        temiz = str(message or "").strip() or "Hata oluştu."
        self.error_box.set_error(temiz)
        try:
            self.new_code_area.set_error_line(line_no)
        except Exception:
            pass

    def _set_status_success(self, message="", line_no=0):
        temiz = str(message or "").strip() or "Doğrulama doğru."
        self.error_box.set_success(temiz, pulse_seconds=6.0)
        try:
            self.new_code_area.set_error_line(line_no)
        except Exception:
            pass

    def _set_popup_error(self, label, editor_area, message="", line_no=0):
        temiz = str(message or "").strip()
        label.text = temiz if temiz else "Hazır."
        label.color = (1, 0.78, 0.78, 1) if temiz else (0.88, 0.94, 1, 1)

        try:
            editor_area.set_error_line(line_no)
        except Exception:
            pass

    def _set_new_code(self, text) -> None:
        metin = self._normalize_code_text(text, trim_outer_blank_lines=True)
        self._new_code_buffer = metin
        self.new_code_area.text = metin
        self.new_code_area.scroll_to_top()

    def _validate_new_code(self, text: str) -> tuple[bool, str, int]:
        yeni = self._normalize_code_text(text, trim_outer_blank_lines=True)

        if not yeni.strip():
            return False, "Yeni kod alanı boş bırakılamaz.", 0

        ilk_satir = yeni.split("\n")[0].strip() if yeni else ""
        if not (ilk_satir.startswith("def ") or ilk_satir.startswith("async def ")):
            return False, "Fonksiyon tanımı 1. satırda başlamalıdır.", 1

        if not self._looks_like_full_function(yeni):
            return False, "Kodun ilk anlamlı satırı 'def' veya 'async def' olmalıdır.", 1

        try:
            self._basic_parse_check(yeni)
        except SyntaxError as exc:
            return (
                False,
                f"Sözdizimi hatası: satır {exc.lineno}, sütun {exc.offset} -> {exc.msg}",
                self._extract_line_number(exc),
            )
        except ValueError as exc:
            return False, str(exc), 1
        except Exception as exc:
            return False, str(exc), self._extract_line_number(exc)

        return True, "", 0

    # ---------------------------------------------------------
    # ITEM
    # ---------------------------------------------------------
    def set_item(self, item) -> None:
        onceki_path = str(getattr(self.current_item, "path", "") or "")
        yeni_path = str(getattr(item, "path", "") or "")

        self.current_item = item
        self._set_status_info("Hazır.", 0)

        if item is None:
            self._close_popups()
            self.path_label.set_text("Seçili fonksiyon: -")
            self.current_code_area.text = ""
            self.new_code_area.text = ""
            self._new_code_buffer = ""
            return

        self.path_label.set_text(f"Seçili fonksiyon: {getattr(item, 'path', '-')}")
        self.current_code_area.text = self._normalize_code_text(
            getattr(item, "source", ""),
            trim_outer_blank_lines=True,
        )
        self.current_code_area.scroll_to_top()

        if onceki_path != yeni_path:
            self._new_code_buffer = ""

        self.new_code_area.text = (
            self._normalize_code_text(self._new_code_buffer, trim_outer_blank_lines=True)
            if self._new_code_buffer.strip()
            else ""
        )
        self.new_code_area.scroll_to_top()

    # ---------------------------------------------------------
    # ACTIONS
    # ---------------------------------------------------------
    def _copy_current_to_new(self, *_args):
        self._set_new_code(self.current_code_area.text)
        self._set_status_info("Mevcut kod yeni alana kopyalandı.", 0)
        self._toast("Kod düzenleme alanına kopyalandı.", "file_copy.png", 2.4)

    def _clear_new_code(self, *_args):
        self._set_new_code("")
        self._set_status_info("Yeni kod alanı temizlendi.", 0)
        self._toast("Yeni kod alanı temizlendi.", "clear.png", 2.0)

    def _check_new_code(self, *_args):
        ok, hata, satir = self._validate_new_code(self.new_code_area.text)
        if ok:
            self._set_status_success("Doğrulama doğru.", 0)
            self._toast("Kod doğrulaması başarılı.", "code_check.png", 2.2)
        else:
            self._set_status_error(hata, satir)
            self._toast("Kod doğrulaması başarısız.", "warning.png", 2.2)

    def _handle_update(self, *_args):
        if not self.on_update or self.current_item is None:
            self._set_status_warning("Güncellenecek öğe seçilmedi.", 0)
            self._toast("Önce fonksiyon seçmelisiniz.", "warning.png", 2.0)
            return

        yeni = self._normalize_code_text(self.new_code_area.text, trim_outer_blank_lines=True)
        self._new_code_buffer = yeni

        ok, hata, satir = self._validate_new_code(yeni)
        if not ok:
            self._set_status_error(hata, satir)
            self._toast("Güncelleme öncesi doğrulama başarısız.", "warning.png", 2.2)
            return

        try:
            self._set_status_info("Güncelleme uygulanıyor...", 0)
            self.on_update(self.current_item, yeni)
            self._set_status_success("Güncelleme tamamlandı.", 0)
            self._toast("Fonksiyon güncellendi.", "upload.png", 2.4)
        except Exception as exc:
            self._set_status_error(str(exc), self._extract_line_number(exc))
            self._toast("Güncelleme hatası oluştu.", "error.png", 2.4)

    def _handle_restore(self, *_args):
        if not self.on_restore:
            self._set_status_warning("Geri yükleme callback bağlı değil.", 0)
            self._toast("Geri yükleme servisi bağlı değil.", "warning.png", 2.0)
            return

        try:
            self._set_status_info("Geri yükleme uygulanıyor...", 0)
            self.on_restore()
            self._set_status_success("Geri yükleme tamamlandı.", 0)
            self._toast("Son yedekten geri yükleme tamamlandı.", "geri_yukle.png", 2.4)
        except Exception as exc:
            self._set_status_error(str(exc), self._extract_line_number(exc))
            self._toast("Geri yükleme hatası oluştu.", "error.png", 2.4)

    # ---------------------------------------------------------
    # POPUPS
    # ---------------------------------------------------------
    def _build_popup_toolbar(self, actions):
        toolbar = IconToolbar(spacing_dp=20, padding_dp=4)
        toolbar.size_hint_y = None
        toolbar.height = dp(86)

        refs = {}
        for key, icon, text, callback in actions:
            refs[key] = toolbar.add_tool(
                icon_name=icon,
                text=text,
                on_release=callback,
                icon_size_dp=42,
                text_size="11sp" if len(text) > 7 else "12sp",
                color=TEXT_MUTED,
                icon_bg=None,
            )
        return toolbar, refs

    def _open_current_code_popup(self, *_args):
        if self._current_popup is not None or self.current_item is None:
            return

        if not str(self.current_code_area.text or "").strip():
            return

        ana = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))

        kod_alani = SadeKodAlani(readonly=True, size_hint=(1, 1))
        kod_alani.text = self._normalize_code_text(
            self.current_code_area.text,
            trim_outer_blank_lines=True,
        )
        kod_alani.scroll_to_top()
        ana.add_widget(kod_alani)

        toolbar, refs = self._build_popup_toolbar([
            ("close", "cancel.png", "Kapat", lambda *_: None),
        ])
        ana.add_widget(toolbar)

        popup = Popup(
            title=f"Mevcut Kod - {getattr(self.current_item, 'path', '-')}",
            content=ana,
            size_hint=(0.96, 0.96),
            auto_dismiss=False,
            separator_color=ACCENT,
        )
        self._current_popup = popup

        refs["close"].bind(on_release=lambda *_: popup.dismiss())
        popup.bind(on_dismiss=lambda *_: setattr(self, "_current_popup", None))
        popup.open()

    def _open_new_code_editor_popup(self, *_args):
        if self._editor_popup is not None or self.current_item is None:
            return

        ana = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))

        editor_area = SadeKodAlani(
            readonly=False,
            hint_text="Tam fonksiyon kodunu yaz",
            size_hint=(1, 1),
        )
        editor_area.text = self._normalize_code_text(
            self._new_code_buffer or self.new_code_area.text or "",
            trim_outer_blank_lines=True,
        )
        editor_area.scroll_to_top()
        ana.add_widget(editor_area)

        popup_error = Label(
            text="Hazır.",
            size_hint_y=None,
            height=dp(26),
            halign="left",
            valign="middle",
            color=(0.88, 0.94, 1, 1),
            font_size="13sp",
            shorten=True,
            shorten_from="right",
        )
        popup_error.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0] - dp(8), None))
        )
        ana.add_widget(popup_error)

        toolbar, refs = self._build_popup_toolbar([
            ("copy", "file_copy.png", "Mevcudu Al", lambda *_: None),
            ("save", "onaylandi.png", "Kaydet", lambda *_: None),
            ("cancel", "cancel.png", "İptal", lambda *_: None),
        ])
        ana.add_widget(toolbar)

        popup = Popup(
            title=f"Yeni Kod Düzenle - {getattr(self.current_item, 'path', '-')}",
            content=ana,
            size_hint=(0.96, 0.96),
            auto_dismiss=False,
            separator_color=ACCENT,
        )
        self._editor_popup = popup

        def mevcuttan_al(*_args):
            self._set_popup_error(popup_error, editor_area, "", 0)
            editor_area.text = self._normalize_code_text(
                self.current_code_area.text,
                trim_outer_blank_lines=True,
            )
            editor_area.scroll_to_top()

        def kaydet(*_args):
            yeni = self._normalize_code_text(editor_area.text, trim_outer_blank_lines=True)
            ok, hata, satir = self._validate_new_code(yeni)

            if not ok:
                self._set_popup_error(popup_error, editor_area, hata, satir)
                return

            self._set_popup_error(popup_error, editor_area, "", 0)
            self._set_new_code(yeni)
            popup.dismiss()
            self._set_status_success("Doğrulama doğru.", 0)
            self._toast("Yeni kod düzenleme alanına aktarıldı.", "onaylandi.png", 2.2)

        refs["copy"].bind(on_release=mevcuttan_al)
        refs["save"].bind(on_release=kaydet)
        refs["cancel"].bind(on_release=lambda *_: popup.dismiss())

        popup.bind(on_dismiss=lambda *_: setattr(self, "_editor_popup", None))
        popup.open()


# =========================================================
# ROOT UYUMLULUK KATMANI
# =========================================================
class RootWidget(EditorPaneli):
    """
    RootWidget bekleyen yerler için doğrudan kullanılabilir uyum sınıfı.
    """

    def __init__(self, on_update=None, on_restore=None, **kwargs):
        super().__init__(
            on_update=on_update or self._dummy_update,
            on_restore=on_restore or self._dummy_restore,
            **kwargs,
        )

    def _dummy_update(self, item, yeni_kod):
        self._set_status_error("on_update callback bağlı değil.", 0)

    def _dummy_restore(self):
        self._set_status_error("on_restore callback bağlı değil.", 0)

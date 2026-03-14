# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paneli.py

ROL:
- Seçilen fonksiyonun mevcut kodunu gösterir
- Yeni fonksiyon kodunu düzenletir
- Popup üzerinden geniş edit desteği verir
- Güncelleme öncesi temel doğrulama ve hata gösterimi yapar

MİMARİ:
- Kendi görünümünü kendi çizer
- Root sadece item ve callback verir
- Mobilde üst üste binmeyen, dengeli yerleşim kullanır
"""

from __future__ import annotations

import ast

from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.codeinput import CodeInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from pygments.lexers import PythonLexer

from app.ui.iconlu_baslik import IconluBaslik
from app.ui.iconlu_buton import IconluButon
from app.ui.tema import (
    ACCENT,
    CARD_BG,
    CARD_BG_DARK,
    CARD_BG_SOFT,
    DANGER,
    INPUT_BG,
    RADIUS_MD,
    SUCCESS,
    TEXT_MUTED,
    TEXT_PRIMARY,
)


class KodEditoru(CodeInput):
    """Python kod düzenleme alanı."""

    error_line = NumericProperty(0)
    line_number_label = ObjectProperty(None)

    def __init__(self, readonly=False, **kwargs):
        super().__init__(
            lexer=PythonLexer(),
            readonly=readonly,
            multiline=True,
            do_wrap=False,
            background_normal="",
            background_active="",
            background_color=(0, 0, 0, 0),
            foreground_color=TEXT_PRIMARY,
            cursor_color=TEXT_PRIMARY,
            selection_color=(0.20, 0.35, 0.55, 0.45),
            font_size="14sp",
            padding=(dp(10), dp(8), dp(10), dp(8)),
            scroll_from_swipe=True,
            write_tab=False,
            tab_width=4,
            **kwargs,
        )

        self.bind(text=self._sync_line_numbers)
        self.bind(size=self._sync_line_numbers)
        self.bind(pos=self._sync_line_numbers)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        key = keycode[1]

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

            current_line = ""
            if 0 <= cursor_row < len(lines):
                current_line = lines[cursor_row]

            current_indent = current_line[: len(current_line) - len(current_line.lstrip(" "))]
            extra = ""

            if current_line.rstrip().endswith(":"):
                extra = "    "

            self.insert_text("\n" + current_indent + extra)
        except Exception:
            self.insert_text("\n")

    def _sync_line_numbers(self, *_args):
        if not self.line_number_label:
            return

        try:
            line_count = max(1, len(self.text.split("\n")))
            self.line_number_label.text = "\n".join(str(i) for i in range(1, line_count + 1))
        except Exception:
            self.line_number_label.text = "1"

    def set_error_line(self, line_no: int):
        try:
            self.error_line = max(0, int(line_no or 0))
        except Exception:
            self.error_line = 0


class KodPaneli(BoxLayout):
    """Kod alanı için ortak kart görünümü."""

    def __init__(self, bg=INPUT_BG, border=(0.16, 0.20, 0.28, 1), **kwargs):
        super().__init__(**kwargs)

        self._bg_rgba = tuple(bg)
        self._border_rgba = tuple(border)

        with self.canvas.before:
            self._bg_color = Color(*self._bg_rgba)
            self._bg_rect = RoundedRectangle(radius=[dp(RADIUS_MD)])

        with self.canvas.after:
            self._border_color = Color(*self._border_rgba)
            self._border_line = Line(
                rounded_rectangle=(0, 0, 0, 0, dp(RADIUS_MD)),
                width=1.0,
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
    """Hata / bilgi mesajı alanı."""

    def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(36),
            padding=(dp(10), dp(6)),
            **kwargs,
        )

        with self.canvas.before:
            self._bg_color = Color(0.10, 0.16, 0.22, 1)
            self._bg_rect = RoundedRectangle(radius=[dp(12)])

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

        self.label = Label(
            text="Hazır.",
            halign="left",
            valign="middle",
            color=(0.82, 0.90, 1, 1),
            font_size="12sp",
            shorten=True,
            shorten_from="right",
        )
        self.label.bind(size=self._sync_label_size)
        self.add_widget(self.label)

    def _update_canvas(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _sync_label_size(self, widget, size):
        widget.text_size = (size[0], None)

    def set_text(self, text: str):
        self.label.text = str(text or "")

    def set_error(self, is_error: bool):
        if is_error:
            self._bg_color.rgba = (0.24, 0.12, 0.12, 1)
            self.label.color = (1, 0.78, 0.78, 1)
        else:
            self._bg_color.rgba = (0.10, 0.16, 0.22, 1)
            self.label.color = (0.82, 0.90, 1, 1)


class SadeKodAlani(KodPaneli):
    """Salt okunur veya düz kod alanı."""

    def __init__(self, readonly=False, hint_text="", **kwargs):
        super().__init__(
            orientation="vertical",
            padding=dp(4),
            bg=INPUT_BG,
            border=(0.16, 0.20, 0.28, 1),
            **kwargs,
        )

        self.editor = KodEditoru(
            readonly=readonly,
            hint_text=hint_text,
        )
        self.add_widget(self.editor)

    @property
    def text(self):
        return self.editor.text

    @text.setter
    def text(self, value):
        self.editor.text = str(value or "")

    def set_error_line(self, line_no: int):
        self.editor.set_error_line(line_no)


class SatirNumaraliKodAlani(KodPaneli):
    """Satır numaralı kod alanı."""

    def __init__(self, readonly=False, hint_text="", **kwargs):
        super().__init__(
            orientation="horizontal",
            spacing=dp(0),
            padding=dp(4),
            bg=INPUT_BG,
            border=(0.16, 0.20, 0.28, 1),
            **kwargs,
        )

        self.line_numbers = Label(
            text="1",
            size_hint_x=None,
            width=dp(34),
            halign="right",
            valign="top",
            color=(0.46, 0.52, 0.62, 1),
            text_size=(dp(28), None),
            padding=(0, dp(8)),
            font_size="12sp",
        )

        self.editor = KodEditoru(
            readonly=readonly,
            hint_text=hint_text,
        )
        self.editor.line_number_label = self.line_numbers
        self.editor._sync_line_numbers()

        self.add_widget(self.line_numbers)
        self.add_widget(self.editor)

    @property
    def text(self):
        return self.editor.text

    @text.setter
    def text(self, value):
        self.editor.text = str(value or "")
        self.editor._sync_line_numbers()

    def set_error_line(self, line_no: int):
        self.editor.set_error_line(line_no)


class EditorPaneli(BoxLayout):
    """Seçili fonksiyonun görüntülenmesi ve güncellenmesi için ana panel."""

    def __init__(self, on_update, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=dp(8),
            **kwargs,
        )

        self.on_update = on_update
        self.current_item = None
        self._new_code_buffer = ""
        self._current_popup = None
        self._editor_popup = None

        self._build_ui()
        self._set_error("", 0)

    # =========================================================
    # UI
    # =========================================================
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

        self.current_title_row = self._build_title_row(
            title="Mevcut Kod",
            icon_name="visibility_on.png",
            button_icon="visibility_on.png",
            callback=self._open_current_code_popup,
        )
        self.add_widget(self.current_title_row)

        self.current_code_area = SadeKodAlani(
            readonly=True,
            size_hint_y=0.34,
        )
        self.add_widget(self.current_code_area)

        self.new_title_row = self._build_title_row(
            title="Yeni Fonksiyon Kodu",
            icon_name="edit.png",
            button_icon="edit.png",
            callback=self._open_new_code_editor_popup,
        )
        self.add_widget(self.new_title_row)

        self.new_code_area = SatirNumaraliKodAlani(
            readonly=False,
            hint_text="Tam fonksiyon kodunu buraya yaz veya yapıştır.\nÖrnek:\ndef ornek(...):\n    pass",
            size_hint_y=0.66,
        )
        self.add_widget(self.new_code_area)

        self._build_action_grid()

    def _build_title_row(self, title: str, icon_name: str, button_icon: str, callback):
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(42),
            spacing=dp(8),
        )

        title_widget = IconluBaslik(
            text=title,
            icon_name=icon_name,
            height_dp=36,
            font_size="14sp",
            color=(0.75, 0.85, 1, 1),
            size_hint_x=1,
        )
        row.add_widget(title_widget)

        btn = IconluButon(
            text="",
            icon_name=button_icon,
            bg=CARD_BG,
            size_hint=(None, None),
            size=(dp(44), dp(44)),
            height_dp=44,
            icon_width_dp=20,
        )
        btn.bind(on_release=callback)
        row.add_widget(btn)

        if title == "Mevcut Kod":
            self.view_popup_button = btn
        else:
            self.edit_popup_button = btn

        return row

    def _build_action_grid(self) -> None:
        self.action_grid = GridLayout(
            cols=2,
            size_hint_y=None,
            height=dp(116),
            spacing=dp(8),
        )

        self.copy_button = IconluButon(
            text="Kopyala",
            icon_name="file_copy.png",
            bg=CARD_BG,
            icon_width_dp=22,
            height_dp=54,
        )
        self.copy_button.bind(on_release=self._copy_current_to_new)
        self.action_grid.add_widget(self.copy_button)

        self.clear_button = IconluButon(
            text="Temizle",
            icon_name="clear.png",
            bg=DANGER,
            icon_width_dp=22,
            height_dp=54,
        )
        self.clear_button.bind(on_release=self._clear_new_code)
        self.action_grid.add_widget(self.clear_button)

        self.fold_button = IconluButon(
            text="Katla",
            icon_name="visibility_on.png",
            bg=CARD_BG_SOFT,
            icon_width_dp=22,
            height_dp=54,
        )
        self.fold_button.bind(on_release=self._show_fold_not_supported)
        self.action_grid.add_widget(self.fold_button)

        self.update_button = IconluButon(
            text="Güncelle",
            icon_name="upload.png",
            bg=SUCCESS,
            icon_width_dp=22,
            height_dp=54,
        )
        self.update_button.bind(on_release=self._handle_update)
        self.action_grid.add_widget(self.update_button)

        self.add_widget(self.action_grid)

    # =========================================================
    # HELPERS
    # =========================================================
    def _normalize_code_text(self, text, trim_outer_blank_lines=False) -> str:
        metin = str(text or "")
        metin = metin.replace("\r\n", "\n").replace("\r", "\n")
        metin = metin.replace("\t", "    ")

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
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                continue
            return stripped
        return ""

    def _looks_like_full_function(self, text: str) -> bool:
        ilk = self._first_meaningful_line(text)
        if not ilk:
            return False
        return ilk.startswith("def ") or ilk.startswith("async def ")

    def _basic_parse_check(self, text: str) -> None:
        mod = ast.parse(text)

        if len(mod.body) != 1:
            raise ValueError("Yeni kod tam olarak tek bir fonksiyon içermelidir.")

        node = mod.body[0]
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            raise ValueError("Yeni kod yalnızca tek bir def veya async def içermelidir.")

    def _extract_line_number(self, exc) -> int:
        try:
            if hasattr(exc, "lineno") and exc.lineno:
                return int(exc.lineno)
        except Exception:
            pass

        msg = str(exc or "")
        for token in msg.replace(",", " ").replace(":", " ").split():
            if token.isdigit():
                try:
                    return int(token)
                except Exception:
                    pass
        return 0

    def _set_error(self, message="", line_no=0):
        temiz = str(message or "").strip()

        if temiz:
            self.error_box.set_text(temiz)
            self.error_box.set_error(True)
        else:
            self.error_box.set_text("Hazır.")
            self.error_box.set_error(False)

        try:
            self.new_code_area.set_error_line(line_no)
        except Exception:
            pass

    def _set_popup_error(self, label, editor_area, message="", line_no=0):
        try:
            temiz = str(message or "").strip()
            label.text = temiz if temiz else "Hazır."
            label.color = (1, 0.78, 0.78, 1) if temiz else (0.82, 0.90, 1, 1)
        except Exception:
            pass

        try:
            editor_area.set_error_line(line_no)
        except Exception:
            pass

    def _set_new_code(self, text) -> None:
        metin = self._normalize_code_text(text, trim_outer_blank_lines=True)
        self._new_code_buffer = metin
        self.new_code_area.text = metin

    def _validate_new_code(self, text: str) -> tuple[bool, str, int]:
        yeni_kod = self._normalize_code_text(text, trim_outer_blank_lines=True)

        if not yeni_kod.strip():
            return False, "Yeni kod alanı boş bırakılamaz", 0

        if not self._looks_like_full_function(yeni_kod):
            return False, "Kodun ilk anlamlı satırı 'def' veya 'async def' olmalıdır.", 1

        try:
            self._basic_parse_check(yeni_kod)
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

    # =========================================================
    # ITEM
    # =========================================================
    def set_item(self, item) -> None:
        onceki_path = str(getattr(self.current_item, "path", "") or "")
        yeni_path = str(getattr(item, "path", "") or "")

        self.current_item = item
        self._set_error("", 0)

        if item is None:
            self.path_label.set_text("Seçili fonksiyon: -")
            self.current_code_area.text = ""
            self._new_code_buffer = ""
            self.new_code_area.text = ""
            return

        self.path_label.set_text(f"Seçili fonksiyon: {item.path}")
        self.current_code_area.text = self._normalize_code_text(
            getattr(item, "source", ""),
            trim_outer_blank_lines=True,
        )

        if onceki_path != yeni_path:
            self._new_code_buffer = ""

        if self._new_code_buffer.strip():
            self.new_code_area.text = self._normalize_code_text(
                self._new_code_buffer,
                trim_outer_blank_lines=True,
            )
        else:
            self.new_code_area.text = ""

    # =========================================================
    # ACTIONS
    # =========================================================
    def _copy_current_to_new(self, *_args):
        self._set_error("", 0)
        self._set_new_code(self.current_code_area.text)

    def _clear_new_code(self, *_args):
        self._set_error("", 0)
        self._set_new_code("")

    def _show_fold_not_supported(self, *_args):
        self._set_error("Gerçek kod katlama bu editörde yerleşik değil. Custom widget gerekir.", 0)

    def _handle_update(self, *_args):
        if not self.on_update or self.current_item is None:
            return

        yeni_kod = self._normalize_code_text(
            self.new_code_area.text,
            trim_outer_blank_lines=True,
        )
        self._new_code_buffer = yeni_kod

        ok, hata, hata_satiri = self._validate_new_code(yeni_kod)
        if not ok:
            self._set_error(hata, hata_satiri)
            return

        try:
            self._set_error("", 0)
            self.on_update(self.current_item, yeni_kod)
        except Exception as exc:
            self._set_error(str(exc), self._extract_line_number(exc))

    # =========================================================
    # POPUP: MEVCUT KOD
    # =========================================================
    def _open_current_code_popup(self, *_args):
        if self._current_popup is not None:
            return

        if not self.current_item or not str(self.current_code_area.text or "").strip():
            return

        ana = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(8),
        )

        kod_alani = SadeKodAlani(readonly=True)
        kod_alani.text = self._normalize_code_text(
            self.current_code_area.text,
            trim_outer_blank_lines=True,
        )
        ana.add_widget(kod_alani)

        alt_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(52),
            spacing=dp(8),
        )

        kapat_btn = IconluButon(
            text="Kapat",
            icon_name="cancel.png",
            bg=DANGER,
        )
        alt_bar.add_widget(kapat_btn)
        ana.add_widget(alt_bar)

        popup = Popup(
            title=f"Mevcut Kod - {self.current_item.path}",
            content=ana,
            size_hint=(0.96, 0.96),
            auto_dismiss=False,
            separator_color=ACCENT,
        )
        self._current_popup = popup

        def kapat(*_args):
            popup.dismiss()

        def popup_kapandi(*_args):
            self._current_popup = None

        kapat_btn.bind(on_release=kapat)
        popup.bind(on_dismiss=popup_kapandi)
        popup.open()

    # =========================================================
    # POPUP: YENİ KOD EDİTÖRÜ
    # =========================================================
    def _open_new_code_editor_popup(self, *_args):
        if self._editor_popup is not None:
            return

        if self.current_item is None:
            return

        ana = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(8),
        )

        editor_area = SatirNumaraliKodAlani(
            readonly=False,
            hint_text="Tam fonksiyon kodunu yaz",
        )
        editor_area.text = self._normalize_code_text(
            self._new_code_buffer or self.new_code_area.text or "",
            trim_outer_blank_lines=True,
        )
        ana.add_widget(editor_area)

        popup_error = Label(
            text="Hazır.",
            size_hint_y=None,
            height=dp(24),
            halign="left",
            valign="middle",
            color=(0.82, 0.90, 1, 1),
            text_size=(0, None),
            shorten=True,
            shorten_from="right",
            font_size="12sp",
        )
        popup_error.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0] - dp(8), None))
        )
        ana.add_widget(popup_error)

        alt_bar = GridLayout(
            cols=2,
            size_hint_y=None,
            height=dp(112),
            spacing=dp(8),
        )

        mevcuttan_kopyala_btn = IconluButon(
            text="Mevcudu Al",
            icon_name="file_copy.png",
            bg=CARD_BG,
            height_dp=52,
        )
        alt_bar.add_widget(mevcuttan_kopyala_btn)

        kaydet_btn = IconluButon(
            text="Kaydet",
            icon_name="onaylandi.png",
            bg=SUCCESS,
            height_dp=52,
        )
        alt_bar.add_widget(kaydet_btn)

        iptal_btn = IconluButon(
            text="İptal",
            icon_name="cancel.png",
            bg=DANGER,
            height_dp=52,
        )
        alt_bar.add_widget(iptal_btn)

        bos = Label(text="")
        alt_bar.add_widget(bos)

        ana.add_widget(alt_bar)

        popup = Popup(
            title=f"Yeni Kod Düzenle - {self.current_item.path}",
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

        def kaydet(*_args):
            yeni_metin = self._normalize_code_text(
                editor_area.text,
                trim_outer_blank_lines=True,
            )

            ok, hata, hata_satiri = self._validate_new_code(yeni_metin)
            if not ok:
                self._set_popup_error(popup_error, editor_area, hata, hata_satiri)
                return

            self._set_popup_error(popup_error, editor_area, "", 0)
            self._set_new_code(yeni_metin)
            popup.dismiss()

        def iptal(*_args):
            popup.dismiss()

        def popup_kapandi(*_args):
            self._editor_popup = None

        mevcuttan_kopyala_btn.bind(on_release=mevcuttan_al)
        kaydet_btn.bind(on_release=kaydet)
        iptal_btn.bind(on_release=iptal)
        popup.bind(on_dismiss=popup_kapandi)

        popup.open()
# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/popup/editor_popuplari.py

ROL:
- Editör paneli için popup içeriklerini oluşturmak
- Mevcut kod görüntüleme popup'ını açmak
- Yeni kod düzenleme popup'ını açmak
- Popup içinden doğrulama ve ana alana aktarma akışını yönetmek

MİMARİ:
- Üst katman bu modüle doğrudan değil, popup/yoneticisi.py üzerinden erişmelidir
- Bileşen, doğrulama ve yardımcı akışlar ilgili yöneticiler üzerinden çağrılır
- Popup yaşam döngüsü panel üzerinde tutulur
- Davranış korunur, bağımlılıklar sadeleştirilmiştir

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 2
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from app.ui.icon_toolbar import IconToolbar
from app.ui.tema import ACCENT, TEXT_MUTED


def _bilesenler():
    from app.ui.editor_paketi.bilesenler import BilesenlerYoneticisi
    return BilesenlerYoneticisi()


def _dogrulama():
    from app.ui.editor_paketi.dogrulama import DogrulamaYoneticisi
    return DogrulamaYoneticisi()


def _yardimci():
    from app.ui.editor_paketi.yardimci import YardimciYoneticisi
    return YardimciYoneticisi()


def build_popup_toolbar(actions):
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


def open_current_code_popup(panel, *_args):
    if panel._current_popup is not None or panel.current_item is None:
        return

    if not str(panel.current_code_area.text or "").strip():
        return

    ana = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))

    kod_alani = _bilesenler().sade_kod_alani_olustur(readonly=True, size_hint=(1, 1))
    kod_alani.text = _dogrulama().normalize_code_text(
        panel.current_code_area.text,
        trim_outer_blank_lines=True,
    )
    kod_alani.scroll_to_top()
    ana.add_widget(kod_alani)

    toolbar, refs = build_popup_toolbar([
        ("close", "cancel.png", "Kapat", lambda *_: None),
    ])
    ana.add_widget(toolbar)

    popup = Popup(
        title=f"Mevcut Kod - {getattr(panel.current_item, 'path', '-')}",
        content=ana,
        size_hint=(0.96, 0.96),
        auto_dismiss=False,
        separator_color=ACCENT,
    )
    panel._current_popup = popup

    refs["close"].bind(on_release=lambda *_: popup.dismiss())
    popup.bind(on_dismiss=lambda *_: setattr(panel, "_current_popup", None))
    popup.open()


def open_new_code_editor_popup(panel, *_args):
    if panel._editor_popup is not None or panel.current_item is None:
        return

    ana = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))

    editor_area = _bilesenler().sade_kod_alani_olustur(
        readonly=False,
        hint_text="Tam fonksiyon kodunu yaz",
        size_hint=(1, 1),
    )
    editor_area.text = _dogrulama().normalize_code_text(
        panel._new_code_buffer or panel.new_code_area.text or "",
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

    toolbar, refs = build_popup_toolbar([
        ("copy", "file_copy.png", "Mevcudu Al", lambda *_: None),
        ("save", "onaylandi.png", "Kaydet", lambda *_: None),
        ("cancel", "cancel.png", "İptal", lambda *_: None),
    ])
    ana.add_widget(toolbar)

    popup = Popup(
        title=f"Yeni Kod Düzenle - {getattr(panel.current_item, 'path', '-')}",
        content=ana,
        size_hint=(0.96, 0.96),
        auto_dismiss=False,
        separator_color=ACCENT,
    )
    panel._editor_popup = popup

    def mevcuttan_al(*_args):
        _yardimci().set_popup_error(popup_error, editor_area, "", 0)
        editor_area.text = _dogrulama().normalize_code_text(
            panel.current_code_area.text,
            trim_outer_blank_lines=True,
        )
        editor_area.scroll_to_top()

    def kaydet(*_args):
        yeni = _dogrulama().normalize_code_text(
            editor_area.text,
            trim_outer_blank_lines=True,
        )
        ok, hata, satir = _dogrulama().validate_new_code(yeni)

        if not ok:
            _yardimci().set_popup_error(popup_error, editor_area, hata, satir)
            return

        _yardimci().set_popup_error(popup_error, editor_area, "", 0)
        panel._set_new_code(yeni)
        popup.dismiss()

        _yardimci().set_status_success(panel, "Doğrulama doğru.", 0)
        _yardimci().show_inline_notice(
            panel,
            title="Yeni kod güncellendi",
            text="Popup içindeki düzenleme ana yeni kod alanına aktarıldı.",
            icon_name="onaylandi.png",
            tone="success",
            duration=3.8,
            on_tap=lambda: panel.new_code_area.scroll_to_top(),
        )
        _yardimci().toast("Yeni kod düzenleme alanına aktarıldı.", "onaylandi.png", 2.2)

    refs["copy"].bind(on_release=mevcuttan_al)
    refs["save"].bind(on_release=kaydet)
    refs["cancel"].bind(on_release=lambda *_: popup.dismiss())

    popup.bind(on_dismiss=lambda *_: setattr(panel, "_editor_popup", None))
    popup.open()
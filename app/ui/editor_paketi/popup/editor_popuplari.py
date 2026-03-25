# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/popup/editor_popuplari.py

ROL:
- Editör paneli için popup içeriklerini oluşturmak
- Mevcut kod görüntüleme popup'ını açmak
- Yeni kod düzenleme popup'ını açmak
- Popup içinden doğrulama ve ana alana aktarma akışını yönetmek
- Görünen metinlerde services tabanlı dil desteğine hazır olmak
- Panodan yapıştırılan içeriklerde güvenli normalize akışı uygulamak
- Boşluk / satır başı-sonu / sekme / satır sonu farklarını güvenli biçimde temizlemek

MİMARİ:
- Üst katman bu modüle doğrudan değil, popup/yoneticisi.py üzerinden erişmelidir
- Bileşen, doğrulama ve yardımcı akışlar ilgili yöneticiler üzerinden çağrılır
- Popup yaşam döngüsü panel üzerinde tutulur
- Davranış korunur, bağımlılıklar sadeleştirilmiştir
- services verilirse sabit metinler dil servisi üzerinden alınabilir
- services verilmezse güvenli fallback ile çalışır
- Clipboard içeriği yoksa veya erişilemezse fail-soft davranır
- Kullanıcıya görünen sabit metinler _m(...) ile çözülür

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 4
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

from kivy.core.clipboard import Clipboard
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


def _services_from_panel(panel):
    try:
        services = getattr(panel, "services", None)
        if services is not None:
            return services
    except Exception:
        pass

    try:
        parent = getattr(panel, "parent", None)
        while parent is not None:
            services = getattr(parent, "services", None)
            if services is not None:
                return services
            parent = getattr(parent, "parent", None)
    except Exception:
        pass

    return None


def _m(panel, anahtar: str, default: str = "") -> str:
    try:
        services = _services_from_panel(panel)
        if services is not None:
            return str(services.metin(anahtar, default) or default or anahtar)
    except Exception:
        pass
    return str(default or anahtar)


def _normalize_text(text, trim_outer_blank_lines: bool = True) -> str:
    try:
        return _dogrulama().normalize_code_text(
            text,
            trim_outer_blank_lines=trim_outer_blank_lines,
        )
    except Exception:
        metin = str(text or "")
        metin = metin.replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ")

        if trim_outer_blank_lines:
            satirlar = metin.split("\n")

            while satirlar and not satirlar[0].strip():
                satirlar.pop(0)

            while satirlar and not satirlar[-1].strip():
                satirlar.pop()

            metin = "\n".join(satirlar)

        return metin


def _safe_scroll_to_top(widget) -> None:
    try:
        if widget is not None and hasattr(widget, "scroll_to_top"):
            widget.scroll_to_top()
    except Exception:
        pass


def _safe_popup_title_path(panel) -> str:
    try:
        return str(getattr(getattr(panel, "current_item", None), "path", "-") or "-")
    except Exception:
        return "-"


def _safe_clipboard_text() -> str:
    try:
        raw = Clipboard.paste()
    except Exception:
        raw = ""

    try:
        if raw is None:
            return ""
        return str(raw)
    except Exception:
        return ""


def _is_blank_text(text: str) -> bool:
    return not str(text or "").strip()


def build_popup_toolbar(actions):
    toolbar = IconToolbar(spacing_dp=20, padding_dp=4)
    toolbar.size_hint_y = None
    toolbar.height = dp(86)

    refs = {}
    for key, icon, text, callback in actions:
        refs[key] = toolbar.add_tool(
            icon_name=icon,
            text=str(text or ""),
            on_release=callback,
            icon_size_dp=42,
            text_size="11sp" if len(str(text or "")) > 7 else "12sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )
    return toolbar, refs


def open_current_code_popup(panel, *_args):
    if panel._current_popup is not None or panel.current_item is None:
        return

    if _is_blank_text(getattr(panel.current_code_area, "text", "")):
        return

    ana = BoxLayout(
        orientation="vertical",
        spacing=dp(8),
        padding=dp(8),
    )

    kod_alani = _bilesenler().sade_kod_alani_olustur(
        readonly=True,
        size_hint=(1, 1),
    )
    kod_alani.text = _normalize_text(
        getattr(panel.current_code_area, "text", ""),
        trim_outer_blank_lines=True,
    )
    _safe_scroll_to_top(kod_alani)
    ana.add_widget(kod_alani)

    toolbar, refs = build_popup_toolbar(
        [
            (
                "close",
                "cancel.png",
                _m(panel, "close", "Kapat"),
                lambda *_: None,
            ),
        ]
    )
    ana.add_widget(toolbar)

    popup = Popup(
        title=(
            f"{_m(panel, 'current_code_title', 'Mevcut Kod')} - "
            f"{_safe_popup_title_path(panel)}"
        ),
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

    ana = BoxLayout(
        orientation="vertical",
        spacing=dp(8),
        padding=dp(8),
    )

    editor_area = _bilesenler().sade_kod_alani_olustur(
        readonly=False,
        hint_text=_m(
            panel,
            "new_function_hint",
            "Tam fonksiyon kodunu buraya yaz veya yapıştır.",
        ),
        size_hint=(1, 1),
    )
    editor_area.text = _normalize_text(
        getattr(panel, "_new_code_buffer", "") or getattr(panel.new_code_area, "text", ""),
        trim_outer_blank_lines=True,
    )
    _safe_scroll_to_top(editor_area)
    ana.add_widget(editor_area)

    popup_error = Label(
        text=_m(panel, "app_ready", "Hazır."),
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

    toolbar, refs = build_popup_toolbar(
        [
            (
                "copy_current",
                "file_copy.png",
                _m(panel, "take_current_code", "Mevcudu Al"),
                lambda *_: None,
            ),
            (
                "paste_clipboard",
                "edit.png",
                _m(panel, "paste", "Yapıştır"),
                lambda *_: None,
            ),
            (
                "save",
                "onaylandi.png",
                _m(panel, "save", "Kaydet"),
                lambda *_: None,
            ),
            (
                "cancel",
                "cancel.png",
                _m(panel, "cancel", "İptal"),
                lambda *_: None,
            ),
        ]
    )
    ana.add_widget(toolbar)

    popup = Popup(
        title=(
            f"{_m(panel, 'edit_new_code_title', 'Yeni Kod Düzenle')} - "
            f"{_safe_popup_title_path(panel)}"
        ),
        content=ana,
        size_hint=(0.96, 0.96),
        auto_dismiss=False,
        separator_color=ACCENT,
    )
    panel._editor_popup = popup

    def _set_popup_info(message_key: str, default: str) -> None:
        _yardimci().set_popup_error(
            popup_error,
            editor_area,
            _m(panel, message_key, default),
            0,
        )

    def mevcuttan_al(*_args):
        try:
            editor_area.text = _normalize_text(
                getattr(panel.current_code_area, "text", ""),
                trim_outer_blank_lines=True,
            )
            _safe_scroll_to_top(editor_area)
            _set_popup_info(
                "current_code_copied_to_new",
                "Mevcut kod yeni alana kopyalandı.",
            )
        except Exception:
            _yardimci().set_popup_error(
                popup_error,
                editor_area,
                _m(panel, "an_error_occurred", "Bir hata oluştu"),
                0,
            )

    def panodan_yapistir(*_args):
        try:
            pano_text = _safe_clipboard_text()
            if _is_blank_text(pano_text):
                _yardimci().set_popup_error(
                    popup_error,
                    editor_area,
                    _m(
                        panel,
                        "clipboard_empty_or_unavailable",
                        "Pano boş veya erişilemedi.",
                    ),
                    0,
                )
                return

            temiz = _normalize_text(pano_text, trim_outer_blank_lines=True)
            if _is_blank_text(temiz):
                _yardimci().set_popup_error(
                    popup_error,
                    editor_area,
                    _m(
                        panel,
                        "clipboard_content_invalid",
                        "Pano içeriği geçerli kod içermiyor.",
                    ),
                    0,
                )
                return

            editor_area.text = temiz
            _safe_scroll_to_top(editor_area)
            _yardimci().set_popup_error(
                popup_error,
                editor_area,
                _m(
                    panel,
                    "clipboard_pasted",
                    "Pano içeriği düzenleyiciye yapıştırıldı.",
                ),
                0,
            )
        except Exception:
            _yardimci().set_popup_error(
                popup_error,
                editor_area,
                _m(
                    panel,
                    "clipboard_paste_failed",
                    "Panodan yapıştırma başarısız oldu.",
                ),
                0,
            )

    def kaydet(*_args):
        yeni = _normalize_text(
            getattr(editor_area, "text", ""),
            trim_outer_blank_lines=True,
        )

        if _is_blank_text(yeni):
            _yardimci().set_popup_error(
                popup_error,
                editor_area,
                _m(
                    panel,
                    "validation_error_new_code_empty",
                    "Yeni kod alanı boş bırakılamaz.",
                ),
                0,
            )
            return

        ok, hata, satir = _dogrulama().validate_new_code(yeni)

        if not ok:
            _yardimci().set_popup_error(popup_error, editor_area, hata, satir)
            return

        _yardimci().set_popup_error(popup_error, editor_area, "", 0)
        panel._set_new_code(yeni)
        popup.dismiss()

        _yardimci().set_status_success(
            panel,
            _m(panel, "validation_correct", "Doğrulama doğru."),
            0,
        )
        _yardimci().show_inline_notice(
            panel,
            title=_m(panel, "new_code_updated", "Yeni kod güncellendi"),
            text=_m(
                panel,
                "popup_edit_transferred_to_main_area",
                "Popup içindeki düzenleme ana yeni kod alanına aktarıldı.",
            ),
            icon_name="onaylandi.png",
            tone="success",
            duration=3.8,
            on_tap=lambda: _safe_scroll_to_top(panel.new_code_area),
        )
        _yardimci().toast(
            _m(
                panel,
                "new_code_transferred_to_editor_area",
                "Yeni kod düzenleme alanına aktarıldı.",
            ),
            "onaylandi.png",
            2.2,
        )

    refs["copy_current"].bind(on_release=mevcuttan_al)
    refs["paste_clipboard"].bind(on_release=panodan_yapistir)
    refs["save"].bind(on_release=kaydet)
    refs["cancel"].bind(on_release=lambda *_: popup.dismiss())

    popup.bind(on_dismiss=lambda *_: setattr(panel, "_editor_popup", None))
    popup.open()

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/aksiyon/editor_aksiyonlari.py

ROL:
- Editör panelindeki kullanıcı aksiyonlarını yürütür
- Kopyalama, yapıştırma, temizleme, doğrulama, güncelleme ve geri yükleme akışlarını yönetir
- Bildirim ve durum güncellemelerini ilgili yöneticiler üzerinden tetikler
- Aktif dile göre kullanıcıya görünen metinleri üretir
- Panodan gelen görünmeyen / bozucu karakterleri temizler
- Yapıştırma akışında güvenli fallback zinciri uygular

MİMARİ:
- Doğrudan üst katman tarafından değil, aksiyon/yoneticisi.py üzerinden kullanılmalıdır
- Doğrulama ve yardımcı akışlar alt paket yöneticileri üzerinden çağrılır
- Panel davranışı korunur
- Çeviri metinleri panel._m(...) hattından çözülür
- Fail-soft yaklaşım korunur

SURUM: 9
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations

from kivy.core.clipboard import Clipboard

from app.ui.editor_paketi.dogrulama import DogrulamaYoneticisi
from app.ui.editor_paketi.yardimci import YardimciYoneticisi


_DOGRULAMA = DogrulamaYoneticisi()
_YARDIMCI = YardimciYoneticisi()


def _m(panel, anahtar: str, default: str = "") -> str:
    """
    Panel üzerindeki çeviri hattını kullanır.
    """
    try:
        metod = getattr(panel, "_m", None)
        if callable(metod):
            return str(metod(anahtar, default) or default or anahtar)
    except Exception:
        pass
    return str(default or anahtar)


def _safe_scroll_to_top(widget) -> None:
    """
    Widget içinde mümkünse en üste kaydırır.
    """
    try:
        metod = getattr(widget, "scroll_to_top", None)
        if callable(metod):
            metod()
    except Exception:
        pass


def _safe_scroll_to_end(widget) -> None:
    """
    Widget içinde mümkünse en alta kaydırır.
    """
    try:
        metod = getattr(widget, "scroll_to_bottom", None)
        if callable(metod):
            metod()
            return
    except Exception:
        pass

    try:
        if widget is not None and hasattr(widget, "scroll_y"):
            widget.scroll_y = 0
    except Exception:
        pass


def _current_item_display_text(panel) -> str:
    """
    Mevcut item için kullanıcıya gösterilecek metni döndürür.
    """
    try:
        return str(_YARDIMCI.current_item_display(panel) or "").strip() or "-"
    except Exception:
        return "-"


def _resolve_template_text(panel, anahtar: str, default: str = "", **values) -> str:
    """
    Çeviri metni içindeki placeholder alanlarını güvenli şekilde doldurur.
    """
    metin = _m(panel, anahtar, default)

    try:
        for key, value in values.items():
            metin = metin.replace("{" + str(key) + "}", str(value))
    except Exception:
        pass

    return str(metin or default or "")


def _normalize_clipboard_text(value) -> str:
    """
    Panodan gelen metni görünmeyen / bozucu karakterlerden temizler.
    """
    try:
        metin = str(value or "")
    except Exception:
        return ""

    try:
        metin = metin.replace("\r\n", "\n").replace("\r", "\n")
    except Exception:
        pass

    try:
        metin = metin.replace("\u2028", "\n").replace("\u2029", "\n")
    except Exception:
        pass

    try:
        metin = metin.replace("\ufeff", "")
        metin = metin.replace("\u200b", "")
        metin = metin.replace("\u200c", "")
        metin = metin.replace("\u200d", "")
        metin = metin.replace("\u2060", "")
    except Exception:
        pass

    try:
        metin = metin.replace("\xa0", " ")
    except Exception:
        pass

    try:
        metin = metin.replace("\t", "    ")
    except Exception:
        pass

    try:
        satirlar = str(metin).split("\n")
        temiz_satirlar = []

        for satir in satirlar:
            try:
                temiz_satir = str(satir or "").rstrip()
            except Exception:
                temiz_satir = ""

            temiz_satirlar.append(temiz_satir)

        metin = "\n".join(temiz_satirlar)
    except Exception:
        pass

    try:
        metin = _DOGRULAMA.normalize_code_text(
            metin,
            trim_outer_blank_lines=True,
        )
    except Exception:
        try:
            metin = str(metin or "").strip("\n")
        except Exception:
            pass

    return str(metin or "")


def _get_new_code_widget(panel):
    """
    Yeni kod alanı widget'ını döndürür.
    """
    try:
        return getattr(panel, "new_code_area", None)
    except Exception:
        return None


def _focus_widget(widget) -> None:
    """
    Mümkünse widget veya iç editörü odaklar.
    """
    if widget is None:
        return

    try:
        editor = getattr(widget, "editor", None)
        if editor is not None and hasattr(editor, "focus"):
            editor.focus = True
            return
    except Exception:
        pass

    try:
        if hasattr(widget, "focus"):
            widget.focus = True
            return
    except Exception:
        pass

    try:
        editor_input = getattr(widget, "editor_input", None)
        if editor_input is not None:
            editor_input.focus = True
    except Exception:
        pass


def _get_widget_text(widget) -> str:
    """
    Widget içindeki mevcut metni uyumlu biçimde okur.
    """
    if widget is None:
        return ""

    try:
        editor = getattr(widget, "editor", None)
        if editor is not None:
            return str(getattr(editor, "text", "") or "")
    except Exception:
        pass

    for method_name in ("get_text", "metni_al", "icerik_al", "kod_al"):
        try:
            method = getattr(widget, method_name, None)
            if callable(method):
                return str(method() or "")
        except Exception:
            continue

    try:
        editor_input = getattr(widget, "editor_input", None)
        if editor_input is not None:
            return str(getattr(editor_input, "text", "") or "")
    except Exception:
        pass

    for attr_name in ("text", "metin", "content", "icerik", "code"):
        try:
            if hasattr(widget, attr_name):
                return str(getattr(widget, attr_name, "") or "")
        except Exception:
            continue

    return ""


def _set_widget_text(widget, text: str) -> bool:
    """
    Widget içine metin yazmayı dener.
    """
    if widget is None:
        return False

    temiz = str(text or "")

    try:
        editor = getattr(widget, "editor", None)
        if editor is not None and hasattr(editor, "text"):
            editor.text = temiz
            return True
    except Exception:
        pass

    for method_name in ("set_text", "metni_yaz", "icerik_yaz", "kod_yaz"):
        try:
            method = getattr(widget, method_name, None)
            if callable(method):
                method(temiz)
                return True
        except Exception:
            continue

    try:
        editor_input = getattr(widget, "editor_input", None)
        if editor_input is not None and hasattr(editor_input, "text"):
            editor_input.text = temiz
            return True
    except Exception:
        pass

    for attr_name in ("text", "metin", "content", "icerik", "code"):
        try:
            if hasattr(widget, attr_name):
                setattr(widget, attr_name, temiz)
                return True
        except Exception:
            continue

    return False


def _try_widget_native_paste(widget) -> bool:
    """
    Widget'ın kendi yerel paste davranışını çağırmayı dener.
    """
    if widget is None:
        return False

    adaylar = (
        "paste",
        "do_paste",
        "_paste",
        "insert_clipboard",
        "paste_from_clipboard",
    )

    try:
        editor = getattr(widget, "editor", None)
        if editor is not None:
            for method_name in adaylar:
                try:
                    method = getattr(editor, method_name, None)
                    if callable(method):
                        try:
                            method()
                            return True
                        except TypeError:
                            method(None)
                            return True
                except Exception:
                    continue
    except Exception:
        pass

    for method_name in adaylar:
        try:
            method = getattr(widget, method_name, None)
            if callable(method):
                try:
                    method()
                    return True
                except TypeError:
                    method(None)
                    return True
        except Exception:
            continue

    try:
        editor_input = getattr(widget, "editor_input", None)
        if editor_input is not None:
            for method_name in adaylar:
                try:
                    method = getattr(editor_input, method_name, None)
                    if callable(method):
                        try:
                            method()
                            return True
                        except TypeError:
                            method(None)
                            return True
                except Exception:
                    continue
    except Exception:
        pass

    return False


def _try_widget_insert_text(widget, text: str) -> bool:
    """
    Widget / TextInput insert_text akışını dener.
    """
    if widget is None:
        return False

    temiz = str(text or "")
    if not temiz:
        return False

    try:
        editor = getattr(widget, "editor", None)
        if editor is not None:
            insert_text = getattr(editor, "insert_text", None)
            if callable(insert_text):
                insert_text(temiz)
                return True
    except Exception:
        pass

    try:
        insert_text = getattr(widget, "insert_text", None)
        if callable(insert_text):
            insert_text(temiz)
            return True
    except Exception:
        pass

    try:
        editor_input = getattr(widget, "editor_input", None)
        if editor_input is not None:
            insert_text = getattr(editor_input, "insert_text", None)
            if callable(insert_text):
                insert_text(temiz)
                return True
    except Exception:
        pass

    return False


def _clipboard_text() -> str:
    """
    Panodan metin almayı dener.
    """
    adaylar = (
        "text/plain;charset=utf-8",
        "UTF8_STRING",
        "text/plain",
        "STRING",
        "TEXT",
    )

    for target in adaylar:
        try:
            metin = Clipboard.get(target)
            metin = _normalize_clipboard_text(metin)
            if metin:
                return metin
        except Exception:
            continue

    try:
        metin = Clipboard.paste()
        metin = _normalize_clipboard_text(metin)
        if metin:
            return metin
    except Exception:
        pass

    return ""


def _panel_set_new_code(panel, text: str) -> bool:
    """
    Panelin kendi güvenli set akışını kullanır.
    """
    try:
        temiz = _DOGRULAMA.normalize_code_text(
            text,
            trim_outer_blank_lines=True,
        )
    except Exception:
        temiz = _normalize_clipboard_text(text)

    try:
        metod = getattr(panel, "_set_new_code", None)
        if callable(metod):
            metod(temiz)
            return True
    except Exception:
        pass

    try:
        widget = _get_new_code_widget(panel)
        if widget is not None:
            return _set_widget_text(widget, temiz)
    except Exception:
        pass

    return False


def _write_clipboard_text_safely(panel, widget, clipboard_text: str) -> bool:
    """
    Panodaki metni normalize edip güvenli biçimde yazar.
    """
    try:
        temiz = _normalize_clipboard_text(clipboard_text)
        if not temiz:
            return False

        yazildi = _panel_set_new_code(panel, temiz)
        if yazildi:
            try:
                _focus_widget(widget)
            except Exception:
                pass

            try:
                _safe_scroll_to_end(widget)
            except Exception:
                pass

            return True
    except Exception:
        pass

    return False


def _show_paste_success(panel, widget, detay_key: str, detay_default: str) -> None:
    """
    Yapıştırma başarı bildirimlerini tek yerde toplar.
    """
    _YARDIMCI.set_status_success(
        panel,
        _m(panel, "clipboard_pasted", "Pano içeriği yapıştırıldı."),
        0,
    )
    _YARDIMCI.show_inline_notice(
        panel,
        title=_m(panel, "paste_completed", "Yapıştırma tamamlandı"),
        text=_m(panel, detay_key, detay_default),
        icon_name="yapistir.png",
        tone="success",
        duration=3.6,
        on_tap=lambda: _safe_scroll_to_end(widget),
    )
    _YARDIMCI.toast(
        text=_m(panel, "clipboard_pasted", "Pano içeriği yapıştırıldı."),
        icon_name="yapistir.png",
        duration=2.2,
        panel=panel,
    )


def copy_current_to_new(panel, *_args):
    """
    Mevcut kodu yeni kod alanına kopyalar.
    """
    panel._set_new_code(panel.current_code_area.text)

    _YARDIMCI.set_status_info(
        panel,
        _m(panel, "current_code_copied_to_new", "Mevcut kod yeni alana kopyalandı."),
        0,
    )
    _YARDIMCI.show_inline_notice(
        panel,
        title=_m(panel, "code_copied", "Kod kopyalandı"),
        text=_m(
            panel,
            "current_function_copied_to_edit_area",
            "Mevcut fonksiyon yeni düzenleme alanına aktarıldı.",
        ),
        icon_name="file_copy.png",
        tone="info",
        duration=3.2,
        on_tap=lambda: _safe_scroll_to_top(panel.new_code_area),
    )
    _YARDIMCI.toast(
        text=_m(panel, "code_copied_to_edit_area", "Kod düzenleme alanına kopyalandı."),
        icon_name="file_copy.png",
        duration=2.4,
        panel=panel,
    )


def paste_new_code(panel, *_args):
    """
    Yeni kod alanına pano içeriğini yapıştırır.
    """
    widget = _get_new_code_widget(panel)
    if widget is None:
        _YARDIMCI.set_status_warning(
            panel,
            _m(panel, "paste_target_not_found", "Yapıştırma alanı bulunamadı."),
            0,
        )
        _YARDIMCI.show_inline_notice(
            panel,
            title=_m(panel, "paste_could_not_be_done", "Yapıştırma yapılamadı"),
            text=_m(
                panel,
                "paste_target_missing",
                "Yeni kod alanı bulunamadığı için yapıştırma işlemi yapılamadı.",
            ),
            icon_name="warning.png",
            tone="warning",
            duration=3.8,
        )
        _YARDIMCI.toast(
            text=_m(panel, "paste_could_not_be_done", "Yapıştırma yapılamadı."),
            icon_name="warning.png",
            duration=2.0,
            panel=panel,
        )
        return

    clipboard_text = _clipboard_text()
    if not clipboard_text:
        _YARDIMCI.set_status_warning(
            panel,
            _m(panel, "clipboard_empty_or_unavailable", "Pano boş veya erişilemedi."),
            0,
        )
        _YARDIMCI.show_inline_notice(
            panel,
            title=_m(panel, "clipboard_empty_title", "Pano boş"),
            text=_m(
                panel,
                "clipboard_empty_detail",
                "Panoda yeni kod alanına yapıştırılabilecek bir metin bulunamadı.",
            ),
            icon_name="warning.png",
            tone="warning",
            duration=3.8,
        )
        _YARDIMCI.toast(
            text=_m(panel, "clipboard_empty_or_unavailable", "Pano boş veya erişilemedi."),
            icon_name="warning.png",
            duration=2.0,
            panel=panel,
        )
        return

    try:
        _focus_widget(widget)
    except Exception:
        pass

    try:
        onceki = _get_widget_text(widget)
        native_ok = _try_widget_native_paste(widget)
        sonraki = _get_widget_text(widget)

        if native_ok and str(sonraki) != str(onceki):
            if _write_clipboard_text_safely(panel, widget, sonraki):
                _show_paste_success(
                    panel,
                    widget,
                    "clipboard_pasted_into_new_code_area",
                    "Pano içeriği yeni kod alanına yapıştırıldı.",
                )
                return
    except Exception:
        pass

    try:
        onceki = _get_widget_text(widget)
        insert_ok = _try_widget_insert_text(widget, clipboard_text)
        sonraki = _get_widget_text(widget)

        if insert_ok and str(sonraki) != str(onceki):
            if _write_clipboard_text_safely(panel, widget, sonraki):
                _show_paste_success(
                    panel,
                    widget,
                    "clipboard_pasted_into_new_code_area",
                    "Pano içeriği yeni kod alanına yapıştırıldı.",
                )
                return
    except Exception:
        pass

    try:
        if _write_clipboard_text_safely(panel, widget, clipboard_text):
            _show_paste_success(
                panel,
                widget,
                "clipboard_pasted_with_safe_fallback",
                "Pano içeriği güvenli yapıştırma yöntemiyle yeni kod alanına aktarıldı.",
            )
            return
    except Exception:
        pass

    _YARDIMCI.set_status_warning(
        panel,
        _m(panel, "clipboard_paste_failed", "Panodan yapıştırma başarısız oldu."),
        0,
    )
    _YARDIMCI.show_inline_notice(
        panel,
        title=_m(panel, "paste_could_not_be_done", "Yapıştırma yapılamadı"),
        text=_m(
            panel,
            "paste_failed_try_long_press",
            "Bu içerik kontrol panelinden yapıştırılamadı. Yeni kod alanında uzun basıp Yapıştır seçeneğini deneyin.",
        ),
        icon_name="warning.png",
        tone="warning",
        duration=4.5,
        on_tap=lambda: _safe_scroll_to_top(widget),
    )
    _YARDIMCI.toast(
        text=_m(panel, "clipboard_paste_failed", "Panodan yapıştırma başarısız oldu."),
        icon_name="warning.png",
        duration=2.2,
        panel=panel,
    )


def clear_new_code(panel, *_args):
    """
    Yeni kod alanını temizler.
    """
    panel._set_new_code("")

    _YARDIMCI.set_status_info(
        panel,
        _m(panel, "new_code_area_cleared", "Yeni kod alanı temizlendi."),
        0,
    )
    _YARDIMCI.show_inline_notice(
        panel,
        title=_m(panel, "area_cleared", "Alan temizlendi"),
        text=_m(
            panel,
            "new_function_code_area_emptied",
            "Yeni fonksiyon kodu alanı boşaltıldı.",
        ),
        icon_name="clear.png",
        tone="info",
        duration=3.0,
        on_tap=lambda: _safe_scroll_to_top(panel.new_code_area),
    )
    _YARDIMCI.toast(
        text=_m(panel, "new_code_area_cleared", "Yeni kod alanı temizlendi."),
        icon_name="clear.png",
        duration=2.0,
        panel=panel,
    )


def check_new_code(panel, *_args):
    """
    Yeni kod alanını doğrular.
    """
    ok, hata, satir = _DOGRULAMA.validate_new_code(panel.new_code_area.text)

    if ok:
        _YARDIMCI.set_status_success(
            panel,
            _m(panel, "validation_correct", "Doğrulama doğru."),
            0,
        )
        _YARDIMCI.show_inline_notice(
            panel,
            title=_m(panel, "validation_successful", "Doğrulama başarılı"),
            text=_m(
                panel,
                "new_function_structure_valid",
                "Yeni fonksiyon yapısı geçerli görünüyor.",
            ),
            icon_name="code_check.png",
            tone="success",
            duration=3.6,
            on_tap=lambda: _safe_scroll_to_top(panel.new_code_area),
        )
        _YARDIMCI.toast(
            text=_m(panel, "code_validation_successful", "Kod doğrulaması başarılı."),
            icon_name="code_check.png",
            duration=2.2,
            panel=panel,
        )
        return

    _YARDIMCI.set_status_error(panel, hata, satir)
    _YARDIMCI.show_inline_notice(
        panel,
        title=_m(panel, "validation_error", "Doğrulama hatası"),
        text=hata,
        icon_name="warning.png",
        tone="error",
        duration=4.2,
        on_tap=lambda: _safe_scroll_to_top(panel.new_code_area),
    )
    _YARDIMCI.toast(
        text=_m(panel, "code_validation_failed", "Kod doğrulaması başarısız."),
        icon_name="warning.png",
        duration=2.2,
        panel=panel,
    )


def handle_update(panel, *_args):
    """
    Güncelleme akışını yürütür.
    """
    if not panel.on_update or panel.current_item is None:
        _YARDIMCI.set_status_warning(
            panel,
            _m(panel, "no_item_selected_to_update", "Güncellenecek öğe seçilmedi."),
            0,
        )
        _YARDIMCI.show_inline_notice(
            panel,
            title=_m(panel, "update_could_not_be_done", "Güncelleme yapılamadı"),
            text=_m(
                panel,
                "select_function_before_update",
                "Önce güncellenecek fonksiyonu seçmelisiniz.",
            ),
            icon_name="warning.png",
            tone="warning",
            duration=3.8,
        )
        _YARDIMCI.toast(
            text=_m(panel, "select_function_first", "Önce fonksiyon seçmelisiniz."),
            icon_name="warning.png",
            duration=2.0,
            panel=panel,
        )
        return

    yeni = _DOGRULAMA.normalize_code_text(
        panel.new_code_area.text,
        trim_outer_blank_lines=True,
    )
    panel._new_code_buffer = yeni

    ok, hata, satir = _DOGRULAMA.validate_new_code(yeni)
    if not ok:
        _YARDIMCI.set_status_error(panel, hata, satir)
        _YARDIMCI.show_inline_notice(
            panel,
            title=_m(panel, "pre_update_error", "Güncelleme öncesi hata"),
            text=hata,
            icon_name="warning.png",
            tone="error",
            duration=4.2,
            on_tap=lambda: _safe_scroll_to_top(panel.new_code_area),
        )
        _YARDIMCI.toast(
            text=_m(
                panel,
                "pre_update_validation_failed",
                "Güncelleme öncesi doğrulama başarısız.",
            ),
            icon_name="warning.png",
            duration=2.2,
            panel=panel,
        )
        return

    try:
        _YARDIMCI.set_status_info(
            panel,
            _m(panel, "update_applying", "Güncelleme uygulanıyor..."),
            0,
        )

        try:
            if panel.inline_notice is not None:
                panel.inline_notice.hide_immediately()
        except Exception:
            pass

        sonuc = panel.on_update(panel.current_item, yeni)

        if sonuc is False:
            _YARDIMCI.set_status_warning(
                panel,
                _m(panel, "update_could_not_be_done", "Güncelleme yapılamadı"),
                0,
            )
            _YARDIMCI.show_inline_notice(
                panel,
                title=_m(panel, "update_error", "Güncelleme hatası"),
                text=_m(panel, "update_error_occurred", "Güncelleme hatası oluştu."),
                icon_name="warning.png",
                tone="warning",
                duration=4.2,
                on_tap=lambda: _safe_scroll_to_top(panel.new_code_area),
            )
            _YARDIMCI.toast(
                text=_m(panel, "update_error_occurred", "Güncelleme hatası oluştu."),
                icon_name="warning.png",
                duration=2.2,
                panel=panel,
            )
            return

        kayit_metni = _resolve_template_text(
            panel,
            "selected_item_saved_double_tap_to_close",
            "{item} kaydedildi. Çift dokunarak kapatabilirsiniz.",
            item=_current_item_display_text(panel),
        )

        _YARDIMCI.set_status_success(
            panel,
            _m(panel, "update_completed", "Güncelleme tamamlandı."),
            0,
        )
        _YARDIMCI.show_inline_notice(
            panel,
            title=_m(panel, "update_completed", "Güncelleme tamamlandı"),
            text=kayit_metni,
            icon_name="onaylandi.png",
            tone="success",
            duration=5.2,
            on_tap=lambda: _safe_scroll_to_top(panel.current_code_area),
        )
        _YARDIMCI.toast(
            text=_m(panel, "function_updated", "Fonksiyon güncellendi."),
            icon_name="upload.png",
            duration=2.4,
            panel=panel,
        )
    except Exception as exc:
        hata = str(exc or _m(panel, "update_error_occurred", "Güncelleme hatası oluştu."))
        _YARDIMCI.set_status_error(panel, hata, _DOGRULAMA.extract_line_number(exc))
        _YARDIMCI.show_inline_notice(
            panel,
            title=_m(panel, "update_error", "Güncelleme hatası"),
            text=hata,
            icon_name="error.png",
            tone="error",
            duration=4.8,
            on_tap=lambda: _safe_scroll_to_top(panel.new_code_area),
        )
        _YARDIMCI.toast(
            text=_m(panel, "update_error_occurred", "Güncelleme hatası oluştu."),
            icon_name="error.png",
            duration=2.4,
            panel=panel,
        )


def handle_restore(panel, *_args):
    """
    Geri yükleme akışını yürütür.
    """
    if not panel.on_restore:
        _YARDIMCI.set_status_warning(
            panel,
            _m(
                panel,
                "restore_callback_not_connected",
                "Geri yükleme callback bağlı değil.",
            ),
            0,
        )
        _YARDIMCI.show_inline_notice(
            panel,
            title=_m(panel, "restore_not_connected", "Geri yükleme bağlı değil"),
            text=_m(panel, "restore_callback_missing", "Geri yükleme callback bulunamadı."),
            icon_name="warning.png",
            tone="warning",
            duration=3.6,
        )
        _YARDIMCI.toast(
            text=_m(panel, "restore_service_not_connected", "Geri yükleme servisi bağlı değil."),
            icon_name="warning.png",
            duration=2.0,
            panel=panel,
        )
        return

    try:
        _YARDIMCI.set_status_info(
            panel,
            _m(panel, "restore_applying", "Geri yükleme uygulanıyor..."),
            0,
        )

        try:
            if panel.inline_notice is not None:
                panel.inline_notice.hide_immediately()
        except Exception:
            pass

        sonuc = panel.on_restore()

        if sonuc is False:
            _YARDIMCI.set_status_warning(
                panel,
                _m(panel, "restore_error", "Geri yükleme hatası"),
                0,
            )
            _YARDIMCI.show_inline_notice(
                panel,
                title=_m(panel, "restore_error", "Geri yükleme hatası"),
                text=_m(panel, "restore_error_occurred", "Geri yükleme hatası oluştu."),
                icon_name="warning.png",
                tone="warning",
                duration=4.2,
                on_tap=lambda: _safe_scroll_to_top(panel.current_code_area),
            )
            _YARDIMCI.toast(
                text=_m(panel, "restore_error_occurred", "Geri yükleme hatası oluştu."),
                icon_name="warning.png",
                duration=2.2,
                panel=panel,
            )
            return

        _YARDIMCI.set_status_success(
            panel,
            _m(panel, "restore_completed", "Geri yükleme tamamlandı."),
            0,
        )
        _YARDIMCI.show_inline_notice(
            panel,
            title=_m(panel, "restore_completed", "Geri yükleme tamamlandı"),
            text=_m(
                panel,
                "last_valid_backup_restored",
                "Son uygun yedek belgeye geri uygulandı.",
            ),
            icon_name="geri_yukle.png",
            tone="success",
            duration=5.0,
            on_tap=lambda: _safe_scroll_to_top(panel.current_code_area),
        )
        _YARDIMCI.toast(
            text=_m(
                panel,
                "restore_completed_from_last_backup",
                "Son yedekten geri yükleme tamamlandı.",
            ),
            icon_name="geri_yukle.png",
            duration=2.4,
            panel=panel,
        )
    except Exception as exc:
        hata = str(exc or _m(panel, "restore_error_occurred", "Geri yükleme hatası oluştu."))
        _YARDIMCI.set_status_error(panel, hata, _DOGRULAMA.extract_line_number(exc))
        _YARDIMCI.show_inline_notice(
            panel,
            title=_m(panel, "restore_error", "Geri yükleme hatası"),
            text=hata,
            icon_name="error.png",
            tone="error",
            duration=4.8,
            on_tap=lambda: _safe_scroll_to_top(panel.current_code_area),
        )
        _YARDIMCI.toast(
            text=_m(panel, "restore_error_occurred", "Geri yükleme hatası oluştu."),
            icon_name="error.png",
            duration=2.4,
            panel=panel,
                             )

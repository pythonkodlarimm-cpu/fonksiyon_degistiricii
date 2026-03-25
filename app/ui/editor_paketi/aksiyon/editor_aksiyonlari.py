# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/aksiyon/editor_aksiyonlari.py

ROL:
- Editör panelindeki kullanıcı aksiyonlarını yürütmek
- Kopyalama, temizleme, doğrulama, güncelleme ve geri yükleme akışlarını yönetmek
- Bildirim ve durum güncellemelerini ilgili yöneticiler üzerinden tetiklemek
- Aktif dile göre kullanıcıya görünen metinleri üretmek

MİMARİ:
- Doğrudan üst katman tarafından değil, aksiyon/yoneticisi.py üzerinden kullanılmalıdır
- Doğrulama ve yardımcı akışlar alt paket yöneticileri üzerinden çağrılır
- Panel davranışı korunur
- UI ile iş akışı ayrımı güçlendirilmiştir
- Görünen metinler panel/services üzerinden çözülebilir
- Low-level doğrulama mesajı UI katmanında kullanıcı diliyle sunulabilir
- Başarı metinlerinde placeholder çözümü güvenli biçimde yapılır
- Callback sonucu False dönerse başarı bildirimi verilmez

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 4
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

from app.ui.editor_paketi.dogrulama import DogrulamaYoneticisi
from app.ui.editor_paketi.yardimci import YardimciYoneticisi


_DOGRULAMA = DogrulamaYoneticisi()
_YARDIMCI = YardimciYoneticisi()


def _m(panel, anahtar: str, default: str = "") -> str:
    try:
        if panel is not None and hasattr(panel, "_m"):
            return str(panel._m(anahtar, default) or default or anahtar)
    except Exception:
        pass
    return str(default or anahtar)


def _safe_scroll_to_top(widget) -> None:
    try:
        if widget is not None and hasattr(widget, "scroll_to_top"):
            widget.scroll_to_top()
    except Exception:
        pass


def _current_item_display_text(panel) -> str:
    try:
        return str(_YARDIMCI.current_item_display(panel) or "").strip() or "-"
    except Exception:
        return "-"


def _resolve_template_text(panel, anahtar: str, default: str = "", **values) -> str:
    metin = _m(panel, anahtar, default)

    try:
        for key, value in values.items():
            metin = metin.replace("{" + str(key) + "}", str(value))
    except Exception:
        pass

    return str(metin or default or "")


def copy_current_to_new(panel, *_args):
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
        _m(panel, "code_copied_to_edit_area", "Kod düzenleme alanına kopyalandı."),
        "file_copy.png",
        2.4,
    )


def clear_new_code(panel, *_args):
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
        _m(panel, "new_code_area_cleared", "Yeni kod alanı temizlendi."),
        "clear.png",
        2.0,
    )


def check_new_code(panel, *_args):
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
            _m(panel, "code_validation_successful", "Kod doğrulaması başarılı."),
            "code_check.png",
            2.2,
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
        _m(panel, "code_validation_failed", "Kod doğrulaması başarısız."),
        "warning.png",
        2.2,
    )


def handle_update(panel, *_args):
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
            _m(panel, "select_function_first", "Önce fonksiyon seçmelisiniz."),
            "warning.png",
            2.0,
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
            _m(
                panel,
                "pre_update_validation_failed",
                "Güncelleme öncesi doğrulama başarısız.",
            ),
            "warning.png",
            2.2,
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
                text=_m(
                    panel,
                    "update_error_occurred",
                    "Güncelleme hatası oluştu.",
                ),
                icon_name="warning.png",
                tone="warning",
                duration=4.2,
                on_tap=lambda: _safe_scroll_to_top(panel.new_code_area),
            )
            _YARDIMCI.toast(
                _m(panel, "update_error_occurred", "Güncelleme hatası oluştu."),
                "warning.png",
                2.2,
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
            _m(panel, "function_updated", "Fonksiyon güncellendi."),
            "upload.png",
            2.4,
        )
    except Exception as exc:
        hata = str(
            exc
            or _m(panel, "update_error_occurred", "Güncelleme hatası oluştu.")
        )
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
            _m(panel, "update_error_occurred", "Güncelleme hatası oluştu."),
            "error.png",
            2.4,
        )


def handle_restore(panel, *_args):
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
            text=_m(
                panel,
                "restore_callback_missing",
                "Geri yükleme callback bulunamadı.",
            ),
            icon_name="warning.png",
            tone="warning",
            duration=3.6,
        )
        _YARDIMCI.toast(
            _m(
                panel,
                "restore_service_not_connected",
                "Geri yükleme servisi bağlı değil.",
            ),
            "warning.png",
            2.0,
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
                text=_m(
                    panel,
                    "restore_error_occurred",
                    "Geri yükleme hatası oluştu.",
                ),
                icon_name="warning.png",
                tone="warning",
                duration=4.2,
                on_tap=lambda: _safe_scroll_to_top(panel.current_code_area),
            )
            _YARDIMCI.toast(
                _m(panel, "restore_error_occurred", "Geri yükleme hatası oluştu."),
                "warning.png",
                2.2,
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
            _m(
                panel,
                "restore_completed_from_last_backup",
                "Son yedekten geri yükleme tamamlandı.",
            ),
            "geri_yukle.png",
            2.4,
        )
    except Exception as exc:
        hata = str(
            exc
            or _m(panel, "restore_error_occurred", "Geri yükleme hatası oluştu.")
        )
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
            _m(panel, "restore_error_occurred", "Geri yükleme hatası oluştu."),
            "error.png",
            2.4,
                       )

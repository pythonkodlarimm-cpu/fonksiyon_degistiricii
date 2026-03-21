# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/aksiyon/editor_aksiyonlari.py

ROL:
- Editör panelindeki kullanıcı aksiyonlarını yürütmek
- Kopyalama, temizleme, doğrulama, güncelleme ve geri yükleme akışlarını yönetmek
- Bildirim ve durum güncellemelerini ilgili yöneticiler üzerinden tetiklemek

MİMARİ:
- Doğrudan üst katman tarafından değil, aksiyon/yoneticisi.py üzerinden kullanılmalıdır
- Doğrulama ve yardımcı akışlar alt paket yöneticileri üzerinden çağrılır
- Panel davranışı korunur
- UI ile iş akışı ayrımı güçlendirilmiştir

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 2
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from app.ui.editor_paketi.dogrulama import DogrulamaYoneticisi
from app.ui.editor_paketi.yardimci import YardimciYoneticisi


_DOGRULAMA = DogrulamaYoneticisi()
_YARDIMCI = YardimciYoneticisi()


def copy_current_to_new(panel, *_args):
    panel._set_new_code(panel.current_code_area.text)

    _YARDIMCI.set_status_info(panel, "Mevcut kod yeni alana kopyalandı.", 0)
    _YARDIMCI.show_inline_notice(
        panel,
        title="Kod kopyalandı",
        text="Mevcut fonksiyon yeni düzenleme alanına aktarıldı.",
        icon_name="file_copy.png",
        tone="info",
        duration=3.2,
        on_tap=lambda: panel.new_code_area.scroll_to_top(),
    )
    _YARDIMCI.toast("Kod düzenleme alanına kopyalandı.", "file_copy.png", 2.4)


def clear_new_code(panel, *_args):
    panel._set_new_code("")

    _YARDIMCI.set_status_info(panel, "Yeni kod alanı temizlendi.", 0)
    _YARDIMCI.show_inline_notice(
        panel,
        title="Alan temizlendi",
        text="Yeni fonksiyon kodu alanı boşaltıldı.",
        icon_name="clear.png",
        tone="info",
        duration=3.0,
        on_tap=lambda: panel.new_code_area.scroll_to_top(),
    )
    _YARDIMCI.toast("Yeni kod alanı temizlendi.", "clear.png", 2.0)


def check_new_code(panel, *_args):
    ok, hata, satir = _DOGRULAMA.validate_new_code(panel.new_code_area.text)

    if ok:
        _YARDIMCI.set_status_success(panel, "Doğrulama doğru.", 0)
        _YARDIMCI.show_inline_notice(
            panel,
            title="Doğrulama başarılı",
            text="Yeni fonksiyon yapısı geçerli görünüyor.",
            icon_name="code_check.png",
            tone="success",
            duration=3.6,
            on_tap=lambda: panel.new_code_area.scroll_to_top(),
        )
        _YARDIMCI.toast("Kod doğrulaması başarılı.", "code_check.png", 2.2)
        return

    _YARDIMCI.set_status_error(panel, hata, satir)
    _YARDIMCI.show_inline_notice(
        panel,
        title="Doğrulama hatası",
        text=hata,
        icon_name="warning.png",
        tone="error",
        duration=4.2,
        on_tap=lambda: panel.new_code_area.scroll_to_top(),
    )
    _YARDIMCI.toast("Kod doğrulaması başarısız.", "warning.png", 2.2)


def handle_update(panel, *_args):
    if not panel.on_update or panel.current_item is None:
        _YARDIMCI.set_status_warning(panel, "Güncellenecek öğe seçilmedi.", 0)
        _YARDIMCI.show_inline_notice(
            panel,
            title="Güncelleme yapılamadı",
            text="Önce güncellenecek fonksiyonu seçmelisiniz.",
            icon_name="warning.png",
            tone="warning",
            duration=3.8,
        )
        _YARDIMCI.toast("Önce fonksiyon seçmelisiniz.", "warning.png", 2.0)
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
            title="Güncelleme öncesi hata",
            text=hata,
            icon_name="warning.png",
            tone="error",
            duration=4.2,
            on_tap=lambda: panel.new_code_area.scroll_to_top(),
        )
        _YARDIMCI.toast("Güncelleme öncesi doğrulama başarısız.", "warning.png", 2.2)
        return

    try:
        _YARDIMCI.set_status_info(panel, "Güncelleme uygulanıyor...", 0)
        panel.inline_notice.hide_immediately()
        panel.on_update(panel.current_item, yeni)
        _YARDIMCI.set_status_success(panel, "Güncelleme tamamlandı.", 0)
        _YARDIMCI.show_inline_notice(
            panel,
            title="Güncelleme tamamlandı",
            text=f"{_YARDIMCI.current_item_display(panel)} kaydedildi. Çift dokunarak kapatabilirsiniz.",
            icon_name="onaylandi.png",
            tone="success",
            duration=5.2,
            on_tap=lambda: panel.current_code_area.scroll_to_top(),
        )
        _YARDIMCI.toast("Fonksiyon güncellendi.", "upload.png", 2.4)
    except Exception as exc:
        hata = str(exc or "Güncelleme hatası oluştu.")
        _YARDIMCI.set_status_error(panel, hata, _DOGRULAMA.extract_line_number(exc))
        _YARDIMCI.show_inline_notice(
            panel,
            title="Güncelleme hatası",
            text=hata,
            icon_name="error.png",
            tone="error",
            duration=4.8,
            on_tap=lambda: panel.new_code_area.scroll_to_top(),
        )
        _YARDIMCI.toast("Güncelleme hatası oluştu.", "error.png", 2.4)


def handle_restore(panel, *_args):
    if not panel.on_restore:
        _YARDIMCI.set_status_warning(panel, "Geri yükleme callback bağlı değil.", 0)
        _YARDIMCI.show_inline_notice(
            panel,
            title="Geri yükleme bağlı değil",
            text="Geri yükleme callback bulunamadı.",
            icon_name="warning.png",
            tone="warning",
            duration=3.6,
        )
        _YARDIMCI.toast("Geri yükleme servisi bağlı değil.", "warning.png", 2.0)
        return

    try:
        _YARDIMCI.set_status_info(panel, "Geri yükleme uygulanıyor...", 0)
        panel.inline_notice.hide_immediately()
        panel.on_restore()
        _YARDIMCI.set_status_success(panel, "Geri yükleme tamamlandı.", 0)
        _YARDIMCI.show_inline_notice(
            panel,
            title="Geri yükleme tamamlandı",
            text="Son uygun yedek belgeye geri uygulandı.",
            icon_name="geri_yukle.png",
            tone="success",
            duration=5.0,
            on_tap=lambda: panel.current_code_area.scroll_to_top(),
        )
        _YARDIMCI.toast("Son yedekten geri yükleme tamamlandı.", "geri_yukle.png", 2.4)
    except Exception as exc:
        hata = str(exc or "Geri yükleme hatası oluştu.")
        _YARDIMCI.set_status_error(panel, hata, _DOGRULAMA.extract_line_number(exc))
        _YARDIMCI.show_inline_notice(
            panel,
            title="Geri yükleme hatası",
            text=hata,
            icon_name="error.png",
            tone="error",
            duration=4.8,
        )
        _YARDIMCI.toast("Geri yükleme hatası oluştu.", "error.png", 2.4)
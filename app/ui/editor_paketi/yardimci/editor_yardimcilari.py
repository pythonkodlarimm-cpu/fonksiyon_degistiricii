# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/yardimci/editor_yardimcilari.py

ROL:
- Editör paneli için yardımcı UI akışlarını toplamak
- Toast, inline notice, popup kapatma ve durum metni işlemlerini yönetmek
- Panel üzerinde seçili öğe ve hata satırı gibi ortak yardımcı davranışları sağlamak

MİMARİ:
- Üst katman bu modüle doğrudan değil, yardimci/yoneticisi.py üzerinden erişmelidir
- Sistem bildirim servisine yönetici üzerinden erişilir
- Editör panelindeki ortak yardımcı davranışlar burada merkezileştirilir

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 2
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations


def _sistem():
    from app.services.sistem import SistemYoneticisi
    return SistemYoneticisi()


def toast(text: str, icon_name: str = "", duration: float = 2.2) -> None:
    try:
        _sistem().bildirim_goster(
            text=str(text or ""),
            icon_name=str(icon_name or ""),
            duration=float(duration or 2.2),
        )
    except Exception:
        pass


def close_popups(panel) -> None:
    for attr in ("_current_popup", "_editor_popup"):
        popup = getattr(panel, attr, None)
        if popup is not None:
            try:
                popup.dismiss()
            except Exception:
                pass
        setattr(panel, attr, None)


def current_item_display(panel) -> str:
    try:
        if panel.current_item is None:
            return "Fonksiyon"

        path = str(getattr(panel.current_item, "path", "") or "").strip()
        if path:
            return path

        return str(getattr(panel.current_item, "name", "") or "Fonksiyon")
    except Exception:
        return "Fonksiyon"


def show_inline_notice(
    panel,
    title: str,
    text: str,
    icon_name: str = "onaylandi.png",
    tone: str = "success",
    duration: float = 4.0,
    on_tap=None,
) -> None:
    try:
        panel.inline_notice.show(
            title=str(title or ""),
            text=str(text or ""),
            icon_name=str(icon_name or "onaylandi.png"),
            tone=str(tone or "success"),
            duration=float(duration or 4.0),
            on_tap=on_tap,
        )
    except Exception:
        pass


def set_status_info(panel, message="", line_no=0):
    temiz = str(message or "").strip() or "Hazır."
    panel.error_box.set_info(temiz)

    try:
        panel.new_code_area.set_error_line(line_no)
    except Exception:
        pass


def set_status_warning(panel, message="", line_no=0):
    temiz = str(message or "").strip() or "Uyarı."
    panel.error_box.set_warning(temiz)

    try:
        panel.new_code_area.set_error_line(line_no)
    except Exception:
        pass


def set_status_error(panel, message="", line_no=0):
    temiz = str(message or "").strip() or "Hata oluştu."
    panel.error_box.set_error(temiz)

    try:
        panel.new_code_area.set_error_line(line_no)
    except Exception:
        pass


def set_status_success(panel, message="", line_no=0):
    temiz = str(message or "").strip() or "Doğrulama doğru."
    panel.error_box.set_success(temiz, pulse_seconds=6.0)

    try:
        panel.new_code_area.set_error_line(line_no)
    except Exception:
        pass


def set_popup_error(label, editor_area, message="", line_no=0):
    temiz = str(message or "").strip()
    label.text = temiz if temiz else "Hazır."
    label.color = (1, 0.78, 0.78, 1) if temiz else (0.88, 0.94, 1, 1)

    try:
        editor_area.set_error_line(line_no)
    except Exception:
        pass
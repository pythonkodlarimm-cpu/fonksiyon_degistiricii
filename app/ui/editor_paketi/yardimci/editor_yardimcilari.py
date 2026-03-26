# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/yardimci/editor_yardimcilari.py

ROL:
- Editör paneli için yardımcı UI akışlarını toplamak
- Toast, inline notice, popup kapatma ve durum metni işlemlerini yönetmek
- Panel üzerinde seçili öğe ve hata satırı gibi ortak yardımcı davranışları sağlamak
- Aktif dile göre kullanıcıya görünen metinleri üretmek
- Yeni dil anahtarı (key) destekli inline notice akışını yönetmek
- Panel / popup tarafındaki ortak durum metni güvenliğini artırmak

MİMARİ:
- Üst katman bu modüle doğrudan değil, yardimci/yoneticisi.py üzerinden erişmelidir
- Sistem bildirim servisine yönetici üzerinden erişilir
- Editör panelindeki ortak yardımcı davranışlar burada merkezileştirilir
- Görünen metinler panel/services üzerinden çözülebilir
- Fail-soft yaklaşım korunur
- Widget erişimlerinde güvenli fallback uygulanır
- Dil anahtarı verilirse metin öncelikle key üzerinden çözülür
- Key verilmezse doğrudan metin kullanılır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 5
TARIH: 2026-03-26
IMZA: FY.
"""

from __future__ import annotations


# =========================================================
# INTERNAL
# =========================================================
def _sistem():
    from app.services.sistem import SistemYoneticisi
    return SistemYoneticisi()


def _m(panel, anahtar: str, default: str = "") -> str:
    try:
        if panel is not None and hasattr(panel, "_m"):
            return str(panel._m(anahtar, default) or default or anahtar)
    except Exception:
        pass
    return str(default or anahtar)


def _safe_getattr(obj, name: str, default=None):
    try:
        return getattr(obj, name, default)
    except Exception:
        return default


def _resolve_notice_text(
    panel,
    text: str,
    key: str = "",
    default: str = "",
) -> str:
    try:
        if str(key or "").strip():
            return str(_m(panel, key, default or text) or default or text or "").strip()
    except Exception:
        pass

    try:
        return str(text or default or "").strip()
    except Exception:
        return str(default or "")


def _set_error_line_safe(editor_area, line_no=0) -> None:
    try:
        if editor_area is not None and hasattr(editor_area, "set_error_line"):
            editor_area.set_error_line(line_no)
    except Exception:
        pass


def _set_popup_label_text_safe(panel, label, text: str = "") -> None:
    temiz = str(text or "").strip()

    try:
        label.text = temiz if temiz else _m(panel, "app_ready", "Hazır.")
    except Exception:
        pass

    try:
        label.color = (1, 0.78, 0.78, 1) if temiz else (0.88, 0.94, 1, 1)
    except Exception:
        pass


# =========================================================
# TOAST
# =========================================================
def toast(text: str, icon_name: str = "", duration: float = 2.2) -> None:
    try:
        _sistem().bildirim_goster(
            text=str(text or ""),
            icon_name=str(icon_name or ""),
            duration=float(duration or 2.2),
        )
    except Exception:
        pass


# =========================================================
# POPUP
# =========================================================
def close_popups(panel) -> None:
    for attr in ("_current_popup", "_editor_popup"):
        popup = _safe_getattr(panel, attr, None)

        if popup is not None:
            try:
                popup.dismiss()
            except Exception:
                pass

        try:
            setattr(panel, attr, None)
        except Exception:
            pass


# =========================================================
# CURRENT ITEM
# =========================================================
def current_item_display(panel) -> str:
    try:
        current_item = _safe_getattr(panel, "current_item", None)
        if current_item is None:
            return _m(panel, "function_generic", "Fonksiyon")

        path = str(_safe_getattr(current_item, "path", "") or "").strip()
        if path:
            return path

        name_value = str(_safe_getattr(current_item, "name", "") or "").strip()
        if name_value:
            return name_value

        signature_value = str(_safe_getattr(current_item, "signature", "") or "").strip()
        if signature_value:
            return signature_value

        return _m(panel, "function_generic", "Fonksiyon")
    except Exception:
        return _m(panel, "function_generic", "Fonksiyon")


# =========================================================
# INLINE NOTICE
# =========================================================
def show_inline_notice(
    panel,
    title: str,
    text: str,
    icon_name: str = "onaylandi.png",
    tone: str = "success",
    duration: float = 4.0,
    on_tap=None,
    title_key: str = "",
    title_default: str = "",
    text_key: str = "",
    text_default: str = "",
) -> None:
    try:
        if panel is None:
            return

        notice = _safe_getattr(panel, "inline_notice", None)
        if notice is None:
            return

        temiz_baslik = _resolve_notice_text(
            panel,
            text=title,
            key=title_key,
            default=title_default,
        )
        temiz_icerik = _resolve_notice_text(
            panel,
            text=text,
            key=text_key,
            default=text_default,
        )

        if not temiz_baslik:
            temiz_baslik = _m(panel, "notification", "Bildirim")

        notice.show(
            title=temiz_baslik,
            text=temiz_icerik,
            icon_name=str(icon_name or "onaylandi.png"),
            tone=str(tone or "success"),
            duration=float(duration or 4.0),
            on_tap=on_tap,
        )

    except Exception:
        pass


# =========================================================
# STATUS
# =========================================================
def set_status_info(panel, message="", line_no=0):
    temiz = str(message or "").strip() or _m(panel, "app_ready", "Hazır.")

    try:
        error_box = _safe_getattr(panel, "error_box", None)
        if error_box is not None and hasattr(error_box, "set_info"):
            error_box.set_info(temiz)
    except Exception:
        pass

    _set_error_line_safe(_safe_getattr(panel, "new_code_area", None), line_no)


def set_status_warning(panel, message="", line_no=0):
    temiz = str(message or "").strip() or _m(panel, "warning", "Uyarı.")

    try:
        error_box = _safe_getattr(panel, "error_box", None)
        if error_box is not None and hasattr(error_box, "set_warning"):
            error_box.set_warning(temiz)
    except Exception:
        pass

    _set_error_line_safe(_safe_getattr(panel, "new_code_area", None), line_no)


def set_status_error(panel, message="", line_no=0):
    temiz = str(message or "").strip() or _m(
        panel,
        "an_error_occurred",
        "Hata oluştu.",
    )

    try:
        error_box = _safe_getattr(panel, "error_box", None)
        if error_box is not None and hasattr(error_box, "set_error"):
            error_box.set_error(temiz)
    except Exception:
        pass

    _set_error_line_safe(_safe_getattr(panel, "new_code_area", None), line_no)


def set_status_success(panel, message="", line_no=0):
    temiz = str(message or "").strip() or _m(
        panel,
        "validation_correct",
        "Doğrulama doğru.",
    )

    try:
        error_box = _safe_getattr(panel, "error_box", None)
        if error_box is not None and hasattr(error_box, "set_success"):
            error_box.set_success(temiz, pulse_seconds=6.0)
    except Exception:
        pass

    _set_error_line_safe(_safe_getattr(panel, "new_code_area", None), line_no)


# =========================================================
# POPUP STATUS
# =========================================================
def set_popup_error(label, editor_area, message="", line_no=0, panel=None):
    temiz = str(message or "").strip()

    _set_popup_label_text_safe(panel, label, temiz)
    _set_error_line_safe(editor_area, line_no)

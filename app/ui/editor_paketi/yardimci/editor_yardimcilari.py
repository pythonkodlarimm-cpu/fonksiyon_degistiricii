# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/yardimci/editor_yardimcilari.py

ROL:
- Editör paneli için yardımcı UI akışlarını toplar
- Toast, inline notice, popup kapatma ve durum metni işlemlerini yönetir
- Panel üzerinde seçili öğe ve hata satırı gibi ortak davranışları sağlar
- Aktif dile göre kullanıcıya görünen metinleri üretir
- Inline notice metnini key veya doğrudan metin üzerinden çözer
- Panel / popup tarafındaki ortak durum metni güvenliğini artırır

MİMARİ:
- Yardımcı fonksiyonlar panel odaklı çalışır
- Çeviri için öncelikle panel._m(...) hattı kullanılır
- Bildirim için öncelikle panel.services kullanılır
- Fail-soft yaklaşım korunur
- Widget erişimlerinde güvenli fallback uygulanır

SURUM: 6
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations


def _safe_getattr(obj, name: str, default=None):
    """
    Güvenli getattr yardımcı fonksiyonu.
    """
    try:
        return getattr(obj, name, default)
    except Exception:
        return default


def _m(panel, anahtar: str, default: str = "") -> str:
    """
    Panel üzerindeki çeviri hattını kullanır.
    """
    try:
        metod = _safe_getattr(panel, "_m", None)
        if callable(metod):
            return str(metod(anahtar, default) or default or anahtar)
    except Exception:
        pass

    return str(default or anahtar)


def _sistem_bildirimi_goster(panel, text: str, icon_name: str = "", duration: float = 2.2) -> None:
    """
    Önce panel.services üzerinden, gerekirse fallback ile bildirim göstermeyi dener.
    """
    try:
        services = _safe_getattr(panel, "services", None)
        if services is not None:
            sistem_yoneticisi = _safe_getattr(services, "sistem_yoneticisi", None)
            if callable(sistem_yoneticisi):
                sistem = sistem_yoneticisi()
                bildirim_goster = _safe_getattr(sistem, "bildirim_goster", None)
                if callable(bildirim_goster):
                    bildirim_goster(
                        text=str(text or ""),
                        icon_name=str(icon_name or ""),
                        duration=float(duration or 2.2),
                    )
                    return
    except Exception:
        pass

    try:
        from app.services.sistem import SistemYoneticisi

        SistemYoneticisi().bildirim_goster(
            text=str(text or ""),
            icon_name=str(icon_name or ""),
            duration=float(duration or 2.2),
        )
    except Exception:
        pass


def _resolve_notice_text(panel, text: str, key: str = "", default: str = "") -> str:
    """
    Notice metnini önce key üzerinden, yoksa düz metin üzerinden çözer.
    """
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
    """
    Editör alanında hata satırını güvenli biçimde işaretler.
    """
    try:
        metod = _safe_getattr(editor_area, "set_error_line", None)
        if callable(metod):
            metod(line_no)
    except Exception:
        pass


def _set_popup_label_text_safe(panel, label, text: str = "") -> None:
    """
    Popup içi durum label metnini ve rengini güvenli biçimde ayarlar.
    """
    temiz = str(text or "").strip()

    try:
        label.text = temiz if temiz else _m(panel, "app_ready", "Hazır.")
    except Exception:
        pass

    try:
        label.color = (1, 0.78, 0.78, 1) if temiz else (0.88, 0.94, 1, 1)
    except Exception:
        pass


def toast(panel, text: str, icon_name: str = "", duration: float = 2.2) -> None:
    """
    Sistem bildirimi göstermeyi dener.
    """
    _sistem_bildirimi_goster(
        panel=panel,
        text=text,
        icon_name=icon_name,
        duration=duration,
    )


def close_popups(panel) -> None:
    """
    Panel üzerindeki açık popup referanslarını kapatır.
    """
    for attr_name in ("_current_popup", "_editor_popup"):
        popup = _safe_getattr(panel, attr_name, None)

        if popup is not None:
            try:
                popup.dismiss()
            except Exception:
                pass

        try:
            setattr(panel, attr_name, None)
        except Exception:
            pass


def current_item_display(panel) -> str:
    """
    Panelde seçili item için kullanıcıya gösterilecek metni döndürür.
    """
    current_item = _safe_getattr(panel, "current_item", None)
    if current_item is None:
        return _m(panel, "function_generic", "Fonksiyon")

    for attr_name in ("path", "name", "signature"):
        try:
            value = str(_safe_getattr(current_item, attr_name, "") or "").strip()
            if value:
                return value
        except Exception:
            continue

    return _m(panel, "function_generic", "Fonksiyon")


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
    """
    Panel üzerindeki inline notice bileşenine bildirim gösterir.
    """
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


def set_status_info(panel, message="", line_no=0):
    """
    Editör panelinde bilgi durumu gösterir.
    """
    temiz = str(message or "").strip() or _m(panel, "app_ready", "Hazır.")

    try:
        error_box = _safe_getattr(panel, "error_box", None)
        metod = _safe_getattr(error_box, "set_info", None)
        if callable(metod):
            metod(temiz)
    except Exception:
        pass

    _set_error_line_safe(_safe_getattr(panel, "new_code_area", None), line_no)


def set_status_warning(panel, message="", line_no=0):
    """
    Editör panelinde uyarı durumu gösterir.
    """
    temiz = str(message or "").strip() or _m(panel, "warning", "Uyarı.")

    try:
        error_box = _safe_getattr(panel, "error_box", None)
        metod = _safe_getattr(error_box, "set_warning", None)
        if callable(metod):
            metod(temiz)
    except Exception:
        pass

    _set_error_line_safe(_safe_getattr(panel, "new_code_area", None), line_no)


def set_status_error(panel, message="", line_no=0):
    """
    Editör panelinde hata durumu gösterir.
    """
    temiz = str(message or "").strip() or _m(
        panel,
        "an_error_occurred",
        "Hata oluştu.",
    )

    try:
        error_box = _safe_getattr(panel, "error_box", None)
        metod = _safe_getattr(error_box, "set_error", None)
        if callable(metod):
            metod(temiz)
    except Exception:
        pass

    _set_error_line_safe(_safe_getattr(panel, "new_code_area", None), line_no)


def set_status_success(panel, message="", line_no=0):
    """
    Editör panelinde başarı durumu gösterir.
    """
    temiz = str(message or "").strip() or _m(
        panel,
        "validation_correct",
        "Doğrulama doğru.",
    )

    try:
        error_box = _safe_getattr(panel, "error_box", None)
        metod = _safe_getattr(error_box, "set_success", None)
        if callable(metod):
            metod(temiz, pulse_seconds=6.0)
    except Exception:
        pass

    _set_error_line_safe(_safe_getattr(panel, "new_code_area", None), line_no)


def set_popup_error(label, editor_area, message="", line_no=0, panel=None):
    """
    Popup içi hata metnini ve hata satırını uygular.
    """
    temiz = str(message or "").strip()
    _set_popup_label_text_safe(panel, label, temiz)
    _set_error_line_safe(editor_area, line_no)

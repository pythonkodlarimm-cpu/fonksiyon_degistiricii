# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/fonksiyon_listesi_paketi/gorunum_akisi/gorunum_akisi.py

ROL:
- Fonksiyon listesi görünüm açma / kapama akışını yönetmek
- Toggle ikonunu senkronize etmek
- Liste yüksekliğini görünüm moduna göre ayarlamak
- Görünüm durumuna göre kullanıcı bilgilendirme metnini güncellemek
- Aktif dil değiştiğinde görünüm metinlerinin yeniden uygulanmasına yardımcı olmak

MİMARİ:
- Görünüm davranışı burada tutulur
- Üst katman bu modüle doğrudan değil, gorunum_akisi/yoneticisi.py üzerinden erişmelidir
- UI metinleri owner -> services -> metin servisi zinciriyle çözülebilir
- Platform bağımsız çalışır
- Fail-soft yaklaşımıyla güvenli fallback kullanır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 3
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

from kivy.clock import Clock


def _m(owner, anahtar: str, default: str = "") -> str:
    try:
        if owner is not None and hasattr(owner, "_m"):
            return str(owner._m(anahtar, default) or default or anahtar)
    except Exception:
        pass
    return str(default or anahtar)


def set_toggle_icon(owner, icon_name: str) -> None:
    if owner is None or getattr(owner, "toggle_button", None) is None:
        return

    icon_widget = getattr(owner.toggle_button, "icon", None)
    if icon_widget is None:
        return

    try:
        from app.ui.icon_yardimci import icon_path

        yol = icon_path(icon_name)
        if not yol:
            return

        icon_widget.source = yol
        try:
            icon_widget.reload()
        except Exception:
            pass
    except Exception:
        pass


def update_toggle_icon(owner) -> None:
    try:
        if bool(getattr(owner, "is_list_expanded", True)):
            owner._gorunum_akisi_yoneticisi.set_toggle_icon(
                owner,
                "visibility_on.png",
            )
        else:
            owner._gorunum_akisi_yoneticisi.set_toggle_icon(
                owner,
                "visibility_off.png",
            )
    except Exception:
        pass


def _apply_toggle_button_text(owner) -> None:
    try:
        if owner is None or getattr(owner, "toggle_button", None) is None:
            return

        text_value = _m(owner, "list", "Liste")

        if hasattr(owner.toggle_button, "set_text") and callable(
            owner.toggle_button.set_text
        ):
            owner.toggle_button.set_text(text_value)
        elif hasattr(owner.toggle_button, "text"):
            owner.toggle_button.text = text_value
    except Exception:
        pass


def _apply_info_text(owner) -> None:
    try:
        if owner is None or getattr(owner, "list_info_label", None) is None:
            return

        if bool(getattr(owner, "is_list_expanded", True)):
            owner.list_info_label.text = _m(
                owner,
                "function_list_expanded_info",
                "Tüm fonksiyonlar geniş listede görüntülenebilir ve aranabilir.",
            )
        else:
            owner.list_info_label.text = _m(
                owner,
                "function_list_compact_info",
                "Dar görünüm açık. Yine kaydırarak birkaç fonksiyon görebilirsiniz.",
            )
    except Exception:
        pass


def _apply_list_height(owner) -> None:
    try:
        if owner is None or getattr(owner, "list_wrap", None) is None:
            return

        if bool(getattr(owner, "is_list_expanded", True)):
            owner.list_wrap.height = getattr(owner, "_expanded_list_height", owner.list_wrap.height)
        else:
            owner.list_wrap.height = getattr(owner, "_compact_list_height", owner.list_wrap.height)
    except Exception:
        pass


def _apply_scroll_and_header_state(owner) -> None:
    try:
        if getattr(owner, "scroll", None) is not None:
            owner.scroll.disabled = False
            owner.scroll.opacity = 1
            owner.scroll.size_hint_y = 1
    except Exception:
        pass

    try:
        if getattr(owner, "table_header", None) is not None:
            owner.table_header.opacity = 1
    except Exception:
        pass


def toggle_list_visibility(owner, *_args) -> None:
    try:
        owner.is_list_expanded = not bool(getattr(owner, "is_list_expanded", True))
    except Exception:
        owner.is_list_expanded = True

    try:
        owner._gorunum_akisi_yoneticisi.sync_list_visibility(owner)
    except Exception:
        pass

    try:
        Clock.schedule_once(owner._scroll_top, 0)
    except Exception:
        pass

    try:
        Clock.schedule_once(owner._refresh_trigger, 0)
    except Exception:
        pass


def sync_list_visibility(owner) -> None:
    if owner is None:
        return

    if (
        getattr(owner, "list_wrap", None) is None
        or getattr(owner, "list_info_label", None) is None
        or getattr(owner, "scroll", None) is None
        or getattr(owner, "table_header", None) is None
    ):
        return

    _apply_list_height(owner)
    _apply_info_text(owner)
    _apply_scroll_and_header_state(owner)

    try:
        _apply_toggle_button_text(owner)
    except Exception:
        pass

    try:
        owner._gorunum_akisi_yoneticisi.update_toggle_icon(owner)
    except Exception:
        pass

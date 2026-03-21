# -*- coding: utf-8 -*-
"""
DOSYA: app/services/belge/ice_aktarma_servisi.py

SURUM: 5
API 35 hardened
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from kivy.utils import platform

from app.services.android.uri_servisi import (
    AndroidUriServisiHatasi,
    get_app_cache_dir,
    get_display_name as get_uri_display_name,
    read_text as read_text_from_uri,
    is_android_document_uri,  # 🔥 YENİ: kritik kontrol
)
from app.services.dosya.servisi import (
    DosyaServisiHatasi,
    get_app_working_root,
    get_display_name as get_path_display_name,
    read_text as read_text_from_path,
    write_text,
)
from app.ui.dosya_secici_paketi.models import DocumentSelection, DocumentSession


class BelgeIceAktarmaServisiHatasi(ValueError):
    pass


# =========================================================
# NAME
# =========================================================
def _normalize_name(name: str) -> str:
    temiz = str(name or "").strip() or "belge.txt"
    for ch in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        temiz = temiz.replace(ch, "_")
    return temiz


def _working_copy_name(display_name: str) -> str:
    zaman = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{zaman}_{_normalize_name(display_name)}"


# =========================================================
# ROOT
# =========================================================
def _working_root() -> Path:
    try:
        root = get_app_working_root() / "working_imports"
        root.mkdir(parents=True, exist_ok=True)
        return root
    except Exception:
        pass

    if platform == "android":
        try:
            root = get_app_cache_dir() / "working_imports"
            root.mkdir(parents=True, exist_ok=True)
            return root
        except Exception:
            pass

    raise BelgeIceAktarmaServisiHatasi("Çalışma dizini oluşturulamadı.")


# =========================================================
# DISPLAY NAME
# =========================================================
def _resolve_display_name(selection: DocumentSelection) -> str:
    try:
        name = str(selection.preferred_display_name() or "").strip()
        if name:
            return name
    except Exception:
        pass

    # 🔥 URI doğrulama EKLENDİ (kritik fix)
    try:
        if selection.has_uri():
            uri = str(getattr(selection, "uri", "") or "").strip()

            if is_android_document_uri(uri):
                name = get_uri_display_name(uri)
                if name:
                    return name
    except Exception:
        pass

    try:
        if selection.has_local_path():
            path = str(getattr(selection, "local_path", "") or "").strip()
            if path:
                name = get_path_display_name(path)
                if name:
                    return name
    except Exception:
        pass

    return "belge.txt"


# =========================================================
# CORE WRITE
# =========================================================
def _write_working_copy(target: Path, content: str) -> None:
    try:
        write_text(target, content)
    except DosyaServisiHatasi as exc:
        raise BelgeIceAktarmaServisiHatasi(str(exc)) from exc


# =========================================================
# ANDROID IMPORT (KRİTİK FIX)
# =========================================================
def _import_from_android_document(selection: DocumentSelection) -> DocumentSession:
    uri = str(getattr(selection, "uri", "") or "").strip()

    # 🔥 EN KRİTİK FIX
    if not uri or not is_android_document_uri(uri):
        raise BelgeIceAktarmaServisiHatasi("Geçersiz Android URI.")

    display_name = _resolve_display_name(selection)
    target = _working_root() / _working_copy_name(display_name)

    try:
        content = read_text_from_uri(uri)
    except AndroidUriServisiHatasi as exc:
        raise BelgeIceAktarmaServisiHatasi(
            f"URI okunamadı (izin yok olabilir): {exc}"
        ) from exc

    if not content:
        raise BelgeIceAktarmaServisiHatasi("Boş içerik alındı.")

    _write_working_copy(target, content)

    return DocumentSession.from_selection(
        selection,
        working_local_path=str(target),
    )


# =========================================================
# FILE IMPORT
# =========================================================
def _import_from_filesystem(selection: DocumentSelection) -> DocumentSession:
    path = str(getattr(selection, "local_path", "") or "").strip()

    # 🔥 kritik fix
    if not path or path.startswith("content://"):
        raise BelgeIceAktarmaServisiHatasi("Geçersiz dosya yolu.")

    display_name = _resolve_display_name(selection)
    target = _working_root() / _working_copy_name(display_name)

    try:
        content = read_text_from_path(path)
    except DosyaServisiHatasi as exc:
        raise BelgeIceAktarmaServisiHatasi(str(exc)) from exc

    _write_working_copy(target, content)

    return DocumentSession.from_selection(
        selection,
        working_local_path=str(target),
    )


# =========================================================
# PUBLIC API
# =========================================================
def belgeyi_ice_aktar(selection: DocumentSelection) -> DocumentSession:
    if selection is None:
        raise BelgeIceAktarmaServisiHatasi("Belge seçimi boş.")

    try:
        # 🔥 BURASI EN KRİTİK NOKTA
        if selection.has_uri():
            return _import_from_android_document(selection)

        if selection.has_local_path():
            return _import_from_filesystem(selection)

    except BelgeIceAktarmaServisiHatasi:
        raise
    except Exception as exc:
        raise BelgeIceAktarmaServisiHatasi(
            f"İçe aktarma başarısız: {exc}"
        ) from exc

    raise BelgeIceAktarmaServisiHatasi("Desteklenmeyen belge tipi.")
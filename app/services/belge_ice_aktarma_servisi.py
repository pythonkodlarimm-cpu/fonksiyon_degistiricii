# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from kivy.utils import platform

from app.services.android_uri_servisi import (
    AndroidUriServisiHatasi,
    get_app_cache_dir,
    get_display_name as get_uri_display_name,
    read_text as read_text_from_uri,
)
from app.services.dosya_servisi import (
    DosyaServisiHatasi,
    get_app_working_root,
    get_display_name as get_path_display_name,
    read_text as read_text_from_path,
    write_text,
)
from app.ui.dosya_secici_paketi.models import DocumentSelection, DocumentSession


class BelgeIceAktarmaServisiHatasi(ValueError):
    pass


def _normalize_name(name: str) -> str:
    temiz = str(name or "").strip() or "belge.txt"
    for ch in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        temiz = temiz.replace(ch, "_")
    return temiz or "belge.txt"


def _working_root() -> Path:
    if platform == "android":
        root = get_app_cache_dir() / "working_imports"
        root.mkdir(parents=True, exist_ok=True)
        return root

    return get_app_working_root()


def _working_copy_name(display_name: str) -> str:
    zaman = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{zaman}_{_normalize_name(display_name)}"


def _resolve_display_name(selection: DocumentSelection) -> str:
    try:
        name = str(selection.preferred_display_name() or "").strip()
        if name:
            return name
    except Exception:
        pass

    try:
        if selection.has_uri():
            name = str(get_uri_display_name(selection.uri) or "").strip()
            if name:
                return name
    except Exception:
        pass

    try:
        if selection.has_local_path():
            name = str(get_path_display_name(selection.local_path) or "").strip()
            if name:
                return name
    except Exception:
        pass

    return "belge.txt"


def _import_from_android_document(selection: DocumentSelection) -> DocumentSession:
    uri = str(selection.uri or "").strip()
    if not uri:
        raise BelgeIceAktarmaServisiHatasi("Android belge URI boş.")

    display_name = _resolve_display_name(selection)

    try:
        content = read_text_from_uri(uri)
    except AndroidUriServisiHatasi as exc:
        raise BelgeIceAktarmaServisiHatasi(f"Android belge okunamadı: {exc}") from exc

    try:
        target = _working_root() / _working_copy_name(display_name)
        write_text(target, content)
    except Exception as exc:
        raise BelgeIceAktarmaServisiHatasi(f"Çalışma dosyası oluşturulamadı: {exc}") from exc

    return DocumentSession.from_selection(selection, working_local_path=str(target))


def _import_from_filesystem(selection: DocumentSelection) -> DocumentSession:
    source_path = str(selection.local_path or "").strip()
    if not source_path:
        raise BelgeIceAktarmaServisiHatasi("Filesystem belge yolu boş.")

    display_name = _resolve_display_name(selection)

    try:
        content = read_text_from_path(source_path)
    except DosyaServisiHatasi as exc:
        raise BelgeIceAktarmaServisiHatasi(f"Yerel belge okunamadı: {exc}") from exc

    try:
        target = _working_root() / _working_copy_name(display_name)
        write_text(target, content)
    except Exception as exc:
        raise BelgeIceAktarmaServisiHatasi(f"Çalışma kopyası oluşturulamadı: {exc}") from exc

    return DocumentSession.from_selection(selection, working_local_path=str(target))


def belgeyi_ice_aktar(selection: DocumentSelection) -> DocumentSession:
    if selection is None:
        raise BelgeIceAktarmaServisiHatasi("Belge seçimi boş.")

    if selection.is_android_document():
        return _import_from_android_document(selection)

    if selection.is_filesystem():
        return _import_from_filesystem(selection)

    raise BelgeIceAktarmaServisiHatasi(f"Desteklenmeyen belge kaynağı: {selection.source}")
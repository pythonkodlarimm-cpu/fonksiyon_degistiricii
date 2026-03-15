# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from kivy.utils import platform

from app.services.android_uri_servisi import get_app_files_dir, read_text as read_uri_text
from app.services.dosya_servisi import read_text as read_path_text, write_text, get_app_backups_root
from app.ui.dosya_secici_paketi.models import DocumentSession


class BelgeYedekServisiHatasi(ValueError):
    pass


def _normalize_name(name: str) -> str:
    temiz = str(name or "").strip() or "belge"
    for ch in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        temiz = temiz.replace(ch, "_")
    return temiz


def _backup_root() -> Path:
    if platform == "android":
        root = get_app_files_dir() / "document_backups"
        root.mkdir(parents=True, exist_ok=True)
        return root
    return get_app_backups_root()


def _build_backup_path(display_name: str) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return _backup_root() / f"{_normalize_name(display_name)}.{ts}.bak"


def _read_original_content(session: DocumentSession) -> str:
    if session.has_source_uri():
        return read_uri_text(session.source_uri)
    if session.has_source_path():
        return read_path_text(session.source_path)
    raise BelgeYedekServisiHatasi("Orijinal belge bulunamadı.")


def yedek_al(session: DocumentSession) -> str:
    if session is None:
        raise BelgeYedekServisiHatasi("Session boş.")

    display_name = str(session.preferred_display_name() or "belge")
    try:
        content = _read_original_content(session)
        backup_path = _build_backup_path(display_name)
        write_text(backup_path, content)
    except Exception as exc:
        raise BelgeYedekServisiHatasi(f"Yedek alınamadı: {exc}") from exc

    try:
        session.last_backup_path = str(backup_path)
    except Exception:
        pass

    return str(backup_path)
# -*- coding: utf-8 -*-
from __future__ import annotations

from app.services.android_uri_servisi import write_text as write_uri_text
from app.services.belge_yedek_servisi import yedek_al
from app.services.dosya_servisi import write_text as write_path_text
from app.ui.dosya_secici_paketi.models import DocumentSession


class BelgeDisariYazmaServisiHatasi(ValueError):
    pass


def _write_to_original_source(session: DocumentSession, content: str) -> None:
    if session.has_source_uri():
        write_uri_text(session.source_uri, content)
        return
    if session.has_source_path():
        write_path_text(session.source_path, content)
        return
    raise BelgeDisariYazmaServisiHatasi("Orijinal yazma hedefi bulunamadı.")


def _write_to_working_copy(session: DocumentSession, content: str) -> None:
    if not session.has_working_local_path():
        raise BelgeDisariYazmaServisiHatasi("Çalışma kopyası yolu bulunamadı.")
    write_path_text(session.working_local_path, content)


def belgeyi_disari_yaz(session: DocumentSession, content: str) -> str:
    if session is None:
        raise BelgeDisariYazmaServisiHatasi("Session boş.")

    yeni_icerik = str(content or "")
    if not yeni_icerik.strip():
        raise BelgeDisariYazmaServisiHatasi("Yeni içerik boş olamaz.")

    try:
        backup_path = yedek_al(session)
        _write_to_original_source(session, yeni_icerik)
        _write_to_working_copy(session, yeni_icerik)
    except Exception as exc:
        raise BelgeDisariYazmaServisiHatasi(f"Belge dışa yazılamadı: {exc}") from exc

    try:
        session.last_backup_path = str(backup_path or "").strip()
    except Exception:
        pass

    return str(backup_path or "").strip()
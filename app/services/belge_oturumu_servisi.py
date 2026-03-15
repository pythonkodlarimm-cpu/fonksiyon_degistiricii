# -*- coding: utf-8 -*-
from __future__ import annotations

from app.services.belge_disari_yazma_servisi import belgeyi_disari_yaz
from app.services.belge_ice_aktarma_servisi import belgeyi_ice_aktar
from app.services.dosya_servisi import exists
from app.ui.dosya_secici_paketi.models import DocumentSelection, DocumentSession


class BelgeOturumuServisiHatasi(ValueError):
    pass


def oturum_baslat(selection: DocumentSelection) -> DocumentSession:
    if selection is None:
        raise BelgeOturumuServisiHatasi("Belge seçimi boş.")

    try:
        session = belgeyi_ice_aktar(selection)
    except Exception as exc:
        raise BelgeOturumuServisiHatasi(f"Oturum başlatılamadı: {exc}") from exc

    if session is None or not session.has_working_local_path():
        raise BelgeOturumuServisiHatasi("Çalışma kopyası oluşturulamadı.")

    return session


def oturum_identifier(session: DocumentSession) -> str:
    if session is None:
        return ""
    try:
        source_id = str(session.preferred_source_identifier() or "").strip()
        if source_id:
            return source_id
    except Exception:
        pass
    try:
        return str(session.working_local_path or "").strip()
    except Exception:
        return ""


def oturum_display_name(session: DocumentSession) -> str:
    if session is None:
        return ""
    try:
        return str(session.preferred_display_name() or "").strip()
    except Exception:
        return ""


def calisma_dosyasi_yolu(session: DocumentSession) -> str:
    if session is None:
        return ""
    return str(session.working_local_path or "").strip()


def calisma_kopyasi_var_mi(session: DocumentSession) -> bool:
    yol = calisma_dosyasi_yolu(session)
    return bool(yol and exists(yol))


def guncellenmis_icerigi_kaydet(session: DocumentSession, new_content: str) -> str:
    if session is None:
        raise BelgeOturumuServisiHatasi("Session boş.")

    icerik = str(new_content or "")
    if not icerik.strip():
        raise BelgeOturumuServisiHatasi("Yeni içerik boş olamaz.")

    try:
        return str(belgeyi_disari_yaz(session, icerik) or "").strip()
    except Exception as exc:
        raise BelgeOturumuServisiHatasi(f"Kaydetme başarısız: {exc}") from exc


def son_yedek_yolu(session: DocumentSession) -> str:
    if session is None:
        return ""
    try:
        return str(session.last_backup_path or "").strip()
    except Exception:
        return ""
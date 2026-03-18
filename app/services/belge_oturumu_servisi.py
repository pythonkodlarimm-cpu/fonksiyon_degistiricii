# -*- coding: utf-8 -*-
"""
DOSYA: app/services/belge_oturumu_servisi.py

SURUM: 3
"""

from __future__ import annotations

from pathlib import Path

from app.services.belge_disari_yazma_servisi import belgeyi_disari_yaz
from app.services.belge_ice_aktarma_servisi import belgeyi_ice_aktar
from app.services.dosya_servisi import exists
from app.ui.dosya_secici_paketi.models import DocumentSelection, DocumentSession


class BelgeOturumuServisiHatasi(ValueError):
    pass


# =========================================================
# SESSION BAŞLATMA
# =========================================================
def oturum_baslat(selection: DocumentSelection) -> DocumentSession:
    if selection is None:
        raise BelgeOturumuServisiHatasi("Belge seçimi boş.")

    try:
        session = belgeyi_ice_aktar(selection)
    except Exception as exc:
        raise BelgeOturumuServisiHatasi(
            f"Oturum başlatılamadı: {exc}"
        ) from exc

    if session is None:
        raise BelgeOturumuServisiHatasi("Session oluşturulamadı.")

    if not _is_valid_session(session):
        raise BelgeOturumuServisiHatasi(
            "Geçersiz oturum: çalışma kopyası yok veya bozuk."
        )

    return session


# =========================================================
# SESSION VALIDATION
# =========================================================
def _is_valid_session(session: DocumentSession) -> bool:
    try:
        path = Path(str(getattr(session, "working_local_path", "") or "").strip())
        return bool(path and path.exists() and path.is_file())
    except Exception:
        return False


# =========================================================
# IDENTIFIER
# =========================================================
def oturum_identifier(session: DocumentSession) -> str:
    if session is None:
        return ""

    try:
        sid = str(session.preferred_source_identifier() or "").strip()
        if sid:
            return sid
    except Exception:
        pass

    try:
        return str(getattr(session, "working_local_path", "") or "").strip()
    except Exception:
        return ""


# =========================================================
# DISPLAY NAME
# =========================================================
def oturum_display_name(session: DocumentSession) -> str:
    if session is None:
        return ""

    try:
        name = str(session.preferred_display_name() or "").strip()
        return name or "belge"
    except Exception:
        return "belge"


# =========================================================
# WORKING FILE
# =========================================================
def calisma_dosyasi_yolu(session: DocumentSession) -> str:
    if session is None:
        return ""

    try:
        return str(getattr(session, "working_local_path", "") or "").strip()
    except Exception:
        return ""


def calisma_kopyasi_var_mi(session: DocumentSession) -> bool:
    path = calisma_dosyasi_yolu(session)
    if not path:
        return False

    try:
        return bool(exists(path))
    except Exception:
        return False


# =========================================================
# SAVE
# =========================================================
def guncellenmis_icerigi_kaydet(session: DocumentSession, new_content: str) -> str:
    if session is None:
        raise BelgeOturumuServisiHatasi("Session boş.")

    if not _is_valid_session(session):
        raise BelgeOturumuServisiHatasi(
            "Geçersiz session: çalışma kopyası bulunamadı."
        )

    content = str(new_content or "")
    if not content.strip():
        raise BelgeOturumuServisiHatasi("Yeni içerik boş olamaz.")

    try:
        backup_path = belgeyi_disari_yaz(session, content)
    except Exception as exc:
        raise BelgeOturumuServisiHatasi(
            f"Kaydetme başarısız: {exc}"
        ) from exc

    return str(backup_path or "").strip()


# =========================================================
# BACKUP
# =========================================================
def son_yedek_yolu(session: DocumentSession) -> str:
    if session is None:
        return ""

    try:
        path = str(getattr(session, "last_backup_path", "") or "").strip()
        if path and Path(path).exists():
            return path
    except Exception:
        pass

    return ""
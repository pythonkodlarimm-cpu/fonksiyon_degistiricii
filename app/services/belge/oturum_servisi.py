# -*- coding: utf-8 -*-
"""
DOSYA: app/services/belge/oturum_servisi.py

ROL:
- Belge oturumu başlatmak
- Oturum bilgilerini okumak
- Güncellenmiş içeriği kaydetmek
- Session içindeki son yedek bilgisini güvenli biçimde sunmak

MİMARİ:
- Dosya erişimi doğrudan yapılmaz, dosya yöneticisi kullanılır
- Android / URI mantığı içe aktarma ve dışa yazma servislerinde kalır
- Session doğrulaması merkezi tutulur
- Importlar lazy çalışır, servis katmanı gereksiz erken yüklenmez

API UYUMLULUK:
- API 35 uyumlu
- Scoped storage uyumlu
- AdMob ile çakışmaz

SURUM: 6
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.ui.dosya_secici_paketi.models import DocumentSelection, DocumentSession


class BelgeOturumuServisiHatasi(ValueError):
    pass


# =========================================================
# LAZY HELPERS
# =========================================================
def _dosya():
    from app.services.dosya import DosyaYoneticisi
    return DosyaYoneticisi()


def _belgeyi_ice_aktar(selection):
    try:
        from app.services.belge.ice_aktarma_servisi import belgeyi_ice_aktar
        return belgeyi_ice_aktar(selection)
    except Exception as exc:
        raise BelgeOturumuServisiHatasi(f"Oturum başlatılamadı: {exc}") from exc


def _belgeyi_disari_yaz(session, content: str) -> str:
    try:
        from app.services.belge.disari_yazma_servisi import belgeyi_disari_yaz
        return str(belgeyi_disari_yaz(session, content) or "").strip()
    except Exception as exc:
        raise BelgeOturumuServisiHatasi(f"Kaydetme başarısız: {exc}") from exc


# =========================================================
# SESSION BAŞLATMA
# =========================================================
def oturum_baslat(selection) -> "DocumentSession":
    if selection is None:
        raise BelgeOturumuServisiHatasi("Belge seçimi boş.")

    session = _belgeyi_ice_aktar(selection)

    if session is None:
        raise BelgeOturumuServisiHatasi("Session oluşturulamadı.")

    if not _is_valid_session(session):
        raise BelgeOturumuServisiHatasi(
            "Geçersiz oturum: çalışma kopyası yok veya bozuk."
        )

    try:
        session.last_backup_path = ""
    except Exception:
        pass

    return session


# =========================================================
# VALIDATION
# =========================================================
def _is_valid_session(session) -> bool:
    if session is None:
        return False

    try:
        raw = str(getattr(session, "working_local_path", "") or "").strip()
        if not raw:
            return False

        return _dosya().exists(raw)
    except Exception:
        return False


# =========================================================
# IDENTIFIER
# =========================================================
def oturum_identifier(session) -> str:
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
def oturum_display_name(session) -> str:
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
def calisma_dosyasi_yolu(session) -> str:
    if session is None:
        return ""

    try:
        return str(getattr(session, "working_local_path", "") or "").strip()
    except Exception:
        return ""


def calisma_kopyasi_var_mi(session) -> bool:
    path = calisma_dosyasi_yolu(session)
    if not path:
        return False

    try:
        return _dosya().exists(path)
    except Exception:
        return False


# =========================================================
# SAVE
# =========================================================
def guncellenmis_icerigi_kaydet(session, new_content: str) -> str:
    if session is None:
        raise BelgeOturumuServisiHatasi("Session boş.")

    if not _is_valid_session(session):
        raise BelgeOturumuServisiHatasi(
            "Geçersiz session: çalışma kopyası bulunamadı."
        )

    content = str(new_content or "")
    if not content.strip():
        raise BelgeOturumuServisiHatasi("Yeni içerik boş olamaz.")

    backup_path = _belgeyi_disari_yaz(session, content)

    try:
        session.last_backup_path = str(backup_path or "").strip()
    except Exception:
        pass

    return str(backup_path or "").strip()


# =========================================================
# BACKUP
# =========================================================
def son_yedek_yolu(session) -> str:
    if session is None:
        return ""

    try:
        raw = str(getattr(session, "last_backup_path", "") or "").strip()
        if not raw:
            return ""

        if _dosya().exists(raw):
            return raw
    except Exception:
        pass

    return ""
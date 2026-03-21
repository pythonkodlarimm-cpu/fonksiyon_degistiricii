# -*- coding: utf-8 -*-
"""
DOSYA: app/services/belge/disari_yazma_servisi.py

ROL:
- Belge içeriğini orijinal kaynağa yazmak
- Çalışma kopyasını güncellemek
- Yazmadan önce yedek almak
- Session içindeki son yedek bilgisini güncellemek

MİMARİ:
- Girdi: session + yeni içerik
- Önce yedek alınır
- Sonra orijinal kaynak güncellenir
- Ardından çalışma kopyası güncellenir
- Başarılıysa session.last_backup_path güncellenir
- Importlar lazy çalışır, servis katmanı açılışta gereksiz yük oluşturmaz

API 35 UYUMLULUK:
- SAF (content://) öncelikli
- Path fallback korunur
- Android / non-android ayrımı güvenli
- Hata durumunda veri kaybı önlenir (önce yedek)

SURUM: 6
TARIH: 2026-03-20
IMZA: FY.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.ui.dosya_secici_paketi.models import DocumentSession


class BelgeDisariYazmaServisiHatasi(ValueError):
    pass


# =========================================================
# LAZY IMPORT HELPERS
# =========================================================
def _write_uri_text(uri: str, content: str) -> None:
    try:
        from app.services.android.uri_servisi import write_text
        write_text(uri, content)
    except Exception as exc:
        raise BelgeDisariYazmaServisiHatasi(
            f"URI kaynağı yazılamadı: {exc}"
        ) from exc


def _write_path_text(path: str, content: str) -> None:
    try:
        from app.services.dosya.servisi import write_text
        write_text(path, content)
    except Exception as exc:
        raise BelgeDisariYazmaServisiHatasi(
            f"Path kaynağı yazılamadı: {exc}"
        ) from exc


def _yedek_al(session) -> str:
    try:
        from app.services.belge.yedek_servisi import yedek_al
        return str(yedek_al(session) or "").strip()
    except Exception as exc:
        raise BelgeDisariYazmaServisiHatasi(
            f"Yedek alınamadı: {exc}"
        ) from exc


# =========================================================
# SESSION VALIDATION
# =========================================================
def _session_var_mi(session) -> None:
    if session is None:
        raise BelgeDisariYazmaServisiHatasi("Session boş.")


def _call_bool_method(obj, method_name: str) -> bool:
    try:
        method = getattr(obj, method_name, None)
        if callable(method):
            return bool(method())
    except Exception:
        pass
    return False


def _session_has_source_uri(session) -> bool:
    return _call_bool_method(session, "has_source_uri")


def _session_has_source_path(session) -> bool:
    return _call_bool_method(session, "has_source_path")


def _session_has_working_local_path(session) -> bool:
    return _call_bool_method(session, "has_working_local_path")


# =========================================================
# ORIGINAL WRITE
# =========================================================
def _write_to_original_source(session, content: str) -> None:
    _session_var_mi(session)

    if _session_has_source_uri(session):
        uri = str(getattr(session, "source_uri", "") or "").strip()
        if not uri:
            raise BelgeDisariYazmaServisiHatasi("Kaynak URI boş.")
        _write_uri_text(uri, content)
        return

    if _session_has_source_path(session):
        path = str(getattr(session, "source_path", "") or "").strip()
        if not path:
            raise BelgeDisariYazmaServisiHatasi("Kaynak path boş.")
        _write_path_text(path, content)
        return

    raise BelgeDisariYazmaServisiHatasi("Yazılacak orijinal kaynak bulunamadı.")


# =========================================================
# WORKING COPY
# =========================================================
def _write_to_working_copy(session, content: str) -> None:
    _session_var_mi(session)

    if not _session_has_working_local_path(session):
        raise BelgeDisariYazmaServisiHatasi("Çalışma kopyası yok.")

    working_path = str(getattr(session, "working_local_path", "") or "").strip()
    if not working_path:
        raise BelgeDisariYazmaServisiHatasi("Çalışma kopyası yolu boş.")

    _write_path_text(working_path, content)


# =========================================================
# MAIN API
# =========================================================
def belgeyi_disari_yaz(session, content: str) -> str:
    _session_var_mi(session)

    yeni_icerik = str(content or "")
    if not yeni_icerik.strip():
        raise BelgeDisariYazmaServisiHatasi("İçerik boş olamaz.")

    # 1) Önce yedek
    backup_path = _yedek_al(session)

    # 2) Orijinal kaynağa yaz
    _write_to_original_source(session, yeni_icerik)

    # 3) Çalışma kopyasını güncelle
    _write_to_working_copy(session, yeni_icerik)

    # 4) Session son yedek bilgisi
    try:
        session.last_backup_path = str(backup_path or "").strip()
    except Exception:
        pass

    return str(backup_path or "").strip()
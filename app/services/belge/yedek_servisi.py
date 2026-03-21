# -*- coding: utf-8 -*-
"""
DOSYA: app/services/belge/yedek_servisi.py

ROL:
- Belgenin mevcut/orijinal içeriğini okuyup yedeğini almak
- Sabit ve yazılabilir uygulama yedek klasörüne yedek yazmak
- Session içine son yedek yolunu kaydetmek

MİMARİ:
- Girdi: DocumentSession
- Orijinal kaynak URI veya path olabilir
- İçerik okunur
- Yedek sadece uygulamanın güvenli yedek alanına yazılır
- Çıktı: yedek dosya yolu

API UYUMLULUK:
- API 35 uyumlu
- Scoped storage dostu
- Tek sabit yedek kökü ile hızlı ve kararlı çalışır
- APK / AAB davranış farkını azaltacak şekilde uygulama içi güvenli klasör kullanır

SURUM: 9
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path

from app.services.android.uri_servisi import (
    AndroidUriServisiHatasi,
    read_text as read_uri_text,
)
from app.services.dosya.servisi import (
    DosyaServisiHatasi,
    get_app_backups_root,
    read_text as read_path_text,
    write_text,
)
from app.ui.dosya_secici_paketi.models import DocumentSession


class BelgeYedekServisiHatasi(ValueError):
    """Belge yedekleme işlemleri sırasında oluşan kontrollü hata."""


def _normalize_name(name: str) -> str:
    """
    Yedek dosya adında kullanılacak adı normalize eder.
    """
    temiz = str(name or "").strip() or "belge"
    for ch in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        temiz = temiz.replace(ch, "_")
    return temiz or "belge"


def _source_identity_hash(session: DocumentSession) -> str:
    """
    Kaynağı ayırt etmek için kısa ve stabil bir hash üretir.
    """
    try:
        if session is not None and session.has_source_uri():
            ham = str(getattr(session, "source_uri", "") or "").strip()
            if ham:
                return hashlib.sha1(ham.encode("utf-8")).hexdigest()[:10]
    except Exception:
        pass

    try:
        if session is not None and session.has_source_path():
            ham = str(getattr(session, "source_path", "") or "").strip()
            if ham:
                return hashlib.sha1(ham.encode("utf-8")).hexdigest()[:10]
    except Exception:
        pass

    return hashlib.sha1(b"belge").hexdigest()[:10]


def _backup_root() -> Path:
    """
    Sabit uygulama yedek klasörünü hazırlar ve döndürür.
    """
    try:
        root = get_app_backups_root()
        root.mkdir(parents=True, exist_ok=True)

        test_file = root / ".write_test.tmp"
        test_file.write_text("ok", encoding="utf-8")
        try:
            test_file.unlink(missing_ok=True)
        except TypeError:
            if test_file.exists():
                test_file.unlink()

        return root
    except Exception as exc:
        raise BelgeYedekServisiHatasi(
            f"Yedek klasörü hazırlanamadı: {exc}"
        ) from exc


def _build_backup_path(session: DocumentSession, display_name: str) -> Path:
    """
    Yedek dosyası için benzersiz bir path üretir.
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    kaynak_hash = _source_identity_hash(session)
    temiz_ad = _normalize_name(display_name)
    return _backup_root() / f"{temiz_ad}.{kaynak_hash}.{ts}.bak"


def _read_original_content(session: DocumentSession) -> str:
    """
    Session içindeki orijinal kaynaktan içeriği okur.

    Öncelik:
    1) source_uri
    2) source_path
    """
    if session is None:
        raise BelgeYedekServisiHatasi("Session boş.")

    try:
        if session.has_source_uri():
            uri = str(getattr(session, "source_uri", "") or "").strip()
            if not uri:
                raise ValueError("source_uri boş")
            return read_uri_text(uri)

        if session.has_source_path():
            path = str(getattr(session, "source_path", "") or "").strip()
            if not path:
                raise ValueError("source_path boş")
            return read_path_text(path)

    except (AndroidUriServisiHatasi, DosyaServisiHatasi) as exc:
        raise BelgeYedekServisiHatasi(
            f"Orijinal içerik okunamadı: {exc}"
        ) from exc
    except Exception as exc:
        raise BelgeYedekServisiHatasi(
            f"Orijinal içerik alınamadı: {exc}"
        ) from exc

    raise BelgeYedekServisiHatasi("Orijinal belge bulunamadı.")


def yedek_al(session: DocumentSession) -> str:
    """
    Session içindeki orijinal belgenin yedeğini alır.

    İş akışı:
    1) session doğrulanır
    2) orijinal içerik okunur
    3) sabit yedek kökü hazırlanır
    4) yedek dosyası yazılır
    5) session.last_backup_path güncellenir

    Çıktı:
    - oluşturulan yedek dosyasının yolu
    """
    if session is None:
        raise BelgeYedekServisiHatasi("Session boş.")

    try:
        display_name = str(session.preferred_display_name() or "belge").strip() or "belge"
    except Exception:
        display_name = "belge"

    try:
        content = _read_original_content(session)
        backup_path = _build_backup_path(session, display_name)
        write_text(backup_path, content)
    except BelgeYedekServisiHatasi:
        raise
    except Exception as exc:
        raise BelgeYedekServisiHatasi(
            f"Yedek alınamadı: {exc}"
        ) from exc

    try:
        session.last_backup_path = str(backup_path)
    except Exception:
        pass

    return str(backup_path)
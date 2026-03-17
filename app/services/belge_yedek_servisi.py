# -*- coding: utf-8 -*-
"""
DOSYA: app/services/belge_yedek_servisi.py

ROL:
- Belgenin mevcut/orijinal içeriğini okuyup yedeğini almak
- Yedeği uygulamanın güvenli alanına yazmak
- Session içine son yedek yolunu kaydetmek

MİMARİ:
- Girdi: DocumentSession
- Orijinal kaynak URI veya path olabilir
- İçerik okunur
- Uygulama içindeki backups alanına .bak dosyası yazılır
- Çıktı: yedek dosya yolu

API UYUMLULUK DEĞERLENDİRMESİ:
- Android tarafında yedekler uygulamanın sandbox/files alanında tutulur
- content:// URI kaynakları SAF tabanlı okunur
- Bu düzenlenmiş sürüm API 34 hedeflenerek güvenli hale getirilmiştir
- Genel uyumluluk hedefi: API 30+ / özellikle API 34

SURUM: 2
TARIH: 2026-03-17
IMZA: FY.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from kivy.utils import platform

from app.services.android_uri_servisi import (
    AndroidUriServisiHatasi,
    get_app_files_dir,
    read_text as read_uri_text,
)
from app.services.dosya_servisi import (
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

    API 34 uyumluluk notu:
    - Yerel dosya sistemi için geçersiz karakterler temizlenir.
    """
    temiz = str(name or "").strip() or "belge"
    for ch in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        temiz = temiz.replace(ch, "_")
    return temiz or "belge"


def _backup_root() -> Path:
    """
    Yedeklerin yazılacağı kök dizini döndürür.

    Android:
    - uygulamanın files alanı altında document_backups

    Android dışı:
    - uygulamanın backups kökü

    API 34 uyumluluk notu:
    - Android tarafında uygulama sandbox/files alanı kullanılır.
    """
    try:
        if platform == "android":
            root = get_app_files_dir() / "document_backups"
            root.mkdir(parents=True, exist_ok=True)
            return root

        root = get_app_backups_root()
        root.mkdir(parents=True, exist_ok=True)
        return root
    except Exception as exc:
        raise BelgeYedekServisiHatasi(
            f"Yedek klasörü hazırlanamadı: {exc}"
        ) from exc


def _build_backup_path(display_name: str) -> Path:
    """
    Yedek dosyası için benzersiz bir path üretir.

    API 34 uyumluluk notu:
    - Aynı belgede birden fazla yedek alınabilmesi için zaman damgası kullanılır.
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return _backup_root() / f"{_normalize_name(display_name)}.{ts}.bak"


def _read_original_content(session: DocumentSession) -> str:
    """
    Session içindeki orijinal kaynaktan içeriği okur.

    Öncelik:
    1) source_uri
    2) source_path

    API 34 uyumluluk notu:
    - Android belge kaynakları content:// URI üzerinden okunur.
    """
    if session is None:
        raise BelgeYedekServisiHatasi("Session boş.")

    try:
        if session.has_source_uri():
            return read_uri_text(str(getattr(session, "source_uri", "") or "").strip())

        if session.has_source_path():
            return read_path_text(str(getattr(session, "source_path", "") or "").strip())
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
    3) yedek path üretilir
    4) yedek dosyası yazılır
    5) session.last_backup_path güncellenir

    Çıktı:
    - oluşturulan yedek dosyasının yolu

    API 34 uyumluluk notu:
    - Yedekleme uygulamanın yerel güvenli alanında tutulur.
    """
    if session is None:
        raise BelgeYedekServisiHatasi("Session boş.")

    try:
        display_name = str(session.preferred_display_name() or "belge").strip() or "belge"
    except Exception:
        display_name = "belge"

    try:
        content = _read_original_content(session)
        backup_path = _build_backup_path(display_name)
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
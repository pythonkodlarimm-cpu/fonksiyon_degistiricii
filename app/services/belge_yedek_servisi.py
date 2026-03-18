# -*- coding: utf-8 -*-
"""
DOSYA: app/services/belge_yedek_servisi.py

ROL:
- Belgenin mevcut/orijinal içeriğini okuyup yedeğini almak
- Yedeği görünür ve ortak bir klasöre yazmak
- Session içine son yedek yolunu kaydetmek

MİMARİ:
- Girdi: DocumentSession
- Orijinal kaynak URI veya path olabilir
- İçerik okunur
- Ortak backups alanına .bak dosyası yazılır
- Çıktı: yedek dosya yolu

API UYUMLULUK DEĞERLENDİRMESİ:
- Bu sürümde yedekler görünür ortak klasörde tutulur
- Hedef klasör: /storage/emulated/0/FonksiyonDegistirici/backups
- content:// URI kaynakları SAF tabanlı okunur
- Android 11+ ve özellikle API 34 için tek yerde toplanmış yedek mantığı uygundur
- Pydroid ve APK tarafında aynı klasör mantığıyla daha tutarlı çalışır

SURUM: 3
TARIH: 2026-03-17
IMZA: FY.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from app.services.android_uri_servisi import (
    AndroidUriServisiHatasi,
    read_text as read_uri_text,
)
from app.services.dosya_servisi import (
    DosyaServisiHatasi,
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

    Hedef:
    - /storage/emulated/0/FonksiyonDegistirici/backups

    API 34 uyumluluk notu:
    - Yedeklerin tek görünür klasörde toplanması
      listeleme / görüntüleme / indirme akışını sadeleştirir.
    - Klasör yoksa otomatik oluşturulur.
    """
    try:
        root = Path("/storage/emulated/0/FonksiyonDegistirici/backups")
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
    - Aynı belge için birden fazla yedek alınabilmesi adına
      zaman damgalı dosya adı kullanılır.
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
            return read_uri_text(
                str(getattr(session, "source_uri", "") or "").strip()
            )

        if session.has_source_path():
            return read_path_text(
                str(getattr(session, "source_path", "") or "").strip()
            )

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
    - Yedekleme görünür ortak klasörde tutulur:
      /storage/emulated/0/FonksiyonDegistirici/backups
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
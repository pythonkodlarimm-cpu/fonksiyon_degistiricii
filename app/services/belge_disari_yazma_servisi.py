# -*- coding: utf-8 -*-
"""
DOSYA: app/services/belge_disari_yazma_servisi.py

ROL:
- Belge içeriğini orijinal kaynağa yazmak
- Çalışma kopyasını güncellemek
- Yazmadan önce yedek almak
- Session içindeki son yedek bilgisini güncellemek

MİMARİ:
- Girdi: DocumentSession + yeni içerik
- Önce yedek alınır
- Sonra orijinal kaynak güncellenir
- Ardından çalışma kopyası güncellenir
- Başarılıysa session.last_backup_path güncellenir

API 34 UYUMLULUK DEĞERLENDİRMESİ:
- Android tarafında orijinal kaynak content:// URI ise yazma işlemi
  android_uri_servisi üzerinden yapılır
- Doğrudan dosya yolu varsa path tabanlı yazma kullanılır
- SAF/content URI akışı korunur
- Yedekleme tarafı artık görünür ortak klasöre yazıldığı için
  bu servis de o yeni akışla uyumlu çalışır
- Genel hedef uyumluluk: API 30+ ve özellikle API 34

SURUM: 3
TARIH: 2026-03-17
IMZA: FY.
"""

from __future__ import annotations

from app.services.android_uri_servisi import (
    AndroidUriServisiHatasi,
    write_text as write_uri_text,
)
from app.services.belge_yedek_servisi import (
    BelgeYedekServisiHatasi,
    yedek_al,
)
from app.services.dosya_servisi import (
    DosyaServisiHatasi,
    write_text as write_path_text,
)
from app.ui.dosya_secici_paketi.models import DocumentSession


class BelgeDisariYazmaServisiHatasi(ValueError):
    """Belge dışa yazma işlemleri sırasında oluşan kontrollü hata."""


def _write_to_original_source(session: DocumentSession, content: str) -> None:
    """
    Belgenin orijinal kaynağına içerik yazar.

    Öncelik:
    1) source_uri varsa URI üzerinden
    2) source_path varsa dosya yolu üzerinden

    API 34 uyumluluk notu:
    - Android SAF ile seçilen belgelerde source_uri tercih edilir
    - content:// URI varsa android_uri_servisi üzerinden yazılır
    """
    if session is None:
        raise BelgeDisariYazmaServisiHatasi("Session boş.")

    try:
        if session.has_source_uri():
            write_uri_text(
                str(getattr(session, "source_uri", "") or "").strip(),
                str(content or ""),
            )
            return

        if session.has_source_path():
            write_path_text(
                str(getattr(session, "source_path", "") or "").strip(),
                str(content or ""),
            )
            return

    except (AndroidUriServisiHatasi, DosyaServisiHatasi) as exc:
        raise BelgeDisariYazmaServisiHatasi(
            f"Orijinal kaynak yazılamadı: {exc}"
        ) from exc
    except Exception as exc:
        raise BelgeDisariYazmaServisiHatasi(
            f"Orijinal kaynak yazılamadı: {exc}"
        ) from exc

    raise BelgeDisariYazmaServisiHatasi("Orijinal yazma hedefi bulunamadı.")


def _write_to_working_copy(session: DocumentSession, content: str) -> None:
    """
    İçeriği çalışma kopyasına yazar.

    API 34 uyumluluk notu:
    - Çalışma kopyası uygulamanın yerel alanında tutulur
    - Path tabanlı yazma kullanılır
    """
    if session is None:
        raise BelgeDisariYazmaServisiHatasi("Session boş.")

    if not session.has_working_local_path():
        raise BelgeDisariYazmaServisiHatasi("Çalışma kopyası yolu bulunamadı.")

    try:
        write_path_text(
            str(getattr(session, "working_local_path", "") or "").strip(),
            str(content or ""),
        )
    except DosyaServisiHatasi as exc:
        raise BelgeDisariYazmaServisiHatasi(
            f"Çalışma kopyası yazılamadı: {exc}"
        ) from exc
    except Exception as exc:
        raise BelgeDisariYazmaServisiHatasi(
            f"Çalışma kopyası yazılamadı: {exc}"
        ) from exc


def belgeyi_disari_yaz(session: DocumentSession, content: str) -> str:
    """
    Belgeyi dış kaynağa ve çalışma kopyasına yazar.

    İş akışı:
    1) Session doğrulanır
    2) İçerik doğrulanır
    3) Yedek alınır
    4) Orijinal kaynak güncellenir
    5) Çalışma kopyası güncellenir
    6) Son yedek yolu session içine yazılır

    Geri dönüş:
    - Oluşturulan yedek dosyasının yolu

    API 34 uyumluluk notu:
    - source_uri varsa Android URI/SAF akışı kullanılır
    - source_path varsa path tabanlı yazma kullanılır
    - Yedek klasörü artık görünür ortak klasör akışıyla uyumludur
    """
    if session is None:
        raise BelgeDisariYazmaServisiHatasi("Session boş.")

    yeni_icerik = str(content or "")
    if not yeni_icerik.strip():
        raise BelgeDisariYazmaServisiHatasi("Yeni içerik boş olamaz.")

    try:
        backup_path = yedek_al(session)
        _write_to_original_source(session, yeni_icerik)
        _write_to_working_copy(session, yeni_icerik)

    except (BelgeYedekServisiHatasi, BelgeDisariYazmaServisiHatasi):
        raise
    except Exception as exc:
        raise BelgeDisariYazmaServisiHatasi(
            f"Belge dışa yazılamadı: {exc}"
        ) from exc

    try:
        session.last_backup_path = str(backup_path or "").strip()
    except Exception:
        pass

    return str(backup_path or "").strip()
# -*- coding: utf-8 -*-
"""
DOSYA: app/services/belge_geri_yukleme_servisi.py

ROL:
- Belgenin son yedeğini geri yüklemek
- Geri yükleme sonrası çalışma kopyasını da senkron tutmak

MİMARİ:
- Girdi: DocumentSession
- Son yedek dosyasını bulur
- İçeriği okur
- Orijinal kaynağa geri yazar
- Çalışma kopyasını da aynı içerikle günceller

API 34 UYUMLULUK NOTU:
- Orijinal kaynak bir content:// URI ise android_uri_servisi üzerinden yazılır
- Orijinal kaynak dosya yolu ise path tabanlı yazma kullanılır
- SAF/content URI akışı korunur

SURUM: 3
TARIH: 2026-03-17
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path

from app.services.android_uri_servisi import (
    AndroidUriServisiHatasi,
    write_text as write_uri_text,
)
from app.services.dosya_servisi import (
    DosyaServisiHatasi,
    read_text as read_path_text,
    write_text as write_path_text,
)
from app.ui.dosya_secici_paketi.models import DocumentSession


class BelgeGeriYuklemeServisiHatasi(ValueError):
    """Belge geri yükleme sırasında oluşan kontrollü hata."""


def _yedek_yolu(session: DocumentSession) -> Path:
    """
    Session içindeki son yedek yolunu döndürür ve doğrular.
    """
    try:
        path = Path(str(getattr(session, "last_backup_path", "") or "").strip())
    except Exception:
        path = Path("")

    if not path or not path.exists() or not path.is_file():
        raise BelgeGeriYuklemeServisiHatasi(
            "Geçerli bir yedek dosyası bulunamadı."
        )

    return path


def _orijinale_yaz(session: DocumentSession, content: str) -> None:
    """
    İçeriği orijinal kaynağa geri yazar.
    """
    if session is None:
        raise BelgeGeriYuklemeServisiHatasi("Session boş.")

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
        raise BelgeGeriYuklemeServisiHatasi(
            f"Orijinal kaynağa yazılamadı: {exc}"
        ) from exc
    except Exception as exc:
        raise BelgeGeriYuklemeServisiHatasi(
            f"Orijinal yazma hatası: {exc}"
        ) from exc

    raise BelgeGeriYuklemeServisiHatasi(
        "Orijinal geri yükleme hedefi bulunamadı."
    )


def _working_kopyayi_guncelle(session: DocumentSession, content: str) -> None:
    """
    Çalışma kopyasını günceller.
    """
    if session is None:
        raise BelgeGeriYuklemeServisiHatasi("Session boş.")

    if not session.has_working_local_path():
        raise BelgeGeriYuklemeServisiHatasi(
            "Çalışma kopyası yolu bulunamadı."
        )

    try:
        write_path_text(
            str(getattr(session, "working_local_path", "") or "").strip(),
            str(content or ""),
        )
    except DosyaServisiHatasi as exc:
        raise BelgeGeriYuklemeServisiHatasi(
            f"Çalışma kopyası yazılamadı: {exc}"
        ) from exc
    except Exception as exc:
        raise BelgeGeriYuklemeServisiHatasi(
            f"Çalışma kopyası güncellenemedi: {exc}"
        ) from exc


def son_yedekten_geri_yukle(session: DocumentSession) -> str:
    """
    Session içindeki son yedeği geri yükler.
    """
    if session is None:
        raise BelgeGeriYuklemeServisiHatasi("Session boş.")

    try:
        backup_path = _yedek_yolu(session)
        backup_content = read_path_text(backup_path)
    except BelgeGeriYuklemeServisiHatasi:
        raise
    except Exception as exc:
        raise BelgeGeriYuklemeServisiHatasi(
            f"Yedek okunamadı: {exc}"
        ) from exc

    try:
        _orijinale_yaz(session, backup_content)
        _working_kopyayi_guncelle(session, backup_content)
    except BelgeGeriYuklemeServisiHatasi:
        raise
    except Exception as exc:
        raise BelgeGeriYuklemeServisiHatasi(
            f"Geri yükleme başarısız: {exc}"
        ) from exc

    return str(backup_path)
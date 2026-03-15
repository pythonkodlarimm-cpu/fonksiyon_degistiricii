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

SURUM: 1
TARIH: 2026-03-16
IMZA: FY.
"""

from __future__ import annotations

from app.services.android_uri_servisi import write_text as write_uri_text
from app.services.dosya_servisi import read_text as read_path_text
from app.services.dosya_servisi import write_text as write_path_text
from app.ui.dosya_secici_paketi.models import DocumentSession


class BelgeGeriYuklemeServisiHatasi(ValueError):
    """Belge geri yükleme sırasında oluşan kontrollü hata."""


def _yedek_yolu(session: DocumentSession) -> str:
    try:
        return str(getattr(session, "last_backup_path", "") or "").strip()
    except Exception:
        return ""


def _orijinale_yaz(session: DocumentSession, content: str) -> None:
    if session.has_source_uri():
        write_uri_text(session.source_uri, content)
        return

    if session.has_source_path():
        write_path_text(session.source_path, content)
        return

    raise BelgeGeriYuklemeServisiHatasi(
        "Orijinal geri yükleme hedefi bulunamadı."
    )


def _working_kopyayi_guncelle(session: DocumentSession, content: str) -> None:
    if not session.has_working_local_path():
        raise BelgeGeriYuklemeServisiHatasi(
            "Çalışma kopyası yolu bulunamadı."
        )

    write_path_text(session.working_local_path, content)


def son_yedekten_geri_yukle(session: DocumentSession) -> str:
    """
    Session içindeki son yedeği geri yükler.

    Çıktı:
    - geri yüklenen yedek yolu
    """
    if session is None:
        raise BelgeGeriYuklemeServisiHatasi("Session boş.")

    backup_path = _yedek_yolu(session)
    if not backup_path:
        raise BelgeGeriYuklemeServisiHatasi("Geri yüklenecek yedek bulunamadı.")

    try:
        backup_content = read_path_text(backup_path)
    except Exception as exc:
        raise BelgeGeriYuklemeServisiHatasi(
            f"Yedek dosya okunamadı: {exc}"
        ) from exc

    try:
        _orijinale_yaz(session, backup_content)
    except Exception as exc:
        raise BelgeGeriYuklemeServisiHatasi(
            f"Orijinal dosyaya geri yüklenemedi: {exc}"
        ) from exc

    try:
        _working_kopyayi_guncelle(session, backup_content)
    except Exception as exc:
        raise BelgeGeriYuklemeServisiHatasi(
            f"Çalışma kopyası geri yüklenemedi: {exc}"
        ) from exc

    return backup_path
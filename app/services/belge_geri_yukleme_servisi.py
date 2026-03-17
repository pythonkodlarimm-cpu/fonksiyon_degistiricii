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
- SAF/content URI akışı korunarak Android 14 hedefinde güvenli geri yükleme sağlanır

SURUM: 2
TARIH: 2026-03-17
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
    """
    Session içindeki son yedek yolunu güvenli biçimde döndürür.

    API 34 uyumluluk notu:
    - Yedekler uygulamanın yerel çalışma alanında tutulduğu için path tabanlı okunur.
    """
    try:
        return str(getattr(session, "last_backup_path", "") or "").strip()
    except Exception:
        return ""


def _orijinale_yaz(session: DocumentSession, content: str) -> None:
    """
    Geri yüklenecek içeriği orijinal kaynağa yazar.

    Öncelik:
    1) source_uri varsa URI üzerinden yazılır
    2) source_path varsa dosya yolu üzerinden yazılır

    API 34 uyumluluk notu:
    - Android SAF ile seçilmiş belgelerde source_uri tercih edilir.
    """
    if session is None:
        raise BelgeGeriYuklemeServisiHatasi("Session boş.")

    try:
        if session.has_source_uri():
            write_uri_text(str(session.source_uri or "").strip(), content)
            return

        if session.has_source_path():
            write_path_text(str(session.source_path or "").strip(), content)
            return
    except Exception as exc:
        raise BelgeGeriYuklemeServisiHatasi(
            f"Orijinal geri yükleme hedefine yazılamadı: {exc}"
        ) from exc

    raise BelgeGeriYuklemeServisiHatasi(
        "Orijinal geri yükleme hedefi bulunamadı."
    )


def _working_kopyayi_guncelle(session: DocumentSession, content: str) -> None:
    """
    Geri yüklenen içeriği çalışma kopyasına da yazar.

    API 34 uyumluluk notu:
    - Çalışma kopyası uygulamanın yerel alanında tutulur ve path tabanlı güncellenir.
    """
    if session is None:
        raise BelgeGeriYuklemeServisiHatasi("Session boş.")

    if not session.has_working_local_path():
        raise BelgeGeriYuklemeServisiHatasi(
            "Çalışma kopyası yolu bulunamadı."
        )

    try:
        write_path_text(str(session.working_local_path or "").strip(), content)
    except Exception as exc:
        raise BelgeGeriYuklemeServisiHatasi(
            f"Çalışma kopyası güncellenemedi: {exc}"
        ) from exc


def son_yedekten_geri_yukle(session: DocumentSession) -> str:
    """
    Session içindeki son yedeği geri yükler.

    İş akışı:
    1) Session doğrulanır
    2) Son yedek yolu alınır
    3) Yedek içeriği okunur
    4) Orijinal kaynağa yazılır
    5) Çalışma kopyası güncellenir

    Çıktı:
    - geri yüklenen yedek yolu

    API 34 uyumluluk notu:
    - content:// URI kaynakları SAF üzerinden geri yazılır
    - yerel çalışma kopyası ayrıca senkron tutulur
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
    except BelgeGeriYuklemeServisiHatasi:
        raise
    except Exception as exc:
        raise BelgeGeriYuklemeServisiHatasi(
            f"Orijinal dosyaya geri yüklenemedi: {exc}"
        ) from exc

    try:
        _working_kopyayi_guncelle(session, backup_content)
    except BelgeGeriYuklemeServisiHatasi:
        raise
    except Exception as exc:
        raise BelgeGeriYuklemeServisiHatasi(
            f"Çalışma kopyası geri yüklenemedi: {exc}"
        ) from exc

    return str(backup_path or "").strip()
# -*- coding: utf-8 -*-
"""
DOSYA: app/services/belge/geri_yukleme_servisi.py

ROL:
- Belgenin son yedeğini geri yüklemek
- Geri yükleme sonrası çalışma kopyasını da senkron tutmak

MİMARİ:
- Girdi: DocumentSession
- Önce session.last_backup_path kontrol edilir
- Geçersizse olası yedek klasörlerinde son uygun yedek aranır
- İçerik okunur
- Orijinal kaynağa geri yazılır
- Çalışma kopyası da aynı içerikle güncellenir

API 35 UYUMLULUK NOTU:
- Orijinal kaynak bir content:// URI ise android/uri_servisi üzerinden yazılır
- Orijinal kaynak dosya yolu ise dosya/servisi üzerinden yazma kullanılır
- SAF/content URI akışı korunur
- Yedek konumu tek klasöre kör bağımlı değildir
- Fallback mantığı korunur
- APK / AAB davranış farkını azaltmak için servis katmanları ayrılmıştır

SURUM: 5
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path

from app.services.android.uri_servisi import (
    AndroidUriServisiHatasi,
    write_text as write_uri_text,
)
from app.services.dosya.servisi import (
    DosyaServisiHatasi,
    read_text as read_path_text,
    write_text as write_path_text,
)
from app.ui.dosya_secici_paketi.models import DocumentSession


class BelgeGeriYuklemeServisiHatasi(ValueError):
    """Belge geri yükleme sırasında oluşan kontrollü hata."""


def _normalize_name(name: str) -> str:
    """
    Yedek dosya adını eşleştirmek için display name'i normalize eder.
    """
    temiz = str(name or "").strip() or "belge"
    for ch in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        temiz = temiz.replace(ch, "_")
    return temiz or "belge"


def _candidate_backup_roots(session: DocumentSession) -> list[Path]:
    """
    Olası yedek köklerini öncelik sırasıyla üretir.

    Öncelik:
    1) Kaynak dosyanın bulunduğu klasörde backups
    2) Kaynak dosyanın bulunduğu klasörde .yedekler
    3) Public ortak klasör
    """
    roots: list[Path] = []

    try:
        if session is not None and session.has_source_path():
            source_path = Path(str(getattr(session, "source_path", "") or "").strip())
            parent = source_path.parent
            if str(parent).strip():
                roots.append(parent / "backups")
                roots.append(parent / ".yedekler")
    except Exception:
        pass

    roots.append(Path("/storage/emulated/0/FonksiyonDegistirici/backups"))

    uniq: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        key = str(root)
        if key not in seen:
            uniq.append(root)
            seen.add(key)

    return uniq


def _session_backup_path(session: DocumentSession) -> Path | None:
    """
    Session içindeki son yedek yolunu okumaya çalışır.
    """
    try:
        raw = str(getattr(session, "last_backup_path", "") or "").strip()
        if not raw:
            return None

        path = Path(raw)
        if path.exists() and path.is_file():
            return path
    except Exception:
        pass

    return None


def _find_latest_backup_from_roots(session: DocumentSession) -> Path | None:
    """
    Bilinen yedek klasörlerinde bu belgeye ait en güncel yedeği arar.
    """
    try:
        display_name = str(session.preferred_display_name() or "belge").strip() or "belge"
    except Exception:
        display_name = "belge"

    normalized = _normalize_name(display_name)
    pattern = f"{normalized}.*.bak"

    adaylar: list[Path] = []

    for root in _candidate_backup_roots(session):
        try:
            if root.exists() and root.is_dir():
                for item in root.glob(pattern):
                    try:
                        if item.is_file():
                            adaylar.append(item)
                    except Exception:
                        continue
        except Exception:
            continue

    if not adaylar:
        return None

    try:
        adaylar.sort(key=lambda path_obj: path_obj.stat().st_mtime, reverse=True)
    except Exception:
        adaylar.sort(reverse=True)

    return adaylar[0]


def _yedek_yolu(session: DocumentSession) -> Path:
    """
    Session için geri yüklenebilir en uygun yedek yolunu bulur.
    """
    if session is None:
        raise BelgeGeriYuklemeServisiHatasi("Session boş.")

    direct_path = _session_backup_path(session)
    if direct_path is not None:
        return direct_path

    fallback_path = _find_latest_backup_from_roots(session)
    if fallback_path is not None:
        try:
            session.last_backup_path = str(fallback_path)
        except Exception:
            pass
        return fallback_path

    raise BelgeGeriYuklemeServisiHatasi(
        "Geçerli bir yedek dosyası bulunamadı."
    )


def _orijinale_yaz(session: DocumentSession, content: str) -> None:
    """
    İçeriği orijinal kaynağa geri yazar.
    """
    if session is None:
        raise BelgeGeriYuklemeServisiHatasi("Session boş.")

    try:
        if session.has_source_uri():
            uri = str(getattr(session, "source_uri", "") or "").strip()
            if not uri:
                raise ValueError("source_uri boş")

            write_uri_text(uri, str(content or ""))
            return

        if session.has_source_path():
            path = str(getattr(session, "source_path", "") or "").strip()
            if not path:
                raise ValueError("source_path boş")

            write_path_text(path, str(content or ""))
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
        working_path = str(getattr(session, "working_local_path", "") or "").strip()
        if not working_path:
            raise ValueError("working_local_path boş")

        write_path_text(working_path, str(content or ""))
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
    Session içindeki son uygun yedeği geri yükler.

    Öncelik:
    1) session.last_backup_path
    2) fallback yedek klasörlerinde en güncel uygun yedek
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

    try:
        session.last_backup_path = str(backup_path)
    except Exception:
        pass

    return str(backup_path)
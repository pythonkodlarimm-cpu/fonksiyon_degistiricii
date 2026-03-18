# -*- coding: utf-8 -*-
"""
DOSYA: app/services/belge_ice_aktarma_servisi.py

ROL:
- Seçilen belgeyi uygulama içine aktarmak
- Android document URI veya filesystem kaynağından içeriği okumak
- İçeriği uygulamanın çalışma kopyasına yazmak
- Sonuçta bir DocumentSession üretmek

MİMARİ:
- Girdi: DocumentSelection
- Kaynağa göre içerik okunur
- Uygulama içinde çalışma kopyası oluşturulur
- Çıktı: DocumentSession

API UYUMLULUK DEĞERLENDİRMESİ:
- Bu servis SAF (Storage Access Framework) temelli Android belge akışına uygundur
- Android tarafında content:// URI kullanımı sayesinde modern Android sürümleriyle uyumludur
- Bu düzenlenmiş sürüm özellikle API 34 hedeflenerek güvenli hale getirilmiştir
- Genel uyumluluk hedefi: API 30+ / özellikle API 34

SURUM: 3
TARIH: 2026-03-17
IMZA: FY.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from kivy.utils import platform

from app.services.android_uri_servisi import (
    AndroidUriServisiHatasi,
    get_app_cache_dir,
    get_display_name as get_uri_display_name,
    read_text as read_text_from_uri,
)
from app.services.dosya_servisi import (
    DosyaServisiHatasi,
    get_app_working_root,
    get_display_name as get_path_display_name,
    read_text as read_text_from_path,
    write_text,
)
from app.ui.dosya_secici_paketi.models import DocumentSelection, DocumentSession


class BelgeIceAktarmaServisiHatasi(ValueError):
    """Belge içe aktarma işlemleri sırasında oluşan kontrollü hata."""


def _normalize_name(name: str) -> str:
    """
    Dosya adını güvenli hale getirir.

    API 34 uyumluluk notu:
    - Çalışma kopyası dosya adı yerel dosya sistemi için normalize edilir.
    """
    temiz = str(name or "").strip() or "belge.txt"
    for ch in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
        temiz = temiz.replace(ch, "_")
    return temiz or "belge.txt"


def _working_root() -> Path:
    """
    Çalışma kopyalarının yazılacağı kök dizini döndürür.

    Android:
    - uygulama cache alanı / working_imports

    Android dışı:
    - uygulamanın normal çalışma kökü

    API 34 uyumluluk notu:
    - Android tarafında uygulama sandbox/cache alanı kullanılır.
    """
    try:
        if platform == "android":
            root = get_app_cache_dir() / "working_imports"
            root.mkdir(parents=True, exist_ok=True)
            return root

        root = get_app_working_root()
        root.mkdir(parents=True, exist_ok=True)
        return root
    except Exception as exc:
        raise BelgeIceAktarmaServisiHatasi(
            f"Çalışma kök dizini oluşturulamadı: {exc}"
        ) from exc


def _working_copy_name(display_name: str) -> str:
    """
    Çalışma kopyası için benzersiz dosya adı üretir.

    API 34 uyumluluk notu:
    - Aynı ada sahip belgelerin çakışmaması için zaman damgası kullanılır.
    """
    zaman = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{zaman}_{_normalize_name(display_name)}"


def _resolve_display_name(selection: DocumentSelection) -> str:
    """
    Belge için gösterim adını belirler.

    Öncelik:
    1) selection.preferred_display_name()
    2) URI display name
    3) Path display name
    4) fallback: belge.txt

    API 34 uyumluluk notu:
    - SAF URI kaynaklarında display_name resolver üzerinden okunur.
    """
    if selection is None:
        return "belge.txt"

    try:
        name = str(selection.preferred_display_name() or "").strip()
        if name:
            return name
    except Exception:
        pass

    try:
        if selection.has_uri():
            name = str(
                get_uri_display_name(str(getattr(selection, "uri", "") or "").strip()) or ""
            ).strip()
            if name:
                return name
    except Exception:
        pass

    try:
        if selection.has_local_path():
            name = str(
                get_path_display_name(
                    str(getattr(selection, "local_path", "") or "").strip()
                ) or ""
            ).strip()
            if name:
                return name
    except Exception:
        pass

    return "belge.txt"


def _build_working_target(display_name: str) -> Path:
    """
    Çalışma kopyasının yazılacağı hedef path'i üretir.
    """
    try:
        return _working_root() / _working_copy_name(display_name)
    except Exception as exc:
        raise BelgeIceAktarmaServisiHatasi(
            f"Çalışma dosyası hedefi üretilemedi: {exc}"
        ) from exc


def _create_session(selection: DocumentSelection, target: Path) -> DocumentSession:
    """
    Selection içinden DocumentSession üretir.
    """
    try:
        return DocumentSession.from_selection(
            selection,
            working_local_path=str(target),
        )
    except Exception as exc:
        raise BelgeIceAktarmaServisiHatasi(
            f"Belge oturumu oluşturulamadı: {exc}"
        ) from exc


def _write_working_copy(target: Path, content: str) -> None:
    """
    Çalışma kopyasına içerik yazar.
    """
    try:
        write_text(target, content)
    except DosyaServisiHatasi as exc:
        raise BelgeIceAktarmaServisiHatasi(
            f"Çalışma kopyası oluşturulamadı: {exc}"
        ) from exc
    except Exception as exc:
        raise BelgeIceAktarmaServisiHatasi(
            f"Çalışma dosyası oluşturulamadı: {exc}"
        ) from exc


def _import_from_android_document(selection: DocumentSelection) -> DocumentSession:
    """
    Android content/document URI kaynağından belgeyi içe aktarır.

    İş akışı:
    - URI doğrulanır
    - içerik URI üzerinden okunur
    - uygulama içi çalışma kopyasına yazılır
    - session oluşturulur

    API 34 uyumluluk notu:
    - SAF/content URI okuma akışı korunur
    - doğrudan path erişimi kullanılmaz
    """
    uri = str(getattr(selection, "uri", "") or "").strip()
    if not uri:
        raise BelgeIceAktarmaServisiHatasi("Android belge URI boş.")

    display_name = _resolve_display_name(selection)
    target = _build_working_target(display_name)

    try:
        content = read_text_from_uri(uri)
    except AndroidUriServisiHatasi as exc:
        raise BelgeIceAktarmaServisiHatasi(
            f"Android belge okunamadı: {exc}"
        ) from exc
    except Exception as exc:
        raise BelgeIceAktarmaServisiHatasi(
            f"Android belge alınamadı: {exc}"
        ) from exc

    _write_working_copy(target, content)
    return _create_session(selection, target)


def _import_from_filesystem(selection: DocumentSelection) -> DocumentSession:
    """
    Yerel dosya sistemi kaynağından belgeyi içe aktarır.

    İş akışı:
    - path doğrulanır
    - içerik path üzerinden okunur
    - çalışma kopyasına yazılır
    - session oluşturulur

    API 34 uyumluluk notu:
    - Android dışı veya yerel path tabanlı kaynaklar için kullanılır.
    """
    source_path = str(getattr(selection, "local_path", "") or "").strip()
    if not source_path:
        raise BelgeIceAktarmaServisiHatasi("Filesystem belge yolu boş.")

    display_name = _resolve_display_name(selection)
    target = _build_working_target(display_name)

    try:
        content = read_text_from_path(source_path)
    except DosyaServisiHatasi as exc:
        raise BelgeIceAktarmaServisiHatasi(
            f"Yerel belge okunamadı: {exc}"
        ) from exc
    except Exception as exc:
        raise BelgeIceAktarmaServisiHatasi(
            f"Yerel belge alınamadı: {exc}"
        ) from exc

    _write_working_copy(target, content)
    return _create_session(selection, target)


def belgeyi_ice_aktar(selection: DocumentSelection) -> DocumentSession:
    """
    Seçilen belgeyi uygulama içine aktarır ve bir DocumentSession döndürür.

    Desteklenen kaynaklar:
    - Android document/content URI
    - Filesystem path

    API 34 uyumluluk notu:
    - Android belge seçimi SAF temelli ise URI akışı kullanılır
    - modern Android davranışına uygun olarak çalışma kopyası yerel alanda tutulur
    """
    if selection is None:
        raise BelgeIceAktarmaServisiHatasi("Belge seçimi boş.")

    try:
        if selection.is_android_document():
            return _import_from_android_document(selection)

        if selection.is_filesystem():
            return _import_from_filesystem(selection)
    except BelgeIceAktarmaServisiHatasi:
        raise
    except Exception as exc:
        raise BelgeIceAktarmaServisiHatasi(
            f"Belge içe aktarma işlemi başarısız: {exc}"
        ) from exc

    raise BelgeIceAktarmaServisiHatasi(
        f"Desteklenmeyen belge kaynağı: {getattr(selection, 'source', '')}"
    )
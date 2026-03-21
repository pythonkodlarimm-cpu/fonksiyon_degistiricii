# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/models.py

ROL:
- Belge seçimi ve belge oturumu için sade veri modelleri sağlamak
- Android document URI ve filesystem seçimlerini tek tip yapıda taşımak
- UI ve servis katmanları arasında güvenli veri sözleşmesi oluşturmak

MİMARİ:
- Saf model katmanıdır
- Doğrudan Android API çağrısı yapmaz
- Picker, belge ve root akışları tarafından ortak kullanılır
- Veri temizleme ve kaynak doğrulama model içinde merkezileştirilmiştir

API UYUMLULUK:
- Android SAF akışında content:// URI kaynakları açıkça ayrı tutulur
- Filesystem path ve Android document URI aynı anda karıştırılmaz
- API 35 uyumlu veri normalizasyonu içerir

SURUM: 2
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from dataclasses import dataclass


def _clean(value: str) -> str:
    try:
        return str(value or "").strip()
    except Exception:
        return ""


def _name_from_path(value: str) -> str:
    try:
        temiz = _clean(value).replace("\\", "/")
        if not temiz:
            return ""
        return temiz.rsplit("/", 1)[-1]
    except Exception:
        return ""


def _name_from_uri(value: str) -> str:
    try:
        temiz = _clean(value)
        if not temiz:
            return ""
        return temiz.rsplit("/", 1)[-1]
    except Exception:
        return ""


def _is_content_uri(value: str) -> bool:
    return _clean(value).startswith("content://")


@dataclass(slots=True)
class DocumentSelection:
    source: str = ""
    uri: str = ""
    local_path: str = ""
    display_name: str = ""
    mime_type: str = ""

    def normalized_source(self) -> str:
        return _clean(self.source)

    def has_uri(self) -> bool:
        return bool(_clean(self.uri))

    def has_local_path(self) -> bool:
        return bool(_clean(self.local_path))

    def preferred_identifier(self) -> str:
        if self.has_uri():
            return _clean(self.uri)
        return _clean(self.local_path)

    def preferred_display_name(self) -> str:
        temiz_ad = _clean(self.display_name)
        if temiz_ad:
            return temiz_ad

        if self.has_local_path():
            ad = _name_from_path(self.local_path)
            if ad:
                return ad

        if self.has_uri():
            ad = _name_from_uri(self.uri)
            if ad:
                return ad

        return ""

    def is_android_document(self) -> bool:
        if self.normalized_source() == "android_document":
            return self.has_uri() and _is_content_uri(self.uri)
        return False

    def is_filesystem(self) -> bool:
        if self.normalized_source() == "filesystem":
            path = _clean(self.local_path)
            return bool(path) and not _is_content_uri(path)
        return False

    def is_valid(self) -> bool:
        if self.is_android_document():
            return True
        if self.is_filesystem():
            return True
        return False


@dataclass(slots=True)
class DocumentSession:
    source: str = ""
    source_uri: str = ""
    source_path: str = ""
    working_local_path: str = ""
    display_name: str = ""
    mime_type: str = ""
    last_backup_path: str = ""

    def normalized_source(self) -> str:
        return _clean(self.source)

    def has_source_uri(self) -> bool:
        return bool(_clean(self.source_uri))

    def has_source_path(self) -> bool:
        return bool(_clean(self.source_path))

    def has_working_local_path(self) -> bool:
        return bool(_clean(self.working_local_path))

    def has_backup_path(self) -> bool:
        return bool(_clean(self.last_backup_path))

    def preferred_source_identifier(self) -> str:
        if self.has_source_uri():
            return _clean(self.source_uri)
        return _clean(self.source_path)

    def preferred_display_name(self) -> str:
        temiz_ad = _clean(self.display_name)
        if temiz_ad:
            return temiz_ad

        if self.has_source_path():
            ad = _name_from_path(self.source_path)
            if ad:
                return ad

        if self.has_source_uri():
            ad = _name_from_uri(self.source_uri)
            if ad:
                return ad

        if self.has_working_local_path():
            ad = _name_from_path(self.working_local_path)
            if ad:
                return ad

        return ""

    def is_android_document(self) -> bool:
        return (
            self.normalized_source() == "android_document"
            and self.has_source_uri()
            and _is_content_uri(self.source_uri)
        )

    def is_filesystem(self) -> bool:
        path = _clean(self.source_path)
        return (
            self.normalized_source() == "filesystem"
            and bool(path)
            and not _is_content_uri(path)
        )

    def is_valid(self) -> bool:
        if not self.has_working_local_path():
            return False

        if self.is_android_document():
            return True

        if self.is_filesystem():
            return True

        return False

    @classmethod
    def from_selection(
        cls,
        selection: DocumentSelection,
        working_local_path: str = "",
    ) -> "DocumentSession":
        source = _clean(getattr(selection, "source", ""))
        uri = _clean(getattr(selection, "uri", ""))
        local_path = _clean(getattr(selection, "local_path", ""))
        display_name = _clean(getattr(selection, "display_name", ""))
        mime_type = _clean(getattr(selection, "mime_type", ""))
        working_path = _clean(working_local_path)

        if source == "android_document":
            return cls(
                source=source,
                source_uri=uri,
                source_path="",
                working_local_path=working_path,
                display_name=display_name,
                mime_type=mime_type,
                last_backup_path="",
            )

        if source == "filesystem":
            return cls(
                source=source,
                source_uri="",
                source_path=local_path,
                working_local_path=working_path,
                display_name=display_name,
                mime_type=mime_type,
                last_backup_path="",
            )

        return cls(
            source=source,
            source_uri="",
            source_path="",
            working_local_path=working_path,
            display_name=display_name,
            mime_type=mime_type,
            last_backup_path="",
        )
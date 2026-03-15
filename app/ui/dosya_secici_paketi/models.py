# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DocumentSelection:
    source: str = ""
    uri: str = ""
    local_path: str = ""
    display_name: str = ""
    mime_type: str = ""

    def has_uri(self) -> bool:
        return bool(str(self.uri or "").strip())

    def has_local_path(self) -> bool:
        return bool(str(self.local_path or "").strip())

    def preferred_identifier(self) -> str:
        if self.has_uri():
            return str(self.uri).strip()
        return str(self.local_path or "").strip()

    def preferred_display_name(self) -> str:
        if str(self.display_name or "").strip():
            return str(self.display_name).strip()

        if self.has_local_path():
            try:
                return str(self.local_path).replace("\\", "/").rsplit("/", 1)[-1]
            except Exception:
                pass

        if self.has_uri():
            try:
                return str(self.uri).rsplit("/", 1)[-1]
            except Exception:
                pass

        return ""

    def is_android_document(self) -> bool:
        return str(self.source or "").strip() == "android_document"

    def is_filesystem(self) -> bool:
        return str(self.source or "").strip() == "filesystem"


@dataclass
class DocumentSession:
    source: str = ""
    source_uri: str = ""
    source_path: str = ""
    working_local_path: str = ""
    display_name: str = ""
    mime_type: str = ""
    last_backup_path: str = ""

    def has_source_uri(self) -> bool:
        return bool(str(self.source_uri or "").strip())

    def has_source_path(self) -> bool:
        return bool(str(self.source_path or "").strip())

    def has_working_local_path(self) -> bool:
        return bool(str(self.working_local_path or "").strip())

    def preferred_source_identifier(self) -> str:
        if self.has_source_uri():
            return str(self.source_uri).strip()
        return str(self.source_path or "").strip()

    def preferred_display_name(self) -> str:
        if str(self.display_name or "").strip():
            return str(self.display_name).strip()

        if self.has_source_path():
            try:
                return str(self.source_path).replace("\\", "/").rsplit("/", 1)[-1]
            except Exception:
                pass

        if self.has_source_uri():
            try:
                return str(self.source_uri).rsplit("/", 1)[-1]
            except Exception:
                pass

        if self.has_working_local_path():
            try:
                return str(self.working_local_path).replace("\\", "/").rsplit("/", 1)[-1]
            except Exception:
                pass

        return ""

    @classmethod
    def from_selection(
        cls,
        selection: DocumentSelection,
        working_local_path: str = "",
    ) -> "DocumentSession":
        source = str(getattr(selection, "source", "") or "").strip()
        uri = str(getattr(selection, "uri", "") or "").strip()
        local_path = str(getattr(selection, "local_path", "") or "").strip()
        display_name = str(getattr(selection, "display_name", "") or "").strip()
        mime_type = str(getattr(selection, "mime_type", "") or "").strip()

        return cls(
            source=source,
            source_uri=uri if source == "android_document" else "",
            source_path=local_path if source == "filesystem" else "",
            working_local_path=str(working_local_path or "").strip(),
            display_name=display_name,
            mime_type=mime_type,
            last_backup_path="",
        )
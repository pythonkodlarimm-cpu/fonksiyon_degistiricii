# -*- coding: utf-8 -*-
"""
DOSYA: app/core/modeller/modeller.py

ROL:
- Fonksiyon tarama ve değiştirme sisteminin çekirdek veri modeli
- FunctionItem → sistemin kimlik (identity) katmanı

MİMARİ:
- Immutable (frozen + slots)
- Type güvenli (strict typing)
- Lazy cache (identity / hesaplanan alanlar)
- Canonical veri normalizasyonu
- Deterministik davranış (replace güvenliği)

KRİTİK:
- Yanlış identity = yanlış fonksiyon değiştirme
- Bu sınıf sistemin en hassas bileşenidir

SURUM: 7
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


# =========================================================
# SABITLER (TYPE SAFE)
# =========================================================
_ALLOWED_KINDS: Final[frozenset[str]] = frozenset({
    "function",
    "method",
    "nested",
    "async_function",
    "async_method",
    "async_nested",
})


# =========================================================
# NORMALIZE
# =========================================================
def _norm_text(v: object) -> str:
    s = str(v or "")
    return s.replace("\r\n", "\n").replace("\r", "\n")


def _norm_single(v: object) -> str:
    return " ".join(_norm_text(v).strip().split())


def _norm_path(v: object) -> str:
    parts = [p.strip() for p in _norm_text(v).split(".") if p.strip()]
    return ".".join(parts)


def _to_int(v: object, name: str) -> int:
    try:
        return int(v)
    except Exception as e:
        raise ValueError(f"{name} int olmalı") from e


# =========================================================
# MODEL
# =========================================================
@dataclass(frozen=True, slots=True)
class FunctionItem:
    path: str
    name: str
    kind: str
    lineno: int
    end_lineno: int
    col_offset: int
    end_col_offset: int
    signature: str
    source: str

    # lazy cache alanları (internal)
    _identity_cache: tuple[str, int, str] | None = None
    _parent_cache: str | None = None

    # =========================================================
    # INIT
    # =========================================================
    def __post_init__(self) -> None:
        path = _norm_path(self.path)
        name = _norm_single(self.name)
        kind = self._norm_kind(self.kind)
        signature = _norm_single(self.signature)
        source = _norm_text(self.source)

        lineno = _to_int(self.lineno, "lineno")
        end_lineno = _to_int(self.end_lineno, "end_lineno")
        col = _to_int(self.col_offset, "col_offset")
        end_col = _to_int(self.end_col_offset, "end_col_offset")

        # ---------------- VALIDATION ----------------
        if not path:
            raise ValueError("FunctionItem.path boş")

        if not name:
            raise ValueError("FunctionItem.name boş")

        if kind not in _ALLOWED_KINDS:
            raise ValueError(f"FunctionItem.kind geçersiz: {kind}")

        if lineno < 1:
            raise ValueError("lineno >= 1 olmalı")

        if end_lineno < lineno:
            raise ValueError("end_lineno >= lineno olmalı")

        if col < 0 or end_col < 0:
            raise ValueError("col_offset >= 0 olmalı")

        if not signature:
            signature = name

        # ---------------- SET ----------------
        object.__setattr__(self, "path", path)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "lineno", lineno)
        object.__setattr__(self, "end_lineno", end_lineno)
        object.__setattr__(self, "col_offset", col)
        object.__setattr__(self, "end_col_offset", end_col)
        object.__setattr__(self, "signature", signature)
        object.__setattr__(self, "source", source)

        # cache başlangıç
        object.__setattr__(self, "_identity_cache", None)
        object.__setattr__(self, "_parent_cache", None)

    # =========================================================
    # KIND NORMALIZE
    # =========================================================
    @staticmethod
    def _norm_kind(v: str) -> str:
        raw = _norm_single(v).lower()

        MAP = {
            "def": "function",
            "func": "function",

            "method": "method",
            "metot": "method",

            "nested": "nested",
            "inner": "nested",

            "async": "async_function",
            "async def": "async_function",

            "async_method": "async_method",
            "async method": "async_method",

            "async_nested": "async_nested",
            "async inner": "async_nested",
        }

        return MAP.get(raw, raw)

    # =========================================================
    # IDENTITY (LAZY CACHE)
    # =========================================================
    def identity(self) -> tuple[str, int, str]:
        cache = self._identity_cache
        if cache is not None:
            return cache

        value = (self.path, self.lineno, self.kind)
        object.__setattr__(self, "_identity_cache", value)
        return value

    def __hash__(self) -> int:
        return hash(self.identity())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FunctionItem):
            return False
        return self.identity() == other.identity()

    # =========================================================
    # LAZY PROPERTY
    # =========================================================
    @property
    def parent_path(self) -> str:
        cache = self._parent_cache
        if cache is not None:
            return cache

        if "." not in self.path:
            value = ""
        else:
            value = self.path.rsplit(".", 1)[0]

        object.__setattr__(self, "_parent_cache", value)
        return value

    # =========================================================
    # DERIVED
    # =========================================================
    @property
    def satir_araligi(self) -> tuple[int, int]:
        return (self.lineno, self.end_lineno)

    @property
    def satir_sayisi(self) -> int:
        return self.end_lineno - self.lineno + 1

    @property
    def tam_kimlik(self) -> str:
        return f"{self.path} [{self.kind}] ({self.lineno}-{self.end_lineno})"

    # =========================================================
    # FLAGS
    # =========================================================
    def is_async(self) -> bool:
        return self.kind.startswith("async")

    def is_method(self) -> bool:
        return "method" in self.kind

    def is_nested(self) -> bool:
        return "nested" in self.kind

    def is_top_level(self) -> bool:
        return self.kind in {"function", "async_function"}

    # =========================================================
    # MATCH (STRICT)
    # =========================================================
    def matches_identity(
        self,
        *,
        path: str | None = None,
        name: str | None = None,
        lineno: int | None = None,
        kind: str | None = None,
    ) -> bool:

        if path is not None and _norm_path(path) != self.path:
            return False

        if name is not None and _norm_single(name) != self.name:
            return False

        if lineno is not None:
            try:
                if int(lineno) != self.lineno:
                    return False
            except Exception:
                return False

        if kind is not None and self._norm_kind(kind) != self.kind:
            return False

        return True

    # =========================================================
    # SERIALIZE
    # =========================================================
    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "name": self.name,
            "kind": self.kind,
            "lineno": self.lineno,
            "end_lineno": self.end_lineno,
            "col_offset": self.col_offset,
            "end_col_offset": self.end_col_offset,
            "signature": self.signature,
            "source": self.source,
        }
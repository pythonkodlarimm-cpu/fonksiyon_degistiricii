# -*- coding: utf-8 -*-
"""
DOSYA: app/core/modeller.py

ROL:
- Fonksiyon değiştirici çekirdeğinde kullanılan veri modelleri
- Tarama sonucu bulunan fonksiyon/metot bilgisini standartlaştırır
- İleride değişiklik isteği ve sonuç modeli ile genişlemeye uygundur

NOT:
- FunctionItem immutable (frozen) tutulur
- Kurulum anında temel doğrulamalar yapılır
- kind alanı normalize edilir
- Satır/sütun sınırları güvenceye alınır

SURUM: 4
TARIH: 2026-03-14
IMZA: FY.
"""

from __future__ import annotations

from dataclasses import dataclass


_ALLOWED_KINDS = {
    "function",
    "method",
    "nested",
    "async_function",
    "async_method",
    "async_nested",
}


def _normalize_text(value) -> str:
    s = str(value or "")
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return s


def _normalize_single_line(value) -> str:
    s = _normalize_text(value).strip()
    return " ".join(s.split())


@dataclass(frozen=True, slots=True)
class FunctionItem:
    """
    Dosya içinden taranmış fonksiyon/metot bilgisini taşır.

    Alanlar:
    - path: dotted path / tam kimlik
      Örnek:
        metin_temizle
        Kisi.tam_ad
        detayli_isle._temizle_satir
        MiniCache.set._trim
    - name: sadece düğüm adı
      Örnek:
        tam_ad
        _trim
    - kind:
        function / method / nested / async_function / async_method / async_nested
    - lineno: başlangıç satırı (1 tabanlı)
    - end_lineno: bitiş satırı (1 tabanlı, dahil)
    - col_offset: başlangıç sütunu
    - end_col_offset: bitiş sütunu
    - signature: def satırı / imza özeti
    - source: fonksiyonun ham kaynak kodu
    """

    path: str
    name: str
    kind: str
    lineno: int
    end_lineno: int
    col_offset: int
    end_col_offset: int
    signature: str
    source: str

    def __post_init__(self) -> None:
        path = _normalize_text(self.path).strip()
        name = _normalize_single_line(self.name)
        kind = self._normalize_kind(self.kind)
        signature = _normalize_single_line(self.signature)
        source = _normalize_text(self.source)

        lineno = self._to_int(self.lineno, field_name="lineno")
        end_lineno = self._to_int(self.end_lineno, field_name="end_lineno")
        col_offset = self._to_int(self.col_offset, field_name="col_offset")
        end_col_offset = self._to_int(self.end_col_offset, field_name="end_col_offset")

        if not path:
            raise ValueError("FunctionItem.path boş olamaz.")

        if not name:
            raise ValueError("FunctionItem.name boş olamaz.")

        if kind not in _ALLOWED_KINDS:
            raise ValueError(
                "FunctionItem.kind geçersiz. "
                f"Beklenen: {sorted(_ALLOWED_KINDS)} | Gelen: {self.kind!r}"
            )

        if lineno < 1:
            raise ValueError("FunctionItem.lineno 1 veya daha büyük int olmalıdır.")

        if end_lineno < lineno:
            raise ValueError("FunctionItem.end_lineno, lineno'dan küçük olamaz.")

        if col_offset < 0:
            raise ValueError("FunctionItem.col_offset 0 veya daha büyük int olmalıdır.")

        if end_col_offset < 0:
            raise ValueError("FunctionItem.end_col_offset 0 veya daha büyük int olmalıdır.")

        if not signature:
            signature = name

        object.__setattr__(self, "path", path)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "lineno", lineno)
        object.__setattr__(self, "end_lineno", end_lineno)
        object.__setattr__(self, "col_offset", col_offset)
        object.__setattr__(self, "end_col_offset", end_col_offset)
        object.__setattr__(self, "signature", signature)
        object.__setattr__(self, "source", source)

    @staticmethod
    def _to_int(value, field_name: str) -> int:
        try:
            return int(value)
        except Exception as exc:
            raise ValueError(f"FunctionItem.{field_name} int olmalıdır.") from exc

    @staticmethod
    def _normalize_kind(value: str) -> str:
        raw = _normalize_single_line(value).lower()

        eslemeler = {
            "func": "function",
            "function": "function",
            "def": "function",

            "method": "method",
            "metot": "method",

            "nested": "nested",
            "nested_function": "nested",
            "nested function": "nested",
            "inner_function": "nested",
            "inner function": "nested",
            "inner": "nested",

            "async": "async_function",
            "async_function": "async_function",
            "async function": "async_function",
            "async def": "async_function",

            "async_method": "async_method",
            "async method": "async_method",
            "async metot": "async_method",

            "async_nested": "async_nested",
            "async nested": "async_nested",
            "async nested function": "async_nested",
            "async_inner": "async_nested",
            "async inner": "async_nested",
        }

        return eslemeler.get(raw, raw)

    @property
    def satir_araligi(self) -> tuple[int, int]:
        """(başlangıç, bitiş) satır aralığını döndürür."""
        return (self.lineno, self.end_lineno)

    @property
    def satir_sayisi(self) -> int:
        """Fonksiyonun kapladığı toplam satır sayısı."""
        return self.end_lineno - self.lineno + 1

    @property
    def tam_kimlik(self) -> str:
        """Log ve listelerde kullanılabilecek kısa kimlik."""
        return f"{self.path} [{self.kind}] ({self.lineno}-{self.end_lineno})"

    @property
    def kisa_imza(self) -> str:
        """Liste ve kısa gösterimler için özet imza."""
        return self.signature or self.name

    @property
    def parent_path(self) -> str:
        """
        Path'in parent kısmını döndürür.
        Örnek:
        - 'Kisi.tam_ad' -> 'Kisi'
        - 'MiniCache.set._trim' -> 'MiniCache.set'
        - 'metin_temizle' -> ''
        """
        if "." not in self.path:
            return ""
        return self.path.rsplit(".", 1)[0]

    def is_async(self) -> bool:
        return self.kind.startswith("async")

    def is_method(self) -> bool:
        return "method" in self.kind

    def is_nested(self) -> bool:
        return "nested" in self.kind

    def is_top_level(self) -> bool:
        return self.kind in {"function", "async_function"}

    def matches_identity(
        self,
        *,
        path: str | None = None,
        name: str | None = None,
        lineno: int | None = None,
        kind: str | None = None,
    ) -> bool:
        if path is not None and _normalize_text(path).strip() != self.path:
            return False

        if name is not None and _normalize_single_line(name) != self.name:
            return False

        if lineno is not None:
            try:
                if int(lineno) != self.lineno:
                    return False
            except Exception:
                return False

        if kind is not None and self._normalize_kind(kind) != self.kind:
            return False

        return True

    def to_dict(self) -> dict:
        """UI / json / log için sözlük çıktısı üretir."""
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
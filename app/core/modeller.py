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

SURUM: 2
"""

from __future__ import annotations

from dataclasses import dataclass


_ALLOWED_KINDS = {
    "function",
    "method",
    "async_function",
    "async_method",
}


@dataclass(frozen=True, slots=True)
class FunctionItem:
    """
    Dosya içinden taranmış fonksiyon/metot bilgisini taşır.

    Alanlar:
    - path: dosya yolu
    - name: fonksiyon/metot adı
    - kind: function / method / async_function / async_method
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
        path = str(self.path or "").strip()
        name = str(self.name or "").strip()
        kind = self._normalize_kind(self.kind)
        signature = str(self.signature or "").strip()
        source = str(self.source or "")

        if not path:
            raise ValueError("FunctionItem.path boş olamaz.")

        if not name:
            raise ValueError("FunctionItem.name boş olamaz.")

        if kind not in _ALLOWED_KINDS:
            raise ValueError(
                "FunctionItem.kind geçersiz. "
                f"Beklenen: {sorted(_ALLOWED_KINDS)} | Gelen: {self.kind!r}"
            )

        if not isinstance(self.lineno, int) or self.lineno < 1:
            raise ValueError("FunctionItem.lineno 1 veya daha büyük int olmalıdır.")

        if not isinstance(self.end_lineno, int) or self.end_lineno < self.lineno:
            raise ValueError("FunctionItem.end_lineno, lineno'dan küçük olamaz.")

        if not isinstance(self.col_offset, int) or self.col_offset < 0:
            raise ValueError("FunctionItem.col_offset 0 veya daha büyük int olmalıdır.")

        if not isinstance(self.end_col_offset, int) or self.end_col_offset < 0:
            raise ValueError("FunctionItem.end_col_offset 0 veya daha büyük int olmalıdır.")

        if not signature:
            signature = name

        object.__setattr__(self, "path", path)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "signature", signature)
        object.__setattr__(self, "source", source)

    @staticmethod
    def _normalize_kind(value: str) -> str:
        raw = str(value or "").strip().lower()

        eslemeler = {
            "func": "function",
            "function": "function",
            "def": "function",
            "method": "method",
            "metot": "method",
            "async": "async_function",
            "async_function": "async_function",
            "async def": "async_function",
            "async_method": "async_method",
            "async metot": "async_method",
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
        return f"{self.name} [{self.kind}] ({self.lineno}-{self.end_lineno})"

    def is_async(self) -> bool:
        return self.kind.startswith("async")

    def is_method(self) -> bool:
        return "method" in self.kind

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
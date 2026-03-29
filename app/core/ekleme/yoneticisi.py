# -*- coding: utf-8 -*-
"""
DOSYA: app/core/ekleme/yoneticisi.py

ROL:
- Fonksiyon ekleme motoruna facade sağlar
- Üst katmanların ekleyici modül detaylarını bilmesini engeller
- Bellek içi ve dosya üstü insert işlemlerini merkezileştirir

MİMARİ:
- Lazy load + strict cache
- Module değil fonksiyon ve sınıf referansı cache edilir
- Type-safe forwarding
- Deterministik ve sıfır belirsizlik
- Geriye uyumluluk katmanı içermez

BAĞIMLILIKLAR:
- app/core/ekleme/ekleyici.py
- app/core/modeller/modeller.py

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Pydroid3 / masaüstü / test ortamlarında aynı davranır

SURUM: 3
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Type

if TYPE_CHECKING:
    from app.core.modeller.modeller import FunctionItem


class EklemeYoneticisi:
    """
    Fonksiyon ekleme facade katmanı.
    """

    __slots__ = (
        "_insert_fn",
        "_insert_file_fn",
        "_error_cls",
    )

    def __init__(self) -> None:
        self._insert_fn: Callable[..., str] | None = None
        self._insert_file_fn: Callable[..., str] | None = None
        self._error_cls: Type[Exception] | None = None

    # =========================================================
    # INTERNAL (LAZY + STRICT CACHE)
    # =========================================================
    def _load(self) -> None:
        if (
            self._insert_fn is not None
            and self._insert_file_fn is not None
            and self._error_cls is not None
        ):
            return

        from app.core.ekleme.ekleyici import (
            FunctionInsertError,
            insert_function,
            insert_function_in_file,
        )

        self._insert_fn = insert_function
        self._insert_file_fn = insert_function_in_file
        self._error_cls = FunctionInsertError

    def _insert(self) -> Callable[..., str]:
        if self._insert_fn is None:
            self._load()
        return self._insert_fn  # type: ignore[return-value]

    def _insert_file(self) -> Callable[..., str]:
        if self._insert_file_fn is None:
            self._load()
        return self._insert_file_fn  # type: ignore[return-value]

    def _error(self) -> Type[Exception]:
        if self._error_cls is None:
            self._load()
        return self._error_cls  # type: ignore[return-value]

    # =========================================================
    # ERROR
    # =========================================================
    def function_insert_error_sinifi(self) -> Type[Exception]:
        """
        Ekleme motorunun hata sınıfını döndürür.
        """
        return self._error()

    # =========================================================
    # INSERT (MEMORY)
    # =========================================================
    def insert_function(
        self,
        source_code: str,
        target_item: FunctionItem | None,
        new_code: str,
        *,
        mode: str,
    ) -> str:
        """
        Bellek içindeki kaynak koda yeni fonksiyon ekler.

        mode:
        - after
        - before
        - inside_class
        - end_of_file
        """
        return self._insert()(
            source_code=source_code,
            target=target_item,
            new_code=new_code,
            mode=mode,
        )

    # =========================================================
    # INSERT (FILE)
    # =========================================================
    def insert_function_in_file(
        self,
        file_path: str,
        target_item: FunctionItem | None,
        new_code: str,
        *,
        mode: str,
        backup: bool = True,
        encoding: str = "utf-8",
    ) -> str:
        """
        Dosya içindeki kaynak koda yeni fonksiyon ekler.

        mode:
        - after
        - before
        - inside_class
        - end_of_file
        """
        return self._insert_file()(
            file_path=file_path,
            target=target_item,
            new_code=new_code,
            mode=mode,
            backup=backup,
            encoding=encoding,
        )
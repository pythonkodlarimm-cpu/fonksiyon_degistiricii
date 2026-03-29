# -*- coding: utf-8 -*-
"""
DOSYA: app/core/enjeksiyon/yoneticisi.py

ROL:
- Enjeksiyon motoruna tek ve kontrollü erişim sağlar
- inject_code ve inject_code_in_file fonksiyonlarını kapsüller
- Üst katmanın enjeksiyon modül detaylarını bilmesini engeller

MİMARİ:
- Lazy load (ilk kullanımda import)
- Kesin cache (fonksiyon ve sınıf referansları)
- Type güvenli (strict callable imzaları)
- Deterministik davranış
- Geriye uyumluluk katmanı içermez

AVANTAJ:
- Import maliyeti minimum
- Attribute lookup maliyeti düşük
- Net API
- Sıfır fallback / sürpriz davranış
- Alt yöneticiler tekrar tekrar oluşturulmaz

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Pydroid3 / masaüstü / test ortamlarında aynı davranır

SURUM: 4
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Protocol, Type

from app.core.modeller.modeller import FunctionItem


# =========================================================
# STRICT TYPES
# =========================================================
class _InjectFn(Protocol):
    def __call__(
        self,
        source_code: str,
        target: FunctionItem,
        inject_code: str,
        *,
        mode: str,
    ) -> str: ...


class _InjectFileFn(Protocol):
    def __call__(
        self,
        file_path: str,
        target: FunctionItem,
        inject_code_str: str,
        *,
        mode: str,
        backup: bool = True,
        encoding: str = "utf-8",
    ) -> str: ...


# =========================================================
# MANAGER
# =========================================================
class EnjeksiyonYoneticisi:
    """
    Enjeksiyon motoru erişim yöneticisi.
    """

    __slots__ = (
        "_inject_fn",
        "_inject_file_fn",
        "_error_cls",
    )

    def __init__(self) -> None:
        self._inject_fn: _InjectFn | None = None
        self._inject_file_fn: _InjectFileFn | None = None
        self._error_cls: Type[Exception] | None = None

    # =========================================================
    # INTERNAL (LAZY + STRICT CACHE)
    # =========================================================
    def _load(self) -> None:
        inject_fn = self._inject_fn
        inject_file_fn = self._inject_file_fn
        error_cls = self._error_cls

        if (
            inject_fn is not None
            and inject_file_fn is not None
            and error_cls is not None
        ):
            return

        from app.core.enjeksiyon.enjeksiyon import (
            FunctionInjectError,
            inject_code,
            inject_code_in_file,
        )

        self._inject_fn = inject_code
        self._inject_file_fn = inject_code_in_file
        self._error_cls = FunctionInjectError

    def _injector(self) -> _InjectFn:
        inject_fn = self._inject_fn
        if inject_fn is None:
            self._load()
            inject_fn = self._inject_fn

        return inject_fn  # type: ignore[return-value]

    def _injector_file(self) -> _InjectFileFn:
        inject_file_fn = self._inject_file_fn
        if inject_file_fn is None:
            self._load()
            inject_file_fn = self._inject_file_fn

        return inject_file_fn  # type: ignore[return-value]

    def _error(self) -> Type[Exception]:
        error_cls = self._error_cls
        if error_cls is None:
            self._load()
            error_cls = self._error_cls

        return error_cls  # type: ignore[return-value]

    # =========================================================
    # PUBLIC API
    # =========================================================
    def inject_error_sinifi(self) -> Type[Exception]:
        """
        Enjeksiyon motorunun hata sınıfını döndürür.
        """
        return self._error()

    def inject(
        self,
        *,
        source_code: str,
        target_item: FunctionItem,
        code: str,
        mode: str,
    ) -> str:
        """
        Hedef fonksiyon içine bellekte kod enjekte eder.

        Args:
            source_code: Kaynak Python kodu
            target_item: Hedef FunctionItem
            code: Enjekte edilecek kod
            mode: Enjeksiyon modu

        Returns:
            Güncellenmiş kaynak kod
        """
        injector = self._injector()

        return injector(
            source_code=source_code,
            target=target_item,
            inject_code=code,
            mode=mode,
        )

    def inject_in_file(
        self,
        *,
        file_path: str,
        target_item: FunctionItem,
        code: str,
        mode: str,
        backup: bool = True,
        encoding: str = "utf-8",
    ) -> str:
        """
        Hedef fonksiyon içine dosya üzerinde kod enjekte eder.

        Args:
            file_path: Hedef dosya yolu
            target_item: Hedef FunctionItem
            code: Enjekte edilecek kod
            mode: Enjeksiyon modu
            backup: Önce yedek alınsın mı
            encoding: Dosya encoding değeri

        Returns:
            Güncellenmiş kaynak kod
        """
        injector_file = self._injector_file()

        return injector_file(
            file_path=file_path,
            target=target_item,
            inject_code_str=code,
            mode=mode,
            backup=backup,
            encoding=encoding,
        )
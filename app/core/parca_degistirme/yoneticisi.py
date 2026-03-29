# -*- coding: utf-8 -*-
"""
DOSYA: app/core/parca_degistirme/yoneticisi.py

ROL:
- Parça değiştirme motoruna facade sağlar
- Üst katmanların degistirici modül detaylarını bilmesini engeller
- Bellek içi ve dosya üstü parça değiştirme işlemlerini merkezileştirir

MİMARİ:
- Lazy load + strict cache
- Module yerine fonksiyon ve sınıf referansı cache edilir
- Net API sunar
- Deterministik davranır
- Mode doğrulaması facade seviyesinde de yapılır
- Geriye uyumluluk katmanı içermez

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Pydroid3 / masaüstü / test ortamlarında aynı davranır

SURUM: 3
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Callable, Type


class ParcaDegistirmeYoneticisi:
    """
    Parça değiştirme motoru facade katmanı.
    """

    __slots__ = (
        "_replace_code_fn",
        "_replace_file_fn",
        "_error_cls",
        "_allowed_modes",
    )

    def __init__(self) -> None:
        self._replace_code_fn: Callable[..., tuple[str, int]] | None = None
        self._replace_file_fn: Callable[..., tuple[str, int]] | None = None
        self._error_cls: Type[Exception] | None = None
        self._allowed_modes: frozenset[str] | None = None

    # =========================================================
    # INTERNAL (LAZY + STRICT CACHE)
    # =========================================================
    def _load(self) -> None:
        replace_code_fn = self._replace_code_fn
        replace_file_fn = self._replace_file_fn
        error_cls = self._error_cls
        allowed_modes = self._allowed_modes

        if (
            replace_code_fn is not None
            and replace_file_fn is not None
            and error_cls is not None
            and allowed_modes is not None
        ):
            return

        from app.core.parca_degistirme.degistirici import (
            ALLOWED_MODES,
            ParcaDegistirmeHatasi,
            replace_piece_in_code,
            replace_piece_in_file,
        )

        self._replace_code_fn = replace_piece_in_code
        self._replace_file_fn = replace_piece_in_file
        self._error_cls = ParcaDegistirmeHatasi
        self._allowed_modes = ALLOWED_MODES

    def _replace_code(self) -> Callable[..., tuple[str, int]]:
        replace_code_fn = self._replace_code_fn
        if replace_code_fn is None:
            self._load()
            replace_code_fn = self._replace_code_fn

        return replace_code_fn  # type: ignore[return-value]

    def _replace_file(self) -> Callable[..., tuple[str, int]]:
        replace_file_fn = self._replace_file_fn
        if replace_file_fn is None:
            self._load()
            replace_file_fn = self._replace_file_fn

        return replace_file_fn  # type: ignore[return-value]

    def _error(self) -> Type[Exception]:
        error_cls = self._error_cls
        if error_cls is None:
            self._load()
            error_cls = self._error_cls

        return error_cls  # type: ignore[return-value]

    def _modes(self) -> frozenset[str]:
        allowed_modes = self._allowed_modes
        if allowed_modes is None:
            self._load()
            allowed_modes = self._allowed_modes

        return allowed_modes  # type: ignore[return-value]

    def _validate_mode(self, mode: str) -> str:
        normalized = str(mode or "").strip().lower()
        allowed_modes = self._modes()

        if normalized not in allowed_modes:
            raise self._error()(
                f"Geçersiz mode: {mode!r}. "
                f"Desteklenen modlar: {sorted(allowed_modes)}"
            )

        return normalized

    # =========================================================
    # PUBLIC API
    # =========================================================
    def parca_degistirme_hatasi_sinifi(self) -> Type[Exception]:
        """
        Parça değiştirme motorunun hata sınıfını döndürür.
        """
        return self._error()

    def replace_piece_in_code(
        self,
        source_code: str,
        old_piece: str,
        new_piece: str,
        *,
        mode: str = "first",
        expected_count: int = 1,
        strict_python: bool = True,
    ) -> tuple[str, int]:
        """
        Bellek içindeki kaynak kodda parça değiştirme yapar.
        """
        normalized_mode = self._validate_mode(mode)

        return self._replace_code()(
            source_code=source_code,
            old_piece=old_piece,
            new_piece=new_piece,
            mode=normalized_mode,
            expected_count=expected_count,
            strict_python=strict_python,
        )

    def replace_piece_in_file(
        self,
        file_path: str,
        old_piece: str,
        new_piece: str,
        *,
        mode: str = "first",
        expected_count: int = 1,
        strict_python: bool = True,
        encoding: str = "utf-8",
        make_backup: bool = True,
    ) -> tuple[str, int]:
        """
        Dosya üstünde parça değiştirme yapar.
        """
        normalized_mode = self._validate_mode(mode)

        return self._replace_file()(
            file_path=file_path,
            old_piece=old_piece,
            new_piece=new_piece,
            mode=normalized_mode,
            expected_count=expected_count,
            strict_python=strict_python,
            encoding=encoding,
            make_backup=make_backup,
        )
# -*- coding: utf-8 -*-
"""
DOSYA: app/core/degistirme/yoneticisi.py

ROL:
- Değiştirme çekirdeğine facade sağlar
- Üst katmanların degistirici modül detaylarını bilmesini engeller
- Bellek içi ve dosya üstü fonksiyon değiştirme işlemlerini merkezileştirir
- Yeni fonksiyon kodu doğrulama akışını da dış katmana sunar

MİMARİ:
- Lazy load + strict module cache
- Net ve deterministik API
- Type güvenliği yüksek
- Geriye uyumluluk katmanı içermez
- Alt yöneticiler tekrar tekrar oluşturulmaz
- Gereksiz fallback içermez
- Micro-perf odaklıdır

BAĞIMLILIKLAR:
- app/core/degistirme/degistirici.py
- app/core/modeller/modeller.py

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Pydroid3 / masaüstü / test ortamlarında aynı davranır

SURUM: 6
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from types import ModuleType
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.core.degistirme.degistirici import FunctionCodeValidationResult
    from app.core.modeller.modeller import FunctionItem


class DegistirmeYoneticisi:
    """
    Değiştirme çekirdeği facade katmanı.
    """

    __slots__ = ("_modul_cache",)

    def __init__(self) -> None:
        self._modul_cache: ModuleType | None = None

    # =========================================================
    # INTERNAL
    # =========================================================
    def _modul(self) -> ModuleType:
        """
        Degistirici modülünü lazy load eder ve cache'ler.
        """
        modul = self._modul_cache
        if modul is None:
            from app.core.degistirme import degistirici as degistirici_modulu

            modul = degistirici_modulu
            self._modul_cache = modul

        return modul

    # =========================================================
    # ERROR
    # =========================================================
    def function_replace_error_sinifi(self) -> type[Exception]:
        """
        Değiştirme motorunun hata sınıfını döndürür.
        """
        return self._modul().FunctionReplaceError

    # =========================================================
    # VALIDATION
    # =========================================================
    def validate_single_top_level_function_code(
        self,
        source_code: str,
        *,
        expected_name: str | None = None,
        allow_async: bool = True,
        allow_other_top_level_nodes: bool = False,
    ) -> FunctionCodeValidationResult:
        """
        Kodun modül seviyesinde tam olarak bir fonksiyon içerip içermediğini doğrular.

        Not:
        - Nested fonksiyonlar serbesttir
        - Top-level düzeyde tam 1 fonksiyon aranır
        - İstenirse beklenen fonksiyon adı doğrulanır
        """
        return self._modul().validate_single_top_level_function_code(
            source_code=source_code,
            expected_name=expected_name,
            allow_async=allow_async,
            allow_other_top_level_nodes=allow_other_top_level_nodes,
        )

    # =========================================================
    # CODE UPDATE
    # =========================================================
    def update_function_in_code(
        self,
        source_code: str,
        target_item: FunctionItem,
        new_code: str,
    ) -> str:
        """
        Bellek içindeki kaynak kodda hedef fonksiyonu değiştirir.
        """
        return self._modul().update_function_in_code(
            source_code=source_code,
            target_item=target_item,
            new_code=new_code,
        )

    # =========================================================
    # FILE UPDATE
    # =========================================================
    def update_function_in_file(
        self,
        file_path: str,
        target_item: FunctionItem,
        new_code: str,
        *,
        backup: bool,
    ) -> str:
        """
        Dosya içindeki hedef fonksiyonu değiştirir.
        """
        return self._modul().update_function_in_file(
            file_path=file_path,
            target_item=target_item,
            new_code=new_code,
            backup=backup,
        )

    # =========================================================
    # RANGE
    # =========================================================
    def resolve_range(
        self,
        source_code: str,
        target_item: FunctionItem,
    ) -> tuple[int, int]:
        """
        Hedef fonksiyonun kaynak içindeki satır aralığını çözer.
        """
        return self._modul()._resolve_range(
            source=source_code,
            target=target_item,
        )

    # =========================================================
    # MATCH
    # =========================================================
    def find_item_by_identity(
        self,
        items: list[FunctionItem],
        *,
        path: str,
        name: str,
        lineno: int,
        kind: str,
    ) -> FunctionItem | None:
        """
        FunctionItem listesi içinde kimlik bazlı tam eşleşme bulur.
        """
        for item in items:
            if item.path != path:
                continue
            if item.name != name:
                continue
            if item.lineno != lineno:
                continue
            if item.kind != kind:
                continue
            return item

        return None
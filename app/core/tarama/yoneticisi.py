# -*- coding: utf-8 -*-
"""
DOSYA: app/core/tarama/yoneticisi.py

ROL:
- Tarama çekirdeğine tek giriş noktası sağlar
- Kod ve dosya tarama işlemlerini merkezileştirir
- Yeni fonksiyon kodu için top-level doğrulama akışını sunar
- Üst katmanın app/core/tarama/tarayici.py detaylarını bilmesini engeller
- Tarama hata sınıfını kontrollü biçimde dış katmana sunar

MİMARİ:
- Lazy import + kesin modül cache kullanır
- İlk erişimden sonra modülü tek kez çözümler
- Üst katman yalnızca bu yöneticiyi kullanır
- Public API yalnızca tarama / doğrulama işlemleriyle sınırlıdır
- Runtime import yükünü azaltmak için tip importları TYPE_CHECKING ile ayrılmıştır
- Geriye uyumluluk katmanı içermez
- Deterministik ve type-safe API sunar

BAĞIMLILIKLAR:
- app/core/tarama/tarayici.py
- app/core/modeller/modeller.py

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Saf Python çalışır
- APK / AAB paketlerinde güvenli çalışır

SURUM: 4
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.core.modeller import FunctionItem


class TaramaYoneticisi:
    """
    Tarama çekirdeği erişim yöneticisi.
    """

    __slots__ = ("_modul_cache",)

    def __init__(self) -> None:
        self._modul_cache: ModuleType | None = None

    # =========================================================
    # INTERNAL
    # =========================================================
    def _modul(self) -> ModuleType:
        """
        Tarayıcı modülünü lazy load eder ve cache'ler.
        """
        modul = self._modul_cache
        if modul is None:
            from app.core.tarama import tarayici as tarayici_modulu

            modul = tarayici_modulu
            self._modul_cache = modul

        return modul

    # =========================================================
    # ERROR
    # =========================================================
    def function_scan_error_sinifi(self) -> type[Exception]:
        """
        Tarama hata sınıfını döndürür.
        """
        return self._modul().FunctionScanError

    # =========================================================
    # PUBLIC API / TARAMA
    # =========================================================
    def scan_functions_from_code(
        self,
        source_code: str,
        file_path: str = "<memory>",
    ) -> list[FunctionItem]:
        """
        Bellekteki kaynak koddan fonksiyonları tarar.
        """
        return self._modul().scan_functions_from_code(
            source_code=source_code,
            file_path=file_path,
        )

    def scan_functions_from_file(
        self,
        file_path: str | Path,
    ) -> list[FunctionItem]:
        """
        Dosya yolundan fonksiyonları tarar.
        """
        return self._modul().scan_functions_from_file(
            file_path=file_path,
        )

    # =========================================================
    # PUBLIC API / VALIDATION
    # =========================================================
    def validate_single_top_level_function_code(
        self,
        source_code: str,
        *,
        expected_name: str | None = None,
        allow_async: bool = True,
        allow_other_top_level_nodes: bool = False,
    ) -> dict[str, Any]:
        """
        Kodun modül seviyesinde tam olarak bir fonksiyon içerip içermediğini doğrular.

        Not:
        - Nested fonksiyonlar serbesttir
        - Yalnızca top-level fonksiyon sayısı kontrol edilir
        - İstenirse beklenen fonksiyon adı da doğrulanır
        """
        return self._modul().validate_single_top_level_function_code(
            source_code=source_code,
            expected_name=expected_name,
            allow_async=allow_async,
            allow_other_top_level_nodes=allow_other_top_level_nodes,
        )
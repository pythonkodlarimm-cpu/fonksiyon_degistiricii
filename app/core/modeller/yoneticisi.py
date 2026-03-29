# -*- coding: utf-8 -*-
"""
DOSYA: app/core/modeller/yoneticisi.py

ROL:
- Model katmanına tek giriş noktası sağlar
- FunctionItem ve ileride eklenecek modelleri merkezileştirir
- Üst katmanın modeller.py detaylarını bilmesini engeller

MİMARİ:
- Lazy import kullanır
- İlk erişimde modül yüklenir, sonra cache kullanılır
- Core ve UI yalnızca bu yöneticiyi kullanır

BAĞIMLILIKLAR:
- app/core/modeller/modeller.py

SURUM: 2
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations

from types import ModuleType


class ModellerYoneticisi:
    """
    Model katmanı erişim yöneticisi.
    """

    def __init__(self) -> None:
        self._modul_cache: ModuleType | None = None

    # =========================================================
    # INTERNAL
    # =========================================================
    def _modul(self) -> ModuleType:
        """
        modeller modülünü lazy load eder ve cache'ler.
        """
        if self._modul_cache is None:
            from app.core.modeller import modeller
            self._modul_cache = modeller

        return self._modul_cache

    # =========================================================
    # PUBLIC API
    # =========================================================
    def function_item_sinifi(self):
        """
        FunctionItem sınıfını döndürür.
        """
        return self._modul().FunctionItem
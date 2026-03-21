# -*- coding: utf-8 -*-
"""
DOSYA: app/core/tarama/yoneticisi.py

ROL:
- Tarama çekirdeğine tek giriş noktası sağlamak
- Kod ve dosya tarama işlemlerini merkezileştirmek
- Üst katmanın tarayici.py detaylarını bilmesini engellemek

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations


class TaramaYoneticisi:
    def _modul(self):
        from app.core.tarama import tarayici
        return tarayici

    def function_scan_error_sinifi(self):
        return self._modul().FunctionScanError

    def scan_functions_from_code(
        self,
        source_code: str,
        file_path: str = "<memory>",
    ):
        return self._modul().scan_functions_from_code(
            source_code=source_code,
            file_path=file_path,
        )

    def scan_functions_from_file(self, file_path):
        return self._modul().scan_functions_from_file(file_path=file_path)
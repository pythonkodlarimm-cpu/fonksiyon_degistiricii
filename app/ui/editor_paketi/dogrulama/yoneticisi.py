# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/dogrulama/yoneticisi.py

ROL:
- Doğrulama alt paketine tek giriş noktası sağlamak
- Editör doğrulama akışını merkezileştirmek
- Üst katmanın doğrulama modülü detaylarını bilmesini engellemek

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt doğrulama modülü doğrudan dışarı açılmaz
- Kod normalize etme, parse kontrolü ve hata satırı çıkarımı burada toplanır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations


class DogrulamaYoneticisi:
    def _modul(self):
        from app.ui.editor_paketi.dogrulama.editor_dogrulama import (
            basic_parse_check,
            extract_line_number,
            first_meaningful_line,
            looks_like_full_function,
            normalize_code_text,
            validate_new_code,
        )

        return {
            "normalize_code_text": normalize_code_text,
            "first_meaningful_line": first_meaningful_line,
            "looks_like_full_function": looks_like_full_function,
            "basic_parse_check": basic_parse_check,
            "extract_line_number": extract_line_number,
            "validate_new_code": validate_new_code,
        }

    def normalize_code_text(self, text, trim_outer_blank_lines=False) -> str:
        return self._modul()["normalize_code_text"](
            text,
            trim_outer_blank_lines=trim_outer_blank_lines,
        )

    def first_meaningful_line(self, text: str) -> str:
        return self._modul()["first_meaningful_line"](text)

    def looks_like_full_function(self, text: str) -> bool:
        return self._modul()["looks_like_full_function"](text)

    def basic_parse_check(self, text: str) -> None:
        return self._modul()["basic_parse_check"](text)

    def extract_line_number(self, exc) -> int:
        return self._modul()["extract_line_number"](exc)

    def validate_new_code(self, text: str) -> tuple[bool, str, int]:
        return self._modul()["validate_new_code"](text)
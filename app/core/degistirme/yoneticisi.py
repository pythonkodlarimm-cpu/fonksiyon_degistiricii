# -*- coding: utf-8 -*-
"""
DOSYA: app/core/degistirme/yoneticisi.py

ROL:
- Değiştirme çekirdeğine tek giriş noktası sağlamak
- Güncelleme ve hedef bulma işlemlerini merkezileştirmek
- Üst katmanın degistirici.py detaylarını bilmesini engellemek

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations


class DegistirmeYoneticisi:
    def _modul(self):
        from app.core.degistirme import degistirici
        return degistirici

    def function_replace_error_sinifi(self):
        return self._modul().FunctionReplaceError

    def update_function_in_code(
        self,
        source_code: str,
        target_item,
        new_code: str,
        *,
        replace_mode: str = "full",
    ) -> str:
        return self._modul().update_function_in_code(
            source_code=source_code,
            target_item=target_item,
            new_code=new_code,
            replace_mode=replace_mode,
        )

    def update_function_in_file(
        self,
        file_path: str,
        target_item,
        new_code: str,
        *,
        encoding: str = "utf-8",
        make_backup: bool = True,
        replace_mode: str = "full",
    ) -> str:
        return self._modul().update_function_in_file(
            file_path=file_path,
            target_item=target_item,
            new_code=new_code,
            encoding=encoding,
            make_backup=make_backup,
            replace_mode=replace_mode,
        )

    def find_item_by_identity(
        self,
        items,
        *,
        path: str,
        name: str,
        lineno: int,
        kind: str | None = None,
    ):
        return self._modul().find_item_by_identity(
            items=items,
            path=path,
            name=name,
            lineno=lineno,
            kind=kind,
        )
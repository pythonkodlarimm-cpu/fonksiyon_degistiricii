# -*- coding: utf-8 -*-
"""
DOSYA: app/core/yoneticisi.py

ROL:
- Core katmanı için tek giriş noktası sağlamak
- Değiştirme, tarama, modeller ve metadata erişimini merkezileştirmek
- Üst katmanın alt modül detaylarını bilmesini engellemek

MİMARİ:
- Alt paket yöneticilerine lazy import ile erişir
- UI ve servis katmanı doğrudan alt modüllere değil, bu yöneticiye bağlanır
- Refactor sırasında import kırılmalarını azaltır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations


class CoreYoneticisi:
    # =========================================================
    # ALT YONETICILER
    # =========================================================
    def _degistirme_yoneticisi(self):
        from app.core.degistirme import DegistirmeYoneticisi
        return DegistirmeYoneticisi()

    def _tarama_yoneticisi(self):
        from app.core.tarama import TaramaYoneticisi
        return TaramaYoneticisi()

    def _modeller_yoneticisi(self):
        from app.core.modeller import ModellerYoneticisi
        return ModellerYoneticisi()

    def _meta_yoneticisi(self):
        from app.core.meta import MetaYoneticisi
        return MetaYoneticisi()

    # =========================================================
    # DEGISTIRME
    # =========================================================
    def function_replace_error_sinifi(self):
        return self._degistirme_yoneticisi().function_replace_error_sinifi()

    def update_function_in_code(
        self,
        source_code: str,
        target_item,
        new_code: str,
        *,
        replace_mode: str = "full",
    ) -> str:
        return self._degistirme_yoneticisi().update_function_in_code(
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
        return self._degistirme_yoneticisi().update_function_in_file(
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
        return self._degistirme_yoneticisi().find_item_by_identity(
            items=items,
            path=path,
            name=name,
            lineno=lineno,
            kind=kind,
        )

    # =========================================================
    # TARAMA
    # =========================================================
    def function_scan_error_sinifi(self):
        return self._tarama_yoneticisi().function_scan_error_sinifi()

    def scan_functions_from_code(
        self,
        source_code: str,
        file_path: str = "<memory>",
    ):
        return self._tarama_yoneticisi().scan_functions_from_code(
            source_code=source_code,
            file_path=file_path,
        )

    def scan_functions_from_file(self, file_path):
        return self._tarama_yoneticisi().scan_functions_from_file(
            file_path=file_path,
        )

    # =========================================================
    # MODELLER
    # =========================================================
    def function_item_sinifi(self):
        return self._modeller_yoneticisi().function_item_sinifi()

    # =========================================================
    # META
    # =========================================================
    def uygulama_adi(self) -> str:
        return self._meta_yoneticisi().uygulama_adi()

    def paket_adi(self) -> str:
        return self._meta_yoneticisi().paket_adi()

    def surum(self) -> str:
        return self._meta_yoneticisi().surum()

    def build(self) -> int:
        return self._meta_yoneticisi().build()

    def tarih(self) -> str:
        return self._meta_yoneticisi().tarih()

    def imza(self) -> str:
        return self._meta_yoneticisi().imza()

    def aciklama(self) -> str:
        return self._meta_yoneticisi().aciklama()

    def tam_surum(self) -> str:
        return self._meta_yoneticisi().tam_surum()

    def apk_surum_kodu(self) -> int:
        return self._meta_yoneticisi().apk_surum_kodu()

    def apk_surum_adi(self) -> str:
        return self._meta_yoneticisi().apk_surum_adi()

    def uygulama_etiketi(self) -> str:
        return self._meta_yoneticisi().uygulama_etiketi()

    def meta_bilgisi(self) -> dict:
        return self._meta_yoneticisi().meta_bilgisi()
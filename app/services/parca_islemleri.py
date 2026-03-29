# -*- coding: utf-8 -*-
"""
DOSYA: app/services/parca_islemleri.py

ROL:
- Parça değiştirme işlemlerini servis katmanında birleştirir
- UI için sade ve tek noktalı API sunar
- Kod ve dosya bazlı replace akışlarını merkezileştirir
- Dosya erişimini (path + Android URI) birleşik erişim servisi üzerinden yönetir

MİMARİ:
- Thin service layer
- IO sorumluluğu burada tutulur
- Core sadece pure logic çalıştırır
- Deterministik davranır
- URI / path ayrımı tamamen izole edilmiştir
- Yedekleme hataları sessizce yutulmaz
- Geriye uyumluluk katmanı içermez

API UYUMLULUK:
- Platform bağımsızdır
- Android SAF (content://) uyumludur
- Android API 35 ile uyumludur
- Pydroid3 / masaüstü / test ortamlarında aynı mantıkla davranır

SURUM: 3
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from app.core import CoreYoneticisi
from app.services.dosya_erisim_servisi import DosyaErisimServisi
from app.services.sil_yada_geri_yukle import SilYadaGeriYukleServisi


class ParcaIslemleriServisi:
    """
    Parça değiştirme servis katmanı.
    """

    __slots__ = ("_core", "_yedek", "_dosya")

    def __init__(self) -> None:
        self._core = CoreYoneticisi()
        self._yedek = SilYadaGeriYukleServisi()
        self._dosya = DosyaErisimServisi()

    # =========================================================
    # CODE BASED
    # =========================================================
    def kodda_parca_degistir(
        self,
        *,
        source_code: str,
        old_piece: str,
        new_piece: str,
        mode: str = "first",
        expected_count: int = 1,
        strict_python: bool = True,
    ) -> tuple[str, int]:
        return self._core.replace_piece_in_code(
            source_code=source_code,
            old_piece=old_piece,
            new_piece=new_piece,
            mode=mode,
            expected_count=expected_count,
            strict_python=strict_python,
        )

    # =========================================================
    # FILE BASED
    # =========================================================
    def dosyada_parca_degistir(
        self,
        *,
        file_path: str,
        old_piece: str,
        new_piece: str,
        mode: str = "first",
        expected_count: int = 1,
        strict_python: bool = True,
        encoding: str = "utf-8",
        make_backup: bool = True,
    ) -> tuple[str, int]:
        """
        Path + Android URI uyumlu parça değiştirme akışı.
        """
        source_code = self._dosya.metin_oku(
            file_path,
            encoding=encoding,
        )

        updated_code, replaced_count = self._core.replace_piece_in_code(
            source_code=source_code,
            old_piece=old_piece,
            new_piece=new_piece,
            mode=mode,
            expected_count=expected_count,
            strict_python=strict_python,
        )

        if make_backup:
            self._yedek.yedek_olustur(
                motor_adi="parca_degistirme",
                hedef_dosya=file_path,
                icerik=source_code,
                encoding=encoding,
            )

        self._dosya.metin_yaz(
            file_path,
            updated_code,
            encoding=encoding,
        )

        return updated_code, replaced_count

    # =========================================================
    # GERI AL
    # =========================================================
    def son_islemi_geri_al(self, *, hedef_dosya: str) -> bool:
        return self._yedek.son_yedegi_geri_yukle(
            motor_adi="parca_degistirme",
            hedef_dosya=hedef_dosya,
        )
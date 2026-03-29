# -*- coding: utf-8 -*-
"""
DOSYA: app/services/enjeksiyon_islemleri.py

ROL:
- Enjeksiyon işlemlerini servis katmanında birleştirir
- UI için sade ve tek noktalı API sunar
- Tarama + hedef bulma + enjeksiyon akışını merkezileştirir
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


class EnjeksiyonIslemleriServisi:
    """
    Enjeksiyon servis katmanı.
    """

    __slots__ = ("_core", "_yedek", "_dosya")

    def __init__(self) -> None:
        self._core = CoreYoneticisi()
        self._yedek = SilYadaGeriYukleServisi()
        self._dosya = DosyaErisimServisi()

    # =========================================================
    # TARAMA
    # =========================================================
    def dosyadan_fonksiyonlari_tara(self, file_path: str):
        """
        Path veya Android URI üzerinden dosyayı okuyup tarar.
        """
        source_code = self._dosya.metin_oku(file_path)

        return self._core.scan_functions_from_code(
            source_code=source_code,
            file_path=file_path,
        )

    def koddan_fonksiyonlari_tara(
        self,
        source_code: str,
        file_path: str = "<memory>",
    ):
        return self._core.scan_functions_from_code(
            source_code=source_code,
            file_path=file_path,
        )

    # =========================================================
    # BULMA
    # =========================================================
    def kimlikle_fonksiyon_bul(
        self,
        *,
        items,
        path: str,
        name: str,
        lineno: int,
        kind: str,
    ):
        return self._core.find_item_by_identity(
            items=items,
            path=path,
            name=name,
            lineno=lineno,
            kind=kind,
        )

    # =========================================================
    # CODE BASED
    # =========================================================
    def kodda_enjeksiyon_yap(
        self,
        *,
        source_code: str,
        target_item,
        code: str,
        mode: str,
    ) -> str:
        return self._core.inject_code(
            source_code=source_code,
            target_item=target_item,
            code=code,
            mode=mode,
        )

    # =========================================================
    # FILE BASED
    # =========================================================
    def dosyada_enjeksiyon_yap(
        self,
        *,
        file_path: str,
        target_item,
        code: str,
        mode: str,
        backup: bool = True,
        encoding: str = "utf-8",
    ) -> str:
        """
        Path + Android URI uyumlu enjeksiyon akışı.
        """
        source_code = self._dosya.metin_oku(
            file_path,
            encoding=encoding,
        )

        updated_code = self._core.inject_code(
            source_code=source_code,
            target_item=target_item,
            code=code,
            mode=mode,
        )

        if backup:
            self._yedek.yedek_olustur(
                motor_adi="enjeksiyon",
                hedef_dosya=file_path,
                icerik=source_code,
                encoding=encoding,
            )

        self._dosya.metin_yaz(
            file_path,
            updated_code,
            encoding=encoding,
        )

        return updated_code

    # =========================================================
    # GERI AL
    # =========================================================
    def son_islemi_geri_al(self, *, hedef_dosya: str) -> bool:
        return self._yedek.son_yedegi_geri_yukle(
            motor_adi="enjeksiyon",
            hedef_dosya=hedef_dosya,
        )
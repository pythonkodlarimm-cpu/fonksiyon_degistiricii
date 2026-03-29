# -*- coding: utf-8 -*-
"""
DOSYA: app/services/fonksiyon_islemleri.py

ROL:
- Fonksiyon tarama ve değiştirme akışlarını servis katmanında birleştirir
- UI için sade ve tek noktalı API sunar
- Dosya erişimini (path + Android URI) merkezi servis üzerinden yönetir
- Core doğrulama akışını dış katmana güvenli biçimde sunar

MİMARİ:
- Thin service layer
- IO sorumluluğu burada tutulur
- Core sadece pure logic çalıştırır (string bazlı)
- Deterministik davranır
- URI / path ayrımı tamamen izole edilmiştir
- Yedekleme hataları sessizce yutulmaz
- Geriye uyumluluk katmanı içermez
- Type-safe ve net API yüzeyi sunar

API UYUMLULUK:
- Platform bağımsız
- Android SAF (content://) uyumlu
- Android API 35 uyumlu
- Pydroid3 / masaüstü / test ortamlarında aynı mantıkla çalışır

SURUM: 5
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core import CoreYoneticisi
from app.services.dosya_erisim_servisi import DosyaErisimServisi
from app.services.sil_yada_geri_yukle import SilYadaGeriYukleServisi

if TYPE_CHECKING:
    from app.core.degistirme.degistirici import FunctionCodeValidationResult
    from app.core.modeller.modeller import FunctionItem


class FonksiyonIslemleriServisi:
    """
    Fonksiyon tarama ve değiştirme servis katmanı.
    """

    __slots__ = (
        "_core",
        "_yedek",
        "_dosya",
    )

    def __init__(
        self,
        core: CoreYoneticisi | None = None,
        yedek: SilYadaGeriYukleServisi | None = None,
        dosya: DosyaErisimServisi | None = None,
    ) -> None:
        self._core: CoreYoneticisi = core if core is not None else CoreYoneticisi()
        self._yedek: SilYadaGeriYukleServisi = (
            yedek if yedek is not None else SilYadaGeriYukleServisi()
        )
        self._dosya: DosyaErisimServisi = (
            dosya if dosya is not None else DosyaErisimServisi()
        )

    # =========================================================
    # PROPERTIES
    # =========================================================
    @property
    def core(self) -> CoreYoneticisi:
        """
        Aktif core yöneticisini döndürür.
        """
        return self._core

    @property
    def yedek(self) -> SilYadaGeriYukleServisi:
        """
        Aktif yedek servis örneğini döndürür.
        """
        return self._yedek

    @property
    def dosya(self) -> DosyaErisimServisi:
        """
        Aktif dosya erişim servis örneğini döndürür.
        """
        return self._dosya

    # =========================================================
    # TARAMA
    # =========================================================
    def dosyadan_fonksiyonlari_tara(self, file_path: str) -> list[FunctionItem]:
        """
        Path veya Android URI üzerinden dosyayı okuyup fonksiyonları tarar.
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
    ) -> list[FunctionItem]:
        """
        Bellekteki kod metni üzerinden fonksiyonları tarar.
        """
        return self._core.scan_functions_from_code(
            source_code=source_code,
            file_path=file_path,
        )

    # =========================================================
    # VALIDATION
    # =========================================================
    def yeni_fonksiyon_kodunu_dogrula(
        self,
        *,
        source_code: str,
        beklenen_fonksiyon_adi: str | None = None,
        allow_async: bool = True,
        allow_other_top_level_nodes: bool = False,
    ) -> FunctionCodeValidationResult:
        """
        Yeni kodun modül seviyesinde tam olarak bir fonksiyon içerip içermediğini doğrular.

        Not:
        - Nested fonksiyonlar serbesttir
        - Doğrulama mantığı core katmanındadır
        - Service yalnızca facade görevi görür
        """
        return self._core.validate_single_top_level_function_code(
            source_code=source_code,
            expected_name=beklenen_fonksiyon_adi,
            allow_async=allow_async,
            allow_other_top_level_nodes=allow_other_top_level_nodes,
        )

    # =========================================================
    # BULMA
    # =========================================================
    def kimlikle_fonksiyon_bul(
        self,
        *,
        items: list[FunctionItem],
        path: str,
        name: str,
        lineno: int,
        kind: str,
    ) -> FunctionItem | None:
        """
        Taranmış item listesi içinde kimlik bilgilerine göre fonksiyon bulur.
        """
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
    def kodda_fonksiyon_degistir(
        self,
        *,
        source_code: str,
        target_item: FunctionItem,
        new_code: str,
    ) -> str:
        """
        Bellekteki kaynak kod içinde hedef fonksiyonu değiştirir.
        """
        return self._core.update_function_in_code(
            source_code=source_code,
            target_item=target_item,
            new_code=new_code,
        )

    # =========================================================
    # FILE BASED
    # =========================================================
    def dosyada_fonksiyon_degistir(
        self,
        *,
        file_path: str,
        target_item: FunctionItem,
        new_code: str,
        backup: bool = True,
    ) -> str:
        """
        Path veya Android URI hedefinde fonksiyon değiştirme akışını çalıştırır.

        Akış:
        1. Dosya içeriğini oku
        2. Core ile yeni içeriği üret
        3. Gerekirse mevcut içeriğin yedeğini al
        4. Yeni içeriği hedefe yaz
        5. Güncellenmiş kodu döndür
        """
        source_code = self._dosya.metin_oku(file_path)

        updated_code = self._core.update_function_in_code(
            source_code=source_code,
            target_item=target_item,
            new_code=new_code,
        )

        if backup:
            self._yedek.yedek_olustur(
                motor_adi="degistirme",
                hedef_dosya=file_path,
                icerik=source_code,
            )

        self._dosya.metin_yaz(file_path, updated_code)
        return updated_code

    # =========================================================
    # GERI AL
    # =========================================================
    def son_islemi_geri_al(self, *, hedef_dosya: str) -> bool:
        """
        İlgili hedef dosya için son yedeği geri yükler.
        """
        return self._yedek.son_yedegi_geri_yukle(
            motor_adi="degistirme",
            hedef_dosya=hedef_dosya,
        )
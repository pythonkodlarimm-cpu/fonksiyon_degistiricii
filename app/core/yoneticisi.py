# -*- coding: utf-8 -*-
"""
DOSYA: app/core/yoneticisi.py

ROL:
- Core katmanı için tek giriş noktası sağlar
- Tüm alt yöneticileri merkezileştirir (facade)
- Bellek içi ve dosya üstü çekirdek işlemlerini tek API altında toplar
- Dil geliştirici yöneticisini de merkezi API'ye ekler

MİMARİ:
- Lazy load + kesin instance cache
- Alt yöneticiler yalnızca 1 kez oluşturulur
- Deterministik API
- Type güvenliği yüksek
- Geriye uyumluluk katmanı içermez
- Her motor kendi uzmanlık alanında ayrı tutulur
- Dış katman alt modül detaylarını bilmez
- Micro-perf optimize

ALT KATMANLAR:
- degistirme
- tarama
- modeller
- meta
- ekleme
- enjeksiyon
- parca_degistirme
- yedekleme
- dil
- dil_ekle

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Saf Python çalışır
- Pydroid3 / masaüstü / test ortamlarında aynı mantıkla davranır

SURUM: 15
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

    from app.core.degistirme.degistirici import FunctionCodeValidationResult
    from app.core.degistirme.yoneticisi import DegistirmeYoneticisi
    from app.core.dil.yoneticisi import DilYoneticisi
    from app.core.dil_ekle.yoneticisi import DilGelistiriciYonetici
    from app.core.ekleme.yoneticisi import EklemeYoneticisi
    from app.core.enjeksiyon.yoneticisi import EnjeksiyonYoneticisi
    from app.core.meta.yoneticisi import MetaYoneticisi
    from app.core.modeller.modeller import FunctionItem
    from app.core.modeller.yoneticisi import ModellerYoneticisi
    from app.core.parca_degistirme.yoneticisi import ParcaDegistirmeYoneticisi
    from app.core.tarama.yoneticisi import TaramaYoneticisi
    from app.core.yedekleme.yoneticisi import YedeklemeYoneticisi


class CoreYoneticisi:
    """
    Core facade yöneticisi.
    """

    __slots__ = (
        "_degistirme",
        "_tarama",
        "_modeller",
        "_meta",
        "_ekleme",
        "_enjeksiyon",
        "_parca_degistirme",
        "_yedekleme",
        "_dil",
        "_dil_ekle",
    )

    def __init__(self) -> None:
        self._degistirme: DegistirmeYoneticisi | None = None
        self._tarama: TaramaYoneticisi | None = None
        self._modeller: ModellerYoneticisi | None = None
        self._meta: MetaYoneticisi | None = None
        self._ekleme: EklemeYoneticisi | None = None
        self._enjeksiyon: EnjeksiyonYoneticisi | None = None
        self._parca_degistirme: ParcaDegistirmeYoneticisi | None = None
        self._yedekleme: YedeklemeYoneticisi | None = None
        self._dil: DilYoneticisi | None = None
        self._dil_ekle: DilGelistiriciYonetici | None = None

    # =========================================================
    # INTERNAL (LAZY + STRICT CACHE)
    # =========================================================
    def _degistirme_yoneticisi(self) -> DegistirmeYoneticisi:
        obj = self._degistirme
        if obj is None:
            from app.core.degistirme import DegistirmeYoneticisi

            obj = DegistirmeYoneticisi()
            self._degistirme = obj
        return obj

    def _tarama_yoneticisi(self) -> TaramaYoneticisi:
        obj = self._tarama
        if obj is None:
            from app.core.tarama import TaramaYoneticisi

            obj = TaramaYoneticisi()
            self._tarama = obj
        return obj

    def _modeller_yoneticisi(self) -> ModellerYoneticisi:
        obj = self._modeller
        if obj is None:
            from app.core.modeller import ModellerYoneticisi

            obj = ModellerYoneticisi()
            self._modeller = obj
        return obj

    def _meta_yoneticisi(self) -> MetaYoneticisi:
        obj = self._meta
        if obj is None:
            from app.core.meta import MetaYoneticisi

            obj = MetaYoneticisi()
            self._meta = obj
        return obj

    def _ekleme_yoneticisi(self) -> EklemeYoneticisi:
        obj = self._ekleme
        if obj is None:
            from app.core.ekleme import EklemeYoneticisi

            obj = EklemeYoneticisi()
            self._ekleme = obj
        return obj

    def _enjeksiyon_yoneticisi(self) -> EnjeksiyonYoneticisi:
        obj = self._enjeksiyon
        if obj is None:
            from app.core.enjeksiyon import EnjeksiyonYoneticisi

            obj = EnjeksiyonYoneticisi()
            self._enjeksiyon = obj
        return obj

    def _parca_degistirme_yoneticisi(self) -> ParcaDegistirmeYoneticisi:
        obj = self._parca_degistirme
        if obj is None:
            from app.core.parca_degistirme import ParcaDegistirmeYoneticisi

            obj = ParcaDegistirmeYoneticisi()
            self._parca_degistirme = obj
        return obj

    def _yedekleme_yoneticisi(self) -> YedeklemeYoneticisi:
        obj = self._yedekleme
        if obj is None:
            from app.core.yedekleme import YedeklemeYoneticisi

            obj = YedeklemeYoneticisi()
            self._yedekleme = obj
        return obj

    def _dil_yoneticisi(self) -> DilYoneticisi:
        obj = self._dil
        if obj is None:
            from pathlib import Path

            from app.core.dil import DilYoneticisi
            from app.services.dil_servisi import DilServisi

            app_dir = Path(__file__).resolve().parent.parent
            lang_dir = app_dir / "assets" / "lang"

            obj = DilYoneticisi(DilServisi(lang_dir))
            self._dil = obj
        return obj

    def _dil_ekle_yoneticisi(self) -> DilGelistiriciYonetici:
        obj = self._dil_ekle
        if obj is None:
            from pathlib import Path

            from app.core.dil_ekle import DilGelistiriciYonetici

            app_dir = Path(__file__).resolve().parent.parent
            lang_dir = app_dir / "assets" / "lang"

            obj = DilGelistiriciYonetici(str(lang_dir))
            self._dil_ekle = obj
        return obj

    # =========================================================
    # PUBLIC YONETICI ERISIMLERI
    # =========================================================
    def degistirme(self) -> DegistirmeYoneticisi:
        return self._degistirme_yoneticisi()

    def tarama(self) -> TaramaYoneticisi:
        return self._tarama_yoneticisi()

    def modeller(self) -> ModellerYoneticisi:
        return self._modeller_yoneticisi()

    def meta(self) -> MetaYoneticisi:
        return self._meta_yoneticisi()

    def ekleme(self) -> EklemeYoneticisi:
        return self._ekleme_yoneticisi()

    def enjeksiyon(self) -> EnjeksiyonYoneticisi:
        return self._enjeksiyon_yoneticisi()

    def parca_degistirme(self) -> ParcaDegistirmeYoneticisi:
        return self._parca_degistirme_yoneticisi()

    def yedekleme(self) -> YedeklemeYoneticisi:
        return self._yedekleme_yoneticisi()

    def dil(self) -> DilYoneticisi:
        return self._dil_yoneticisi()

    def dil_ekle(self) -> DilGelistiriciYonetici:
        return self._dil_ekle_yoneticisi()

    def dil_gelistirici(self) -> DilGelistiriciYonetici:
        return self._dil_ekle_yoneticisi()

    # =========================================================
    # DIL
    # =========================================================
    def t(self, key: str) -> str:
        return self._dil_yoneticisi().t(key)

    def set_language(self, code: str) -> None:
        self._dil_yoneticisi().set_language(code)

    def get_language(self) -> str:
        return self._dil_yoneticisi().get_language()

    def is_rtl(self) -> bool:
        return self._dil_yoneticisi().is_rtl()

    def available_languages(self):
        return self._dil_yoneticisi().available_languages()

    # =========================================================
    # DIL EKLE / GELISTIRICI
    # =========================================================
    def dil_dosyalarini_listele(self) -> list[dict[str, object]]:
        return self._dil_ekle_yoneticisi().dil_dosyalarini_listele()

    def dil_kodlarini_listele(self) -> list[str]:
        return self._dil_ekle_yoneticisi().dil_kodlarini_listele()

    def dil_dosyasi_var_mi(self, dil_kodu: str) -> bool:
        return self._dil_ekle_yoneticisi().dil_dosyasi_var_mi(dil_kodu)

    def dil_dosyasi_yolu(self, dil_kodu: str) -> str:
        return self._dil_ekle_yoneticisi().dil_dosyasi_yolu(dil_kodu)

    def dil_verisini_yukle(self, dil_kodu: str) -> dict[str, object]:
        return self._dil_ekle_yoneticisi().dil_verisini_yukle(dil_kodu)

    def dil_keylerini_getir(
        self,
        dil_kodu: str,
        *,
        meta_dahil: bool = False,
    ) -> list[str]:
        return self._dil_ekle_yoneticisi().dil_keylerini_getir(
            dil_kodu,
            meta_dahil=meta_dahil,
        )

    def dil_ozeti_getir(self, dil_kodu: str) -> dict[str, object]:
        return self._dil_ekle_yoneticisi().dil_ozeti_getir(dil_kodu)

    def eksik_keyleri_bul(
        self,
        referans_dil_kodu: str,
        hedef_dil_kodu: str,
    ) -> list[str]:
        return self._dil_ekle_yoneticisi().eksik_keyleri_bul(
            referans_dil_kodu,
            hedef_dil_kodu,
        )

    def tum_dillerde_eksik_analizi(
        self,
        referans_dil_kodu: str,
    ) -> list[dict[str, object]]:
        return self._dil_ekle_yoneticisi().tum_dillerde_eksik_analizi(
            referans_dil_kodu
        )

    def tek_dile_key_ekle(
        self,
        dil_kodu: str,
        key: str,
        deger: str = "",
        *,
        varsa_uzerine_yaz: bool = False,
    ):
        return self._dil_ekle_yoneticisi().tek_dile_key_ekle(
            dil_kodu,
            key,
            deger,
            varsa_uzerine_yaz=varsa_uzerine_yaz,
        )

    def coklu_dillere_key_ekle(
        self,
        key: str,
        dil_deger_haritasi: dict[str, str],
        *,
        eksik_olanlara_ekle: bool = True,
        varsa_uzerine_yaz: bool = False,
    ):
        return self._dil_ekle_yoneticisi().coklu_dillere_key_ekle(
            key,
            dil_deger_haritasi,
            eksik_olanlara_ekle=eksik_olanlara_ekle,
            varsa_uzerine_yaz=varsa_uzerine_yaz,
        )

    def tum_dillere_key_ekle(
        self,
        key: str,
        varsayilan_deger: str = "",
        *,
        referans_dil_kodu: str | None = None,
        referans_degeri_kullan: bool = True,
        varsa_uzerine_yaz: bool = False,
    ):
        return self._dil_ekle_yoneticisi().tum_dillere_key_ekle(
            key,
            varsayilan_deger,
            referans_dil_kodu=referans_dil_kodu,
            referans_degeri_kullan=referans_degeri_kullan,
            varsa_uzerine_yaz=varsa_uzerine_yaz,
        )

    def eksik_keyleri_hedef_dile_ekle(
        self,
        referans_dil_kodu: str,
        hedef_dil_kodu: str,
        *,
        bos_deger_kullan: bool = True,
        varsa_uzerine_yaz: bool = False,
    ):
        return self._dil_ekle_yoneticisi().eksik_keyleri_hedef_dile_ekle(
            referans_dil_kodu,
            hedef_dil_kodu,
            bos_deger_kullan=bos_deger_kullan,
            varsa_uzerine_yaz=varsa_uzerine_yaz,
        )

    def yeni_dil_sablonu_uret(
        self,
        referans_dil_kodu: str,
        yeni_dil_kodu: str,
        yeni_dil_adi: str,
        *,
        bos_deger_kullan: bool = True,
    ):
        return self._dil_ekle_yoneticisi().yeni_dil_sablonu_uret(
            referans_dil_kodu,
            yeni_dil_kodu,
            yeni_dil_adi,
            bos_deger_kullan=bos_deger_kullan,
        )

    def yeni_dil_dosyasi_olustur(
        self,
        referans_dil_kodu: str,
        yeni_dil_kodu: str,
        yeni_dil_adi: str,
        *,
        bos_deger_kullan: bool = True,
        varsa_uzerine_yaz: bool = False,
    ):
        return self._dil_ekle_yoneticisi().yeni_dil_dosyasi_olustur(
            referans_dil_kodu,
            yeni_dil_kodu,
            yeni_dil_adi,
            bos_deger_kullan=bos_deger_kullan,
            varsa_uzerine_yaz=varsa_uzerine_yaz,
        )

    # =========================================================
    # DEGISTIRME
    # =========================================================
    def function_replace_error_sinifi(self) -> type[Exception]:
        return self._degistirme_yoneticisi().function_replace_error_sinifi()

    def validate_single_top_level_function_code(
        self,
        *,
        source_code: str,
        expected_name: str | None = None,
        allow_async: bool = True,
        allow_other_top_level_nodes: bool = False,
    ) -> FunctionCodeValidationResult:
        return self._degistirme_yoneticisi().validate_single_top_level_function_code(
            source_code=source_code,
            expected_name=expected_name,
            allow_async=allow_async,
            allow_other_top_level_nodes=allow_other_top_level_nodes,
        )

    def update_function_in_code(
        self,
        *,
        source_code: str,
        target_item: FunctionItem,
        new_code: str,
    ) -> str:
        return self._degistirme_yoneticisi().update_function_in_code(
            source_code=source_code,
            target_item=target_item,
            new_code=new_code,
        )

    def update_function_in_file(
        self,
        *,
        file_path: str,
        target_item: FunctionItem,
        new_code: str,
        backup: bool = True,
    ) -> str:
        return self._degistirme_yoneticisi().update_function_in_file(
            file_path=file_path,
            target_item=target_item,
            new_code=new_code,
            backup=backup,
        )

    def find_item_by_identity(
        self,
        *,
        items: list[FunctionItem],
        path: str,
        name: str,
        lineno: int,
        kind: str,
    ) -> FunctionItem | None:
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
    def function_scan_error_sinifi(self) -> type[Exception]:
        return self._tarama_yoneticisi().function_scan_error_sinifi()

    def scan_functions_from_code(
        self,
        *,
        source_code: str,
        file_path: str = "<memory>",
    ) -> list[FunctionItem]:
        return self._tarama_yoneticisi().scan_functions_from_code(
            source_code=source_code,
            file_path=file_path,
        )

    def scan_functions_from_file(
        self,
        *,
        file_path: str,
    ) -> list[FunctionItem]:
        return self._tarama_yoneticisi().scan_functions_from_file(
            file_path=file_path,
        )

    # =========================================================
    # EKLEME
    # =========================================================
    def function_insert_error_sinifi(self) -> type:
        return self._ekleme_yoneticisi().function_insert_error_sinifi()

    def insert_function(
        self,
        *,
        source_code: str,
        target_item: FunctionItem | None,
        new_code: str,
        mode: str,
    ) -> str:
        return self._ekleme_yoneticisi().insert_function(
            source_code=source_code,
            target_item=target_item,
            new_code=new_code,
            mode=mode,
        )

    def insert_function_in_file(
        self,
        *,
        file_path: str,
        target_item: FunctionItem | None,
        new_code: str,
        mode: str,
        backup: bool = True,
        encoding: str = "utf-8",
    ) -> str:
        return self._ekleme_yoneticisi().insert_function_in_file(
            file_path=file_path,
            target_item=target_item,
            new_code=new_code,
            mode=mode,
            backup=backup,
            encoding=encoding,
        )

    # =========================================================
    # ENJEKSIYON
    # =========================================================
    def inject_error_sinifi(self) -> type:
        return self._enjeksiyon_yoneticisi().inject_error_sinifi()

    def inject_code(
        self,
        *,
        source_code: str,
        target_item: FunctionItem,
        code: str,
        mode: str,
    ) -> str:
        return self._enjeksiyon_yoneticisi().inject(
            source_code=source_code,
            target_item=target_item,
            code=code,
            mode=mode,
        )

    def inject_code_in_file(
        self,
        *,
        file_path: str,
        target_item: FunctionItem,
        code: str,
        mode: str,
        backup: bool = True,
        encoding: str = "utf-8",
    ) -> str:
        return self._enjeksiyon_yoneticisi().inject_in_file(
            file_path=file_path,
            target_item=target_item,
            code=code,
            mode=mode,
            backup=backup,
            encoding=encoding,
        )

    # =========================================================
    # PARCA DEGISTIRME
    # =========================================================
    def parca_degistirme_hatasi_sinifi(self) -> type:
        return self._parca_degistirme_yoneticisi().parca_degistirme_hatasi_sinifi()

    def replace_piece_in_code(
        self,
        *,
        source_code: str,
        old_piece: str,
        new_piece: str,
        mode: str = "first",
        expected_count: int = 1,
        strict_python: bool = True,
    ) -> tuple[str, int]:
        return self._parca_degistirme_yoneticisi().replace_piece_in_code(
            source_code=source_code,
            old_piece=old_piece,
            new_piece=new_piece,
            mode=mode,
            expected_count=expected_count,
            strict_python=strict_python,
        )

    def replace_piece_in_file(
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
        return self._parca_degistirme_yoneticisi().replace_piece_in_file(
            file_path=file_path,
            old_piece=old_piece,
            new_piece=new_piece,
            mode=mode,
            expected_count=expected_count,
            strict_python=strict_python,
            encoding=encoding,
            make_backup=make_backup,
        )

    # =========================================================
    # YEDEKLEME
    # =========================================================
    def backup_kok_dizini(self) -> Path:
        return self._yedekleme_yoneticisi().backup_kok_dizini()

    def motor_backup_dizini(self, motor_adi: str) -> Path:
        return self._yedekleme_yoneticisi().motor_backup_dizini(motor_adi)

    def backup_dosya_yolu_uret(
        self,
        *,
        motor_adi: str,
        kaynak_dosya_adi: str,
        uzanti: str = ".bak",
    ) -> Path:
        return self._yedekleme_yoneticisi().backup_dosya_yolu_uret(
            motor_adi=motor_adi,
            kaynak_dosya_adi=kaynak_dosya_adi,
            uzanti=uzanti,
        )

    def yedek_sil(self, path: str | Path) -> bool:
        return self._yedekleme_yoneticisi().yedek_sil(path)

    def yedekleri_sil(self, paths: list[str | Path]) -> int:
        return self._yedekleme_yoneticisi().yedekleri_sil(paths)

    def motor_yedeklerini_sil(self, motor_adi: str) -> int:
        return self._yedekleme_yoneticisi().motor_yedeklerini_sil(motor_adi)

    def eski_yedekleri_sil(
        self,
        motor_adi: str,
        *,
        keep_last: int = 20,
    ) -> int:
        return self._yedekleme_yoneticisi().eski_yedekleri_sil(
            motor_adi,
            keep_last=keep_last,
        )

    def yedekleri_listele(self, motor_adi: str):
        return self._yedekleme_yoneticisi().yedekleri_listele(motor_adi)

    def backup_geri_yukle(
        self,
        *,
        backup_path: str,
        hedef_dosya: str,
        motor_adi: str,
        backup_once: bool = True,
    ) -> bool:
        return self._yedekleme_yoneticisi().backup_geri_yukle(
            backup_path=backup_path,
            hedef_dosya=hedef_dosya,
            motor_adi=motor_adi,
            backup_once=backup_once,
        )

    def son_yedegi_geri_yukle(
        self,
        *,
        motor_adi: str,
        hedef_dosya: str,
    ) -> bool:
        return self._yedekleme_yoneticisi().son_yedegi_geri_yukle(
            motor_adi=motor_adi,
            hedef_dosya=hedef_dosya,
        )

    def yedek_silme_hatasi_sinifi(self) -> type:
        return self._yedekleme_yoneticisi().yedek_silme_hatasi_sinifi()

    # =========================================================
    # MODELLER
    # =========================================================
    def function_item_sinifi(self) -> type:
        return self._modeller_yoneticisi().function_item_sinifi()

    # =========================================================
    # META
    # =========================================================
    def meta_bilgisi(self) -> dict[str, str | int]:
        return self._meta_yoneticisi().meta_bilgisi()

    def uygulama_adi(self) -> str:
        return self._meta_yoneticisi().uygulama_adi()

    def paket_adi(self) -> str:
        return self._meta_yoneticisi().paket_adi()

    def tarih(self) -> str:
        return self._meta_yoneticisi().tarih()

    def imza(self) -> str:
        return self._meta_yoneticisi().imza()

    def surum_adi(self) -> str:
        return self._meta_yoneticisi().surum_adi()

    def surum_kodu(self) -> int:
        return self._meta_yoneticisi().surum_kodu()

    def tam_surum(self) -> str:
        return self._meta_yoneticisi().tam_surum()
# -*- coding: utf-8 -*-
"""
DOSYA: app/services/sil_yada_geri_yukle.py

ROL:
- Yedek silme, oluşturma ve geri yükleme işlemlerini servis katmanında birleştirir
- Core yedekleme motorunu UI dostu ve sade API ile sunar
- Listeleme, tekil silme, toplu silme, motor bazlı temizleme,
  eski yedek temizleme, yedek oluşturma ve geri yükleme akışlarını merkezileştirir

MİMARİ:
- Thin service layer
- İş mantığını core katmanına bırakır
- Deterministik davranır
- Net ve sade API sunar
- Geriye uyumluluk katmanı içermez

BAĞIMLILIK:
- app/core/yedekleme/__init__.py
- app/core/yedekleme/yoneticisi.py

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Pydroid3 / masaüstü / test ortamlarında aynı mantıkla davranır

SURUM: 2
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from app.core.yedekleme import YedeklemeYoneticisi

if TYPE_CHECKING:
    from typing import Iterable


class SilYadaGeriYukleServisi:
    """
    Yedek silme, oluşturma ve geri yükleme servis katmanı.
    """

    __slots__ = ("_core",)

    def __init__(self) -> None:
        self._core = YedeklemeYoneticisi()

    # =========================================================
    # LISTELEME
    # =========================================================
    def yedekleri_listele(self, motor_adi: str) -> list[Path]:
        return self._core.yedekleri_listele(motor_adi)

    def backup_kok_dizini(self) -> Path:
        return self._core.backup_kok_dizini()

    def motor_backup_dizini(self, motor_adi: str) -> Path:
        return self._core.motor_backup_dizini(motor_adi)

    # =========================================================
    # OLUSTURMA
    # =========================================================
    def yedek_olustur(
        self,
        *,
        motor_adi: str,
        hedef_dosya: str,
        icerik: str,
        uzanti: str = ".bak",
        encoding: str = "utf-8",
    ) -> str:
        """
        Verilen içerik için motor bazlı yedek oluşturur.

        Returns:
            Oluşturulan yedek dosya yolu (str)
        """
        return self._core.yedek_olustur(
            motor_adi=motor_adi,
            hedef_dosya=hedef_dosya,
            icerik=icerik,
            uzanti=uzanti,
            encoding=encoding,
        )

    # =========================================================
    # SILME
    # =========================================================
    def yedek_sil(self, backup_path: str | Path) -> bool:
        return self._core.yedek_sil(backup_path)

    def yedekleri_sil(self, paths: Iterable[str | Path]) -> int:
        return self._core.yedekleri_sil(list(paths))

    def motor_yedeklerini_sil(self, motor_adi: str) -> int:
        return self._core.motor_yedeklerini_sil(motor_adi)

    def eski_yedekleri_sil(
        self,
        motor_adi: str,
        *,
        keep_last: int = 20,
    ) -> int:
        return self._core.eski_yedekleri_sil(
            motor_adi,
            keep_last=keep_last,
        )

    # =========================================================
    # GERI YUKLEME
    # =========================================================
    def backup_geri_yukle(
        self,
        *,
        backup_path: str,
        hedef_dosya: str,
        motor_adi: str,
        backup_once: bool = True,
    ) -> bool:
        return self._core.backup_geri_yukle(
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
        return self._core.son_yedegi_geri_yukle(
            motor_adi=motor_adi,
            hedef_dosya=hedef_dosya,
        )

    # =========================================================
    # ERROR
    # =========================================================
    def yedek_silme_hatasi_sinifi(self) -> type[Exception]:
        return self._core.yedek_silme_hatasi_sinifi()
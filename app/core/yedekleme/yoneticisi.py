# -*- coding: utf-8 -*-
"""
DOSYA: app/core/yedekleme/yoneticisi.py

ROL:
- Yedekleme sistemine facade sağlar
- Yedekleme, listeleme, geri yükleme ve silme işlemlerini tek noktadan yönetir
- Üst katmanların yollar.py, silici.py ve geri_yukleyici.py detaylarını bilmesini engeller

MİMARİ:
- Lazy load + strict cache
- Module yerine fonksiyon referansı cache edilir
- Net API sunar
- Deterministik davranır
- Geriye uyumluluk yok
- Micro-perf optimize

KAPSAM:
- Backup kök dizini
- Motor backup dizini
- Backup dosya yolu üretimi
- Yedek oluşturma
- Yedek listeleme
- Tekil yedek silme
- Toplu yedek silme
- Motor yedeklerini temizleme
- Otomatik eski yedek temizleme
- Tekil backup geri yükleme
- Son yedeği geri yükleme

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Pydroid3 / masaüstü / test ortamlarında aynı mantıkla davranır

SURUM: 3
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable


class YedeklemeYoneticisi:
    """
    Yedekleme facade katmanı.
    """

    __slots__ = (
        "_backup_kok_dizini_fn",
        "_motor_backup_dizini_fn",
        "_backup_dosya_yolu_uret_fn",
        "_yedek_olustur_fn",
        "_yedekleri_listele_fn",
        "_backup_geri_yukle_fn",
        "_son_yedegi_geri_yukle_fn",
        "_backup_sil_fn",
        "_backuplari_sil_fn",
        "_motor_yedeklerini_sil_fn",
        "_eski_yedekleri_sil_fn",
        "_error_cls",
    )

    def __init__(self) -> None:
        self._backup_kok_dizini_fn: Callable[[], Path] | None = None
        self._motor_backup_dizini_fn: Callable[[str], Path] | None = None
        self._backup_dosya_yolu_uret_fn: Callable[..., Path] | None = None

        self._yedek_olustur_fn: Callable[..., str] | None = None
        self._yedekleri_listele_fn: Callable[[str], list[Path]] | None = None
        self._backup_geri_yukle_fn: Callable[..., bool] | None = None
        self._son_yedegi_geri_yukle_fn: Callable[..., bool] | None = None

        self._backup_sil_fn: Callable[[str | Path], bool] | None = None
        self._backuplari_sil_fn: Callable[[Iterable[str | Path]], int] | None = None
        self._motor_yedeklerini_sil_fn: Callable[[str], int] | None = None
        self._eski_yedekleri_sil_fn: Callable[..., int] | None = None

        self._error_cls: type[Exception] | None = None

    # =========================================================
    # INTERNAL (LAZY + STRICT CACHE)
    # =========================================================
    def _load(self) -> None:
        if self._backup_kok_dizini_fn is not None:
            return

        from app.core.yedekleme.yollar import (
            backup_dosya_yolu_uret,
            backup_kok_dizini,
            motor_backup_dizini,
        )
        from app.core.yedekleme.islemler import (
            YedeklemeHatasi,
            backup_geri_yukle,
            eski_yedekleri_sil,
            motor_yedeklerini_sil,
            son_yedegi_geri_yukle,
            yedek_olustur,
            yedek_sil,
            yedekleri_listele,
            yedekleri_sil,
        )

        self._backup_kok_dizini_fn = backup_kok_dizini
        self._motor_backup_dizini_fn = motor_backup_dizini
        self._backup_dosya_yolu_uret_fn = backup_dosya_yolu_uret

        self._yedek_olustur_fn = yedek_olustur
        self._yedekleri_listele_fn = yedekleri_listele
        self._backup_geri_yukle_fn = backup_geri_yukle
        self._son_yedegi_geri_yukle_fn = son_yedegi_geri_yukle

        self._backup_sil_fn = yedek_sil
        self._backuplari_sil_fn = yedekleri_sil
        self._motor_yedeklerini_sil_fn = motor_yedeklerini_sil
        self._eski_yedekleri_sil_fn = eski_yedekleri_sil

        self._error_cls = YedeklemeHatasi

    def _backup_kok(self) -> Callable[[], Path]:
        if self._backup_kok_dizini_fn is None:
            self._load()
        return self._backup_kok_dizini_fn  # type: ignore[return-value]

    def _motor_backup(self) -> Callable[[str], Path]:
        if self._motor_backup_dizini_fn is None:
            self._load()
        return self._motor_backup_dizini_fn  # type: ignore[return-value]

    def _backup_yolu(self) -> Callable[..., Path]:
        if self._backup_dosya_yolu_uret_fn is None:
            self._load()
        return self._backup_dosya_yolu_uret_fn  # type: ignore[return-value]

    def _yedek_olustur(self) -> Callable[..., str]:
        if self._yedek_olustur_fn is None:
            self._load()
        return self._yedek_olustur_fn  # type: ignore[return-value]

    def _yedekleri_listele(self) -> Callable[[str], list[Path]]:
        if self._yedekleri_listele_fn is None:
            self._load()
        return self._yedekleri_listele_fn  # type: ignore[return-value]

    def _geri_yukle(self) -> Callable[..., bool]:
        if self._backup_geri_yukle_fn is None:
            self._load()
        return self._backup_geri_yukle_fn  # type: ignore[return-value]

    def _son_geri_yukle(self) -> Callable[..., bool]:
        if self._son_yedegi_geri_yukle_fn is None:
            self._load()
        return self._son_yedegi_geri_yukle_fn  # type: ignore[return-value]

    def _yedek_sil(self) -> Callable[[str | Path], bool]:
        if self._backup_sil_fn is None:
            self._load()
        return self._backup_sil_fn  # type: ignore[return-value]

    def _yedekleri_sil(self) -> Callable[[Iterable[str | Path]], int]:
        if self._backuplari_sil_fn is None:
            self._load()
        return self._backuplari_sil_fn  # type: ignore[return-value]

    def _motor_sil(self) -> Callable[[str], int]:
        if self._motor_yedeklerini_sil_fn is None:
            self._load()
        return self._motor_yedeklerini_sil_fn  # type: ignore[return-value]

    def _eski_sil(self) -> Callable[..., int]:
        if self._eski_yedekleri_sil_fn is None:
            self._load()
        return self._eski_yedekleri_sil_fn  # type: ignore[return-value]

    def _error(self) -> type[Exception]:
        if self._error_cls is None:
            self._load()
        return self._error_cls  # type: ignore[return-value]

    # =========================================================
    # PUBLIC API - YOLLAR
    # =========================================================
    def backup_kok_dizini(self) -> Path:
        return self._backup_kok()()

    def motor_backup_dizini(self, motor_adi: str) -> Path:
        return self._motor_backup()(motor_adi)

    def backup_dosya_yolu_uret(
        self,
        *,
        motor_adi: str,
        kaynak_dosya_adi: str,
        uzanti: str = ".bak",
    ) -> Path:
        return self._backup_yolu()(
            motor_adi=motor_adi,
            kaynak_dosya_adi=kaynak_dosya_adi,
            uzanti=uzanti,
        )

    # =========================================================
    # PUBLIC API - OLUSTUR / LISTE
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
        return self._yedek_olustur()(
            motor_adi=motor_adi,
            hedef_dosya=hedef_dosya,
            icerik=icerik,
            uzanti=uzanti,
            encoding=encoding,
        )

    def yedekleri_listele(self, motor_adi: str) -> list[Path]:
        return self._yedekleri_listele()(motor_adi)

    # =========================================================
    # PUBLIC API - GERI YUKLE
    # =========================================================
    def backup_geri_yukle(
        self,
        *,
        backup_path: str,
        hedef_dosya: str,
        motor_adi: str,
        backup_once: bool = True,
    ) -> bool:
        return self._geri_yukle()(
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
        return self._son_geri_yukle()(
            motor_adi=motor_adi,
            hedef_dosya=hedef_dosya,
        )

    # =========================================================
    # PUBLIC API - SILME
    # =========================================================
    def yedek_sil(self, backup_path: str | Path) -> bool:
        return self._yedek_sil()(backup_path)

    def yedekleri_sil(self, paths: Iterable[str | Path]) -> int:
        return self._yedekleri_sil()(paths)

    def motor_yedeklerini_sil(self, motor_adi: str) -> int:
        return self._motor_sil()(motor_adi)

    def eski_yedekleri_sil(
        self,
        motor_adi: str,
        *,
        keep_last: int = 20,
    ) -> int:
        return self._eski_sil()(
            motor_adi,
            keep_last=keep_last,
        )

    # =========================================================
    # ERROR
    # =========================================================
    def yedek_silme_hatasi_sinifi(self) -> type[Exception]:
        return self._error()
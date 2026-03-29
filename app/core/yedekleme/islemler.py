# -*- coding: utf-8 -*-
"""
DOSYA: app/core/yedekleme/islemler.py

ROL:
- Yedekleme işlemlerinin gerçek uygulama katmanıdır
- Yedek oluşturma, listeleme, geri yükleme ve silme işlemlerini yürütür
- Motor bazlı yedek klasör yapısını kullanır

MİMARİ:
- Saf Python çalışır
- Deterministik davranır
- Type güvenliği yüksektir
- Atomic write uygular
- Geriye uyumluluk katmanı içermez

BAĞIMLILIK:
- app/core/yedekleme/yollar.py

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Pydroid3 / masaüstü / test ortamlarında aynı mantıkla davranır

SURUM: 1
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from app.core.yedekleme.yollar import (
    backup_dosya_yolu_uret,
    motor_backup_dizini,
)


class YedeklemeHatasi(ValueError):
    """
    Yedekleme işlemlerinde oluşan kontrollü hata.
    """


def _normalize_motor_adi(motor_adi: str) -> str:
    value = str(motor_adi or "").strip().lower()
    if not value:
        raise YedeklemeHatasi("motor_adi boş olamaz.")
    return value


def _normalize_path(value: str | Path) -> Path:
    raw = str(value or "").strip()
    if not raw:
        raise YedeklemeHatasi("Dosya yolu boş olamaz.")
    return Path(raw)


def _safe_unlink(path_obj: Path) -> bool:
    try:
        if path_obj.exists():
            path_obj.unlink()
            return True
        return False
    except Exception as exc:
        raise YedeklemeHatasi(f"Dosya silinemedi: {path_obj}") from exc


def _atomic_write_text(path_obj: Path, content: str, encoding: str = "utf-8") -> None:
    tmp_path = path_obj.with_name(f".{path_obj.name}.tmp")

    try:
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        tmp_path.write_text(str(content or ""), encoding=encoding)
        os.replace(str(tmp_path), str(path_obj))
    except Exception as exc:
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            pass
        raise YedeklemeHatasi(f"Dosya güvenli şekilde yazılamadı: {path_obj}") from exc


def yedek_olustur(
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
    normalized_motor = _normalize_motor_adi(motor_adi)
    hedef_path = _normalize_path(hedef_dosya)

    backup_path = backup_dosya_yolu_uret(
        motor_adi=normalized_motor,
        kaynak_dosya_adi=hedef_path.name,
        uzanti=uzanti,
    )

    _atomic_write_text(backup_path, icerik, encoding=encoding)
    return str(backup_path)


def yedekleri_listele(motor_adi: str) -> list[Path]:
    """
    İstenen motor için yedekleri en yeniden eskiye listeler.
    """
    normalized_motor = _normalize_motor_adi(motor_adi)
    backup_dir = motor_backup_dizini(normalized_motor)

    items = [item for item in backup_dir.iterdir() if item.is_file()]
    items.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return items


def backup_geri_yukle(
    *,
    backup_path: str,
    hedef_dosya: str,
    motor_adi: str,
    backup_once: bool = True,
) -> bool:
    """
    Belirli bir yedek dosyayı hedef dosyaya geri yükler.
    """
    normalized_motor = _normalize_motor_adi(motor_adi)
    source_backup = _normalize_path(backup_path)
    hedef_path = _normalize_path(hedef_dosya)

    if not source_backup.exists() or not source_backup.is_file():
        raise YedeklemeHatasi(f"Yedek dosya bulunamadı: {source_backup}")

    try:
        backup_content = source_backup.read_text(encoding="utf-8")
    except Exception as exc:
        raise YedeklemeHatasi(f"Yedek dosya okunamadı: {source_backup}") from exc

    if backup_once and hedef_path.exists() and hedef_path.is_file():
        try:
            mevcut_icerik = hedef_path.read_text(encoding="utf-8")
        except Exception as exc:
            raise YedeklemeHatasi(f"Hedef dosya okunamadı: {hedef_path}") from exc

        yedek_olustur(
            motor_adi=normalized_motor,
            hedef_dosya=str(hedef_path),
            icerik=mevcut_icerik,
            uzanti=".restore_before.bak",
            encoding="utf-8",
        )

    _atomic_write_text(hedef_path, backup_content, encoding="utf-8")
    return True


def son_yedegi_geri_yukle(
    *,
    motor_adi: str,
    hedef_dosya: str,
) -> bool:
    """
    İstenen motor için en son yedeği hedef dosyaya geri yükler.
    """
    backups = yedekleri_listele(motor_adi)
    if not backups:
        raise YedeklemeHatasi(f"Geri yüklenecek yedek yok: {motor_adi}")

    return backup_geri_yukle(
        backup_path=str(backups[0]),
        hedef_dosya=hedef_dosya,
        motor_adi=motor_adi,
        backup_once=True,
    )


def yedek_sil(backup_path: str | Path) -> bool:
    """
    Tekil yedek dosyayı siler.
    """
    path_obj = _normalize_path(backup_path)
    return _safe_unlink(path_obj)


def yedekleri_sil(paths: Iterable[str | Path]) -> int:
    """
    Birden fazla yedek dosyayı siler.
    """
    deleted = 0

    for item in paths:
        if yedek_sil(item):
            deleted += 1

    return deleted


def motor_yedeklerini_sil(motor_adi: str) -> int:
    """
    Bir motorun tüm yedeklerini siler.
    """
    backups = yedekleri_listele(motor_adi)
    return yedekleri_sil(backups)


def eski_yedekleri_sil(
    motor_adi: str,
    *,
    keep_last: int = 20,
) -> int:
    """
    En yeni N yedek dışında kalan eski yedekleri siler.
    """
    if int(keep_last) < 0:
        raise YedeklemeHatasi("keep_last 0 veya daha büyük olmalıdır.")

    backups = yedekleri_listele(motor_adi)
    targets = backups[int(keep_last):]
    return yedekleri_sil(targets)
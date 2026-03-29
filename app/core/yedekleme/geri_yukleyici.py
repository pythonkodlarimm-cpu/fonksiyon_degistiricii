# -*- coding: utf-8 -*-
"""
DOSYA: app/core/yedekleme/geri_yukleyici.py

ROL:
- Yedek dosyalardan geri yükleme (restore) işlemlerini yapar
- Son yedeği geri alma (undo) desteği sağlar

MİMARİ:
- Deterministik
- Fail-fast
- Atomik yazım
- Restore öncesi otomatik backup (chain-safe)

SURUM: 1
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import List

from app.core.yedekleme.yollar import (
    backup_kok_dizini,
    motor_backup_dizini,
    backup_dosya_yolu_uret,
)


class YedekGeriYuklemeHatasi(ValueError):
    pass


# =========================================================
# INTERNAL
# =========================================================
def _resolve(p: str | Path) -> Path:
    return Path(p).expanduser().resolve()


def _validate_backup(path: Path) -> None:
    root = backup_kok_dizini().resolve()

    try:
        path.relative_to(root)
    except Exception:
        raise YedekGeriYuklemeHatasi("Backup root dışı path.")

    if not path.exists():
        raise YedekGeriYuklemeHatasi("Backup bulunamadı.")

    if not path.name.endswith(".bak"):
        raise YedekGeriYuklemeHatasi("Geçersiz backup uzantısı.")


def _atomic_write(target: Path, data: str) -> None:
    tmp = target.with_suffix(".tmp")

    tmp.write_text(data, encoding="utf-8")
    os.replace(tmp, target)


# =========================================================
# PUBLIC API
# =========================================================
def backup_geri_yukle(
    *,
    backup_path: str,
    hedef_dosya: str,
    motor_adi: str,
    backup_once: bool = True,
) -> bool:
    """
    Belirli bir yedekten dosyayı geri yükler.
    """

    bpath = _resolve(backup_path)
    target = _resolve(hedef_dosya)

    _validate_backup(bpath)

    if not target.exists():
        raise YedekGeriYuklemeHatasi("Hedef dosya bulunamadı.")

    try:
        content = bpath.read_text(encoding="utf-8")
    except Exception as exc:
        raise YedekGeriYuklemeHatasi("Backup okunamadı.") from exc

    # chain backup
    if backup_once:
        backup_new = backup_dosya_yolu_uret(
            motor_adi=motor_adi,
            kaynak_dosya_adi=target.name,
        )
        shutil.copyfile(target, backup_new)

    _atomic_write(target, content)

    return True


def son_yedegi_geri_yukle(
    *,
    motor_adi: str,
    hedef_dosya: str,
) -> bool:
    """
    En son yedeği geri yükler (undo).
    """

    mdir = motor_backup_dizini(motor_adi)

    files = list(mdir.glob("*.bak"))

    if not files:
        raise YedekGeriYuklemeHatasi("Hiç backup yok.")

    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    latest = files[0]

    return backup_geri_yukle(
        backup_path=str(latest),
        hedef_dosya=hedef_dosya,
        motor_adi=motor_adi,
    )


def tum_yedekleri_listele(motor_adi: str) -> List[Path]:
    """
    Motor bazlı tüm yedekleri döndürür.
    """

    mdir = motor_backup_dizini(motor_adi)

    files = list(mdir.glob("*.bak"))

    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    return files
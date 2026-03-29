# -*- coding: utf-8 -*-
"""
DOSYA: app/core/yedekleme/silici.py

ROL:
- Yedek dosyalarını güvenli şekilde siler
- Toplu silme ve motor bazlı temizleme sağlar
- Otomatik eski yedek temizleme işlemlerini yürütür

MİMARİ:
- Deterministik davranış
- Fail-fast (geçersiz girişlerde direkt hata)
- Güvenli path doğrulama (sandbox: backup kök dizini)
- Sadece .bak uzantılı dosyalar işlenir
- Platform bağımsız (Android API 35 uyumlu)

KAPSAM:
- Tek yedek silme
- Toplu yedek silme
- Motor klasörü temizleme
- Eski yedekleri adet bazlı temizleme

GÜVENLİK:
- Sadece backup kök dizini altında işlem yapılır
- Harici path'ler reddedilir
- Dosya olmayan path'ler reddedilir

SURUM: 1
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final, Iterable

from app.core.yedekleme.yollar import backup_kok_dizini, motor_backup_dizini


# =========================================================
# SABITLER
# =========================================================
BAK_SUFFIX: Final[str] = ".bak"


# =========================================================
# HATA
# =========================================================
class YedekSilmeHatasi(ValueError):
    """
    Yedek silme işlemleri sırasında oluşan kontrollü hata.
    """


# =========================================================
# INTERNAL (VALIDATION)
# =========================================================
def _normalize_path(path: str | Path) -> Path:
    p = Path(path).expanduser().resolve()
    return p


def _ensure_within_backup_root(path_obj: Path) -> None:
    root = backup_kok_dizini().resolve()

    try:
        path_obj.relative_to(root)
    except Exception:
        raise YedekSilmeHatasi(
            f"Yetkisiz path (backup dışı): {path_obj}"
        )


def _ensure_valid_backup_file(path_obj: Path) -> None:
    if not path_obj.exists():
        raise YedekSilmeHatasi(f"Dosya bulunamadı: {path_obj}")

    if not path_obj.is_file():
        raise YedekSilmeHatasi(f"Geçerli bir dosya değil: {path_obj}")

    if not path_obj.name.endswith(BAK_SUFFIX):
        raise YedekSilmeHatasi(
            f"Sadece '{BAK_SUFFIX}' uzantılı dosyalar silinebilir: {path_obj}"
        )


def _validate_and_resolve_backup(path: str | Path) -> Path:
    path_obj = _normalize_path(path)
    _ensure_within_backup_root(path_obj)
    _ensure_valid_backup_file(path_obj)
    return path_obj


# =========================================================
# CORE OPERATIONS
# =========================================================
def backup_sil(backup_path: str | Path) -> bool:
    """
    Tek bir yedek dosyasını siler.

    Returns:
        True -> başarıyla silindi
    """
    path_obj = _validate_and_resolve_backup(backup_path)

    try:
        path_obj.unlink()
        return True
    except Exception as exc:
        raise YedekSilmeHatasi(
            f"Yedek silinemedi: {path_obj}"
        ) from exc


def backuplari_sil(backup_paths: Iterable[str | Path]) -> int:
    """
    Birden fazla yedek dosyasını siler.

    Returns:
        Silinen dosya sayısı
    """
    if backup_paths is None:
        raise YedekSilmeHatasi("backup_paths boş olamaz.")

    count = 0

    for p in backup_paths:
        backup_sil(p)
        count += 1

    return count


def motor_yedeklerini_sil(motor_adi: str) -> int:
    """
    Belirli bir motorun tüm yedeklerini siler.

    Returns:
        Silinen dosya sayısı
    """
    motor_dir = motor_backup_dizini(motor_adi)

    files = list(motor_dir.glob(f"*{BAK_SUFFIX}"))

    if not files:
        return 0

    count = 0
    for f in files:
        _ensure_within_backup_root(f)
        if f.is_file() and f.name.endswith(BAK_SUFFIX):
            f.unlink()
            count += 1

    return count


def eski_yedekleri_sil(
    motor_adi: str,
    *,
    keep_last: int = 20,
) -> int:
    """
    En son N yedeği tutar, geri kalanları siler.

    Args:
        motor_adi: motor adı
        keep_last: kaç adet yedek tutulacak

    Returns:
        Silinen dosya sayısı
    """
    if keep_last < 0:
        raise YedekSilmeHatasi("keep_last negatif olamaz.")

    motor_dir = motor_backup_dizini(motor_adi)

    files = list(motor_dir.glob(f"*{BAK_SUFFIX}"))

    if not files:
        return 0

    # en yeni -> eski sıralama
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    to_delete = files[keep_last:]

    if not to_delete:
        return 0

    count = 0

    for f in to_delete:
        _ensure_within_backup_root(f)
        if f.is_file():
            f.unlink()
            count += 1

    return count
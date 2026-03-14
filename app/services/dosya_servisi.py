# -*- coding: utf-8 -*-
"""
DOSYA: app/services/dosya_servisi.py
ROL:
- Metin dosyalarını güvenli biçimde okumak / yazmak
- Gerekirse yedek dosya üretmek
- Android / APK tarafında daha güvenli dosya işlemi sağlamak
"""

from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path


class DosyaServisiHatasi(ValueError):
    """Dosya işlemleri sırasında oluşan kontrollü hata."""


def _normalize_path(file_path: str) -> Path:
    raw = str(file_path or "").strip()
    if not raw:
        raise DosyaServisiHatasi("Dosya yolu boş.")
    return Path(raw)


def _build_backup_path(path_obj: Path) -> Path:
    default_backup = path_obj.with_suffix(path_obj.suffix + ".bak")
    if not default_backup.exists():
        return default_backup

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return path_obj.with_name(f"{path_obj.name}.{ts}.bak")


def _build_temp_path(path_obj: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return path_obj.with_name(f".{path_obj.name}.{ts}.tmp")


def read_text(file_path: str, encoding: str = "utf-8") -> str:
    path_obj = _normalize_path(file_path)

    if not path_obj.exists():
        raise DosyaServisiHatasi(f"Dosya bulunamadı: {path_obj}")

    if not path_obj.is_file():
        raise DosyaServisiHatasi(f"Geçerli bir dosya değil: {path_obj}")

    try:
        return path_obj.read_text(encoding=encoding)
    except UnicodeDecodeError as exc:
        raise DosyaServisiHatasi(
            f"Dosya '{encoding}' ile okunamadı: {path_obj}"
        ) from exc
    except OSError as exc:
        raise DosyaServisiHatasi(f"Dosya okunamadı: {path_obj}") from exc


def write_text(file_path: str, content: str, encoding: str = "utf-8") -> None:
    path_obj = _normalize_path(file_path)

    if path_obj.exists() and not path_obj.is_file():
        raise DosyaServisiHatasi(f"Geçerli bir dosya değil: {path_obj}")

    if not path_obj.parent.exists():
        raise DosyaServisiHatasi(f"Hedef klasör bulunamadı: {path_obj.parent}")

    temp_path = _build_temp_path(path_obj)

    try:
        temp_path.write_text(str(content or ""), encoding=encoding)
        os.replace(str(temp_path), str(path_obj))
    except Exception as exc:
        try:
            if temp_path.exists():
                temp_path.unlink()
        except Exception:
            pass
        raise DosyaServisiHatasi(f"Dosya yazılamadı: {path_obj}") from exc


def backup_file(file_path: str) -> str:
    path_obj = _normalize_path(file_path)

    if not path_obj.exists():
        raise DosyaServisiHatasi(f"Yedek alınacak dosya bulunamadı: {path_obj}")

    if not path_obj.is_file():
        raise DosyaServisiHatasi(f"Geçerli bir dosya değil: {path_obj}")

    backup_path = _build_backup_path(path_obj)

    try:
        shutil.copyfile(path_obj, backup_path)
    except Exception as exc:
        raise DosyaServisiHatasi(f"Yedek dosya oluşturulamadı: {backup_path}") from exc

    return str(backup_path)


def exists(file_path: str) -> bool:
    try:
        return _normalize_path(file_path).is_file()
    except Exception:
        return False
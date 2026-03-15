# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import os
import shutil
from datetime import datetime
from pathlib import Path


class DosyaServisiHatasi(ValueError):
    pass


def _normalize_path(file_path: str | Path) -> Path:
    raw = str(file_path or "").strip()
    if not raw:
        raise DosyaServisiHatasi("Dosya yolu boş.")
    return Path(raw)


def _hash_text(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def _path_exists(path_obj: Path) -> bool:
    try:
        return path_obj.exists()
    except Exception:
        return False


def _path_is_file(path_obj: Path) -> bool:
    try:
        return path_obj.is_file()
    except Exception:
        return False


def _path_is_dir(path_obj: Path) -> bool:
    try:
        return path_obj.is_dir()
    except Exception:
        return False


def _build_backup_path(path_obj: Path) -> Path:
    default_backup = path_obj.with_suffix(path_obj.suffix + ".bak")
    if not default_backup.exists():
        return default_backup

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return path_obj.with_name(f"{path_obj.name}.{ts}.bak")


def _build_temp_path(path_obj: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return path_obj.with_name(f".{path_obj.name}.{ts}.tmp")


def _ensure_parent_dir_exists(path_obj: Path) -> None:
    parent = path_obj.parent
    if not parent.exists():
        raise DosyaServisiHatasi(f"Hedef klasör bulunamadı: {parent}")
    if not parent.is_dir():
        raise DosyaServisiHatasi(f"Hedef klasör geçerli değil: {parent}")


def _cleanup_temp_file(temp_path: Path) -> None:
    try:
        if temp_path.exists():
            temp_path.unlink()
    except Exception:
        pass


def _uygulama_veri_koku() -> Path:
    """
    Python / masaüstü testinde görünür ve sabit bir klasör kullan.
    """
    adaylar = [
        Path.cwd(),
        Path.home(),
    ]

    for aday in adaylar:
        try:
            if aday.exists() and aday.is_dir():
                root = aday / "fonksiyon_degistirici_veri"
                root.mkdir(parents=True, exist_ok=True)
                return root
        except Exception:
            pass

    root = Path("fonksiyon_degistirici_veri")
    root.mkdir(parents=True, exist_ok=True)
    return root


def read_text(file_path: str | Path, encoding: str = "utf-8") -> str:
    path_obj = _normalize_path(file_path)

    if not _path_exists(path_obj):
        raise DosyaServisiHatasi(f"Dosya bulunamadı: {path_obj}")

    if not _path_is_file(path_obj):
        raise DosyaServisiHatasi(f"Geçerli bir dosya değil: {path_obj}")

    try:
        return path_obj.read_text(encoding=encoding)
    except UnicodeDecodeError as exc:
        raise DosyaServisiHatasi(f"Dosya '{encoding}' ile okunamadı: {path_obj}") from exc
    except OSError as exc:
        raise DosyaServisiHatasi(f"Dosya okunamadı: {path_obj}") from exc


def write_text(file_path: str | Path, content: str, encoding: str = "utf-8") -> None:
    path_obj = _normalize_path(file_path)

    if _path_exists(path_obj) and not _path_is_file(path_obj):
        raise DosyaServisiHatasi(f"Geçerli bir dosya değil: {path_obj}")

    _ensure_parent_dir_exists(path_obj)

    temp_path = _build_temp_path(path_obj)
    hedef = str(content or "")
    hedef_hash = _hash_text(hedef)

    try:
        with open(temp_path, "w", encoding=encoding, newline="") as f:
            f.write(hedef)
            f.flush()
            os.fsync(f.fileno())

        os.replace(str(temp_path), str(path_obj))

        dogrula = path_obj.read_text(encoding=encoding)
        if _hash_text(dogrula) != hedef_hash:
            raise DosyaServisiHatasi(f"Dosya yazma doğrulaması başarısız oldu: {path_obj}")

    except DosyaServisiHatasi:
        _cleanup_temp_file(temp_path)
        raise
    except Exception as exc:
        _cleanup_temp_file(temp_path)
        raise DosyaServisiHatasi(f"Dosya yazılamadı: {path_obj}") from exc


def backup_file(file_path: str | Path) -> str:
    path_obj = _normalize_path(file_path)

    if not _path_exists(path_obj):
        raise DosyaServisiHatasi(f"Yedek alınacak dosya bulunamadı: {path_obj}")

    if not _path_is_file(path_obj):
        raise DosyaServisiHatasi(f"Geçerli bir dosya değil: {path_obj}")

    backup_path = _build_backup_path(path_obj)

    try:
        shutil.copy2(path_obj, backup_path)
    except Exception as exc:
        raise DosyaServisiHatasi(f"Yedek dosya oluşturulamadı: {backup_path}") from exc

    return str(backup_path)


def exists(file_path: str | Path) -> bool:
    try:
        path_obj = _normalize_path(file_path)
        return _path_exists(path_obj) and _path_is_file(path_obj)
    except Exception:
        return False


def get_display_name(file_path: str | Path) -> str:
    try:
        return _normalize_path(file_path).name
    except Exception:
        return ""


def get_app_working_root() -> Path:
    root = _uygulama_veri_koku() / "app_working_imports"
    root.mkdir(parents=True, exist_ok=True)
    return root


def get_app_backups_root() -> Path:
    root = _uygulama_veri_koku() / "app_document_backups"
    root.mkdir(parents=True, exist_ok=True)
    return root

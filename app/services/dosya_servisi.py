# -*- coding: utf-8 -*-
"""
DOSYA: app/services/dosya_servisi.py

SURUM: 7
"""

from __future__ import annotations

import hashlib
import os
import shutil
from datetime import datetime
from pathlib import Path


class DosyaServisiHatasi(ValueError):
    pass


# =========================================================
# PATH
# =========================================================
def _normalize_path(file_path: str | Path) -> Path:
    raw = str(file_path or "").strip()

    if not raw:
        raise DosyaServisiHatasi("Dosya yolu boş.")

    if raw.startswith("content://"):
        raise DosyaServisiHatasi(
            "content:// URI bu serviste kullanılamaz."
        )

    return Path(raw)


def _path_exists(p: Path) -> bool:
    try:
        return p.exists()
    except Exception:
        return False


def _path_is_file(p: Path) -> bool:
    try:
        return p.is_file()
    except Exception:
        return False


def _path_is_dir(p: Path) -> bool:
    try:
        return p.is_dir()
    except Exception:
        return False


# =========================================================
# HASH
# =========================================================
def _hash_text(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


# =========================================================
# ROOT
# =========================================================
def _uygulama_veri_koku() -> Path:
    adaylar: list[Path] = []

    try:
        adaylar.append(Path.cwd())
    except Exception:
        pass

    try:
        adaylar.append(Path.home())
    except Exception:
        pass

    for aday in adaylar:
        try:
            if _path_exists(aday) and _path_is_dir(aday):
                root = aday / "fonksiyon_degistirici_veri"
                root.mkdir(parents=True, exist_ok=True)
                return root
        except Exception:
            pass

    root = Path("fonksiyon_degistirici_veri")
    root.mkdir(parents=True, exist_ok=True)
    return root


# =========================================================
# READ
# =========================================================
def read_text(file_path: str | Path, encoding: str = "utf-8") -> str:
    path_obj = _normalize_path(file_path)

    if not _path_exists(path_obj):
        raise DosyaServisiHatasi(f"Dosya bulunamadı: {path_obj}")

    if not _path_is_file(path_obj):
        raise DosyaServisiHatasi(f"Geçerli bir dosya değil: {path_obj}")

    try:
        return path_obj.read_text(encoding=encoding)
    except UnicodeDecodeError:
        # fallback (çok önemli Android için)
        try:
            return path_obj.read_text(encoding="latin-1")
        except Exception as exc:
            raise DosyaServisiHatasi(
                f"Dosya okunamadı (encoding): {path_obj}"
            ) from exc
    except Exception as exc:
        raise DosyaServisiHatasi(
            f"Dosya okunamadı: {path_obj}"
        ) from exc


# =========================================================
# WRITE
# =========================================================
def write_text(file_path: str | Path, content: str, encoding: str = "utf-8") -> None:
    path_obj = _normalize_path(file_path)

    if _path_exists(path_obj) and not _path_is_file(path_obj):
        raise DosyaServisiHatasi(f"Geçerli dosya değil: {path_obj}")

    parent = path_obj.parent
    if not _path_exists(parent):
        parent.mkdir(parents=True, exist_ok=True)

    temp_path = path_obj.with_name(
        f".{path_obj.name}.{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.tmp"
    )

    hedef = str(content or "")
    hedef_hash = _hash_text(hedef)

    try:
        with open(temp_path, "w", encoding=encoding, newline="") as f:
            f.write(hedef)
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass

        os.replace(temp_path, path_obj)

        # doğrulama
        okunan = read_text(path_obj)
        if _hash_text(okunan) != hedef_hash:
            raise DosyaServisiHatasi("Yazma doğrulaması başarısız.")

    except Exception as exc:
        try:
            if temp_path.exists():
                temp_path.unlink()
        except Exception:
            pass

        raise DosyaServisiHatasi(
            f"Dosya yazılamadı: {path_obj}"
        ) from exc


# =========================================================
# BACKUP
# =========================================================
def backup_file(file_path: str | Path) -> str:
    path_obj = _normalize_path(file_path)

    if not _path_exists(path_obj):
        raise DosyaServisiHatasi(f"Dosya yok: {path_obj}")

    if not _path_is_file(path_obj):
        raise DosyaServisiHatasi(f"Geçerli dosya değil: {path_obj}")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path_obj.with_name(f"{path_obj.name}.{ts}.bak")

    try:
        shutil.copy2(path_obj, backup_path)
    except Exception as exc:
        raise DosyaServisiHatasi(
            f"Yedek alınamadı: {backup_path}"
        ) from exc

    return str(backup_path)


# =========================================================
# UTILS
# =========================================================
def exists(file_path: str | Path) -> bool:
    try:
        p = _normalize_path(file_path)
        return _path_exists(p) and _path_is_file(p)
    except Exception:
        return False


def get_display_name(file_path: str | Path) -> str:
    try:
        return _normalize_path(file_path).name
    except Exception:
        return ""


# =========================================================
# ROOT HELPERS
# =========================================================
def get_app_working_root() -> Path:
    root = _uygulama_veri_koku() / "app_working_imports"
    root.mkdir(parents=True, exist_ok=True)
    return root


def get_app_backups_root() -> Path:
    root = _uygulama_veri_koku() / "app_document_backups"
    root.mkdir(parents=True, exist_ok=True)
    return root
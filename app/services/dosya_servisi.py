# -*- coding: utf-8 -*-
"""
DOSYA: app/services/dosya_servisi.py

ROL:
- Metin dosyalarını güvenli biçimde okumak / yazmak
- Gerekirse yedek dosya üretmek
- Android / APK tarafında daha güvenli dosya işlemi sağlamak
- Atomik yazma, yedekleme ve doğrulama ile dosya bozulma riskini azaltmak

NOT:
- Bu servis gerçek uçtan uca şifreleme yapmaz.
- Bunun yerine belgeyi korumak için güvenli dosya işlemi uygular:
  - path doğrulama
  - kontrollü okuma
  - atomik yazma
  - fsync
  - yedekleme
  - yazma sonrası doğrulama
  - geçici dosya temizliği

ANDROID / APK NOTLARI:
- Sistem picker ile seçilen geçici dosyalarla çalışabilir
- Sabit proje kökü veya sabit depolama alanı varsaymaz
- Geçici dosya, normal dosya, güvenli klasör görünümü gibi durumlarda
  path ne geldiyse onunla çalışır

SURUM: 6
TARIH: 2026-03-15
IMZA: FY.
"""

from __future__ import annotations

import hashlib
import os
import shutil
from datetime import datetime
from pathlib import Path


class DosyaServisiHatasi(ValueError):
    """Dosya işlemleri sırasında oluşan kontrollü hata."""


def _normalize_path(file_path: str | Path) -> Path:
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


def _hash_text(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def _ensure_parent_dir_exists(path_obj: Path) -> None:
    parent = path_obj.parent
    if not parent.exists():
        raise DosyaServisiHatasi(f"Hedef klasör bulunamadı: {parent}")
    if not parent.is_dir():
        raise DosyaServisiHatasi(f"Hedef klasör geçerli değil: {parent}")


def _copy_permissions_if_possible(src: Path, dst: Path) -> None:
    try:
        if src.exists():
            shutil.copystat(src, dst)
    except Exception:
        pass


def _cleanup_temp_file(temp_path: Path) -> None:
    try:
        if temp_path.exists():
            temp_path.unlink()
    except Exception:
        pass


def read_text(file_path: str | Path, encoding: str = "utf-8") -> str:
    path_obj = _normalize_path(file_path)

    try:
        if not path_obj.exists():
            raise DosyaServisiHatasi(f"Dosya bulunamadı: {path_obj}")

        if not path_obj.is_file():
            raise DosyaServisiHatasi(f"Geçerli bir dosya değil: {path_obj}")
    except OSError as exc:
        raise DosyaServisiHatasi(f"Dosya erişim hatası: {path_obj}") from exc

    try:
        return path_obj.read_text(encoding=encoding)
    except UnicodeDecodeError as exc:
        raise DosyaServisiHatasi(
            f"Dosya '{encoding}' ile okunamadı: {path_obj}"
        ) from exc
    except OSError as exc:
        raise DosyaServisiHatasi(f"Dosya okunamadı: {path_obj}") from exc


def write_text(file_path: str | Path, content: str, encoding: str = "utf-8") -> None:
    """
    Güvenli yazma akışı:

    1) hedef yolu doğrula
    2) geçici dosyaya yaz
    3) flush + fsync
    4) izinleri mümkünse koru
    5) os.replace ile atomik değiştir
    6) tekrar okuyup içerik doğrula
    """
    path_obj = _normalize_path(file_path)

    try:
        if path_obj.exists() and not path_obj.is_file():
            raise DosyaServisiHatasi(f"Geçerli bir dosya değil: {path_obj}")
    except OSError as exc:
        raise DosyaServisiHatasi(f"Dosya erişim hatası: {path_obj}") from exc

    _ensure_parent_dir_exists(path_obj)

    temp_path = _build_temp_path(path_obj)
    target_text = str(content or "")
    target_hash = _hash_text(target_text)

    try:
        with open(temp_path, "w", encoding=encoding, newline="") as f:
            f.write(target_text)
            f.flush()
            os.fsync(f.fileno())

        _copy_permissions_if_possible(path_obj, temp_path)

        os.replace(str(temp_path), str(path_obj))

        # Mümkünse klasör metadata'sını da senkronla
        try:
            dir_fd = os.open(str(path_obj.parent), os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except Exception:
            pass

        # Son doğrulama
        try:
            written_text = path_obj.read_text(encoding=encoding)
        except Exception as exc:
            raise DosyaServisiHatasi(
                f"Dosya yazıldı ancak doğrulama için tekrar okunamadı: {path_obj}"
            ) from exc

        written_hash = _hash_text(written_text)
        if written_hash != target_hash:
            raise DosyaServisiHatasi(
                f"Dosya yazma doğrulaması başarısız oldu: {path_obj}"
            )

    except DosyaServisiHatasi:
        _cleanup_temp_file(temp_path)
        raise
    except Exception as exc:
        _cleanup_temp_file(temp_path)
        raise DosyaServisiHatasi(f"Dosya yazılamadı: {path_obj}") from exc


def backup_file(file_path: str | Path) -> str:
    """
    Hedef dosyanın güvenli yedeğini alır.
    Aynı isimde .bak varsa zaman damgalı yeni yedek üretir.
    """
    path_obj = _normalize_path(file_path)

    try:
        if not path_obj.exists():
            raise DosyaServisiHatasi(f"Yedek alınacak dosya bulunamadı: {path_obj}")

        if not path_obj.is_file():
            raise DosyaServisiHatasi(f"Geçerli bir dosya değil: {path_obj}")
    except OSError as exc:
        raise DosyaServisiHatasi(f"Dosya erişim hatası: {path_obj}") from exc

    backup_path = _build_backup_path(path_obj)

    try:
        shutil.copy2(path_obj, backup_path)
    except Exception as exc:
        raise DosyaServisiHatasi(f"Yedek dosya oluşturulamadı: {backup_path}") from exc

    return str(backup_path)


def safe_write_with_backup(
    file_path: str | Path,
    content: str,
    encoding: str = "utf-8",
) -> str:
    """
    Önce yedek alır, sonra güvenli yazma yapar.
    Başarılıysa yedek yolunu döner.
    """
    backup_path = backup_file(file_path)
    write_text(file_path, content, encoding=encoding)
    return backup_path


def exists(file_path: str | Path) -> bool:
    try:
        return _normalize_path(file_path).is_file()
    except Exception:
        return False


def is_writable_file(file_path: str | Path) -> bool:
    """
    Dosya mevcutsa yazılabilir mi kontrol etmeye çalışır.
    Dosya yoksa parent klasör yazılabilir mi bakar.
    """
    try:
        path_obj = _normalize_path(file_path)

        if path_obj.exists():
            return path_obj.is_file() and os.access(str(path_obj), os.W_OK)

        parent = path_obj.parent
        return parent.exists() and parent.is_dir() and os.access(str(parent), os.W_OK)
    except Exception:
        return False

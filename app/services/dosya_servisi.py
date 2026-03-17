# -*- coding: utf-8 -*-
"""
DOSYA: app/services/dosya_servisi.py

ROL:
- Yerel dosya sistemi üzerinden metin okumak ve yazmak
- Yedek dosya oluşturmak
- Uygulama içi çalışma ve yedek klasörlerini üretmek

MİMARİ:
- Bu servis path tabanlı çalışır
- Android content:// URI kaynakları için kullanılmaz
- Android document/SAF işlemleri android_uri_servisi üzerinden yürütülmelidir

API UYUMLULUK DEĞERLENDİRMESİ:
- Bu servis doğrudan Android API çağrısı yapmaz
- Yerel dosya sistemi ve uygulama içi çalışma alanı için uygundur
- API 34 hedefinde Android dışı/dahili path işlemleri için güvenli hale getirilmiştir
- Android dış kaynak erişiminde bu servis yerine URI tabanlı servis kullanılmalıdır

SURUM: 2
TARIH: 2026-03-17
IMZA: FY.
"""

from __future__ import annotations

import hashlib
import os
import shutil
from datetime import datetime
from pathlib import Path

from kivy.utils import platform


class DosyaServisiHatasi(ValueError):
    """Yerel dosya işlemleri sırasında oluşan kontrollü hata."""


def _normalize_path(file_path: str | Path) -> Path:
    """
    Girilen yolu Path nesnesine çevirir.

    API 34 uyumluluk notu:
    - Bu servis yalnızca path tabanlı yerel dosyalar için tasarlanmıştır.
    - content:// gibi URI kaynakları bu serviste desteklenmez.
    """
    raw = str(file_path or "").strip()
    if not raw:
        raise DosyaServisiHatasi("Dosya yolu boş.")

    if raw.startswith("content://"):
        raise DosyaServisiHatasi(
            "content:// URI bu serviste kullanılamaz. Android URI servisi kullanılmalıdır."
        )

    return Path(raw)


def _hash_text(text: str) -> str:
    """
    Metnin sha256 özetini üretir.
    """
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
    """
    Yedek dosya yolu üretir.
    """
    default_backup = path_obj.with_suffix(path_obj.suffix + ".bak")
    if not default_backup.exists():
        return default_backup

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return path_obj.with_name(f"{path_obj.name}.{ts}.bak")


def _build_temp_path(path_obj: Path) -> Path:
    """
    Geçici dosya yolu üretir.
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return path_obj.with_name(f".{path_obj.name}.{ts}.tmp")


def _ensure_parent_dir_exists(path_obj: Path) -> None:
    """
    Hedef dosyanın üst klasörünün var ve geçerli olduğunu doğrular.
    """
    parent = path_obj.parent
    if not _path_exists(parent):
        raise DosyaServisiHatasi(f"Hedef klasör bulunamadı: {parent}")
    if not _path_is_dir(parent):
        raise DosyaServisiHatasi(f"Hedef klasör geçerli değil: {parent}")


def _cleanup_temp_file(temp_path: Path) -> None:
    """
    Geçici dosyayı güvenli biçimde silmeye çalışır.
    """
    try:
        if _path_exists(temp_path):
            temp_path.unlink()
    except Exception:
        pass


def _uygulama_veri_koku() -> Path:
    """
    Uygulamanın yerel veri kökünü döndürür.

    Android:
    - Göreli/uygulama içi görünür bir kök klasör kullanılır
    - Bu servis Android dış depolama erişimi için değil, yerel çalışma alanı için tasarlanmıştır

    Masaüstü/Python:
    - önce cwd
    - sonra home
    - son fallback: göreli klasör

    API 34 uyumluluk notu:
    - Bu kök yalnızca uygulamanın yerel çalışma ve yedek alanı içindir.
    - Android dış belge erişimi burada değil URI servisinde çözülmelidir.
    """
    adaylar = []

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


def read_text(file_path: str | Path, encoding: str = "utf-8") -> str:
    """
    Yerel path tabanlı bir dosyayı metin olarak okur.

    API 34 uyumluluk notu:
    - content:// URI için kullanılmaz.
    """
    path_obj = _normalize_path(file_path)

    if not _path_exists(path_obj):
        raise DosyaServisiHatasi(f"Dosya bulunamadı: {path_obj}")

    if not _path_is_file(path_obj):
        raise DosyaServisiHatasi(f"Geçerli bir dosya değil: {path_obj}")

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
    Yerel path tabanlı bir dosyaya güvenli biçimde metin yazar.

    İş akışı:
    - temp dosya oluştur
    - içeriği temp dosyaya yaz
    - fsync dene
    - os.replace ile atomik değiştir
    - hash ile doğrula

    API 34 uyumluluk notu:
    - Bu yazma işlemi uygulamanın yerel alanı ve path tabanlı dosyalar içindir.
    """
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
            try:
                os.fsync(f.fileno())
            except Exception:
                pass

        os.replace(str(temp_path), str(path_obj))

        dogrula = path_obj.read_text(encoding=encoding)
        if _hash_text(dogrula) != hedef_hash:
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
    Verilen yerel dosyanın yedeğini alır.

    API 34 uyumluluk notu:
    - Yalnızca path tabanlı yerel dosyalar için kullanılır.
    """
    path_obj = _normalize_path(file_path)

    if not _path_exists(path_obj):
        raise DosyaServisiHatasi(f"Yedek alınacak dosya bulunamadı: {path_obj}")

    if not _path_is_file(path_obj):
        raise DosyaServisiHatasi(f"Geçerli bir dosya değil: {path_obj}")

    backup_path = _build_backup_path(path_obj)

    try:
        shutil.copy2(path_obj, backup_path)
    except Exception as exc:
        raise DosyaServisiHatasi(
            f"Yedek dosya oluşturulamadı: {backup_path}"
        ) from exc

    return str(backup_path)


def exists(file_path: str | Path) -> bool:
    """
    Verilen path'in var olan bir dosya olup olmadığını döndürür.
    """
    try:
        path_obj = _normalize_path(file_path)
        return _path_exists(path_obj) and _path_is_file(path_obj)
    except Exception:
        return False


def get_display_name(file_path: str | Path) -> str:
    """
    Verilen path'in dosya adını döndürür.
    """
    try:
        return _normalize_path(file_path).name
    except Exception:
        return ""


def get_app_working_root() -> Path:
    """
    Uygulamanın yerel çalışma kopyaları kökünü döndürür.

    API 34 uyumluluk notu:
    - Yerel çalışma dosyaları için güvenli uygulama alanı üretir.
    """
    root = _uygulama_veri_koku() / "app_working_imports"
    root.mkdir(parents=True, exist_ok=True)
    return root


def get_app_backups_root() -> Path:
    """
    Uygulamanın yerel yedek klasörü kökünü döndürür.

    API 34 uyumluluk notu:
    - Yedekler uygulamanın kontrol ettiği yerel alanda tutulur.
    """
    root = _uygulama_veri_koku() / "app_document_backups"
    root.mkdir(parents=True, exist_ok=True)
    return root
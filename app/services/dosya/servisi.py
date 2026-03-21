# -*- coding: utf-8 -*-
"""
DOSYA: app/services/dosya/servisi.py

ROL:
- Path tabanlı dosya okuma / yazma / varlık kontrolü
- Uygulama çalışma ve yedek köklerini üretme
- Yerel dosya sistemi işlemlerini güvenli ve doğrulanabilir şekilde yürütme

MİMARİ:
- Sadece path tabanlı yerel dosya sistemiyle çalışır
- content:// URI bu serviste desteklenmez
- Android SAF/URI işlemleri android/uri_servisi katmanında kalır
- Atomic write + doğrulama yaklaşımı kullanır
- Uygulama veri kökleri kontrollü fallback mantığıyla hazırlanır

API UYUMLULUK:
- API 35 uyumlu
- Scoped storage ile çakışmaz
- AndroidX yapısından bağımsız çalışır
- APK / AAB davranış farkını azaltmak için güvenli yazılabilir kök seçer

SURUM: 10
TARIH: 2026-03-19
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
    """Dosya servisi işlemleri sırasında oluşan kontrollü hata."""


# =========================================================
# DEBUG
# =========================================================
def _debug(message: str) -> None:
    try:
        print("[DOSYA_SERVISI]", str(message))
    except Exception:
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


def _ensure_dir(path_obj: Path) -> Path:
    try:
        path_obj.mkdir(parents=True, exist_ok=True)
        return path_obj
    except Exception as exc:
        raise DosyaServisiHatasi(
            f"Klasör oluşturulamadı: {path_obj}"
        ) from exc


def _assert_dir_writable(path_obj: Path) -> Path:
    """
    Klasörün yazılabilir olduğunu test eder.
    """
    try:
        _ensure_dir(path_obj)

        test_file = path_obj / f".write_test_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.tmp"
        test_file.write_text("ok", encoding="utf-8")
        try:
            test_file.unlink(missing_ok=True)
        except TypeError:
            if test_file.exists():
                test_file.unlink()

        return path_obj
    except Exception as exc:
        raise DosyaServisiHatasi(
            f"Klasör yazılabilir değil: {path_obj}"
        ) from exc


# =========================================================
# HASH
# =========================================================
def _hash_text(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def _hash_path(path_obj: Path) -> str:
    return hashlib.sha1(str(path_obj).encode("utf-8")).hexdigest()[:10]


# =========================================================
# ROOT
# =========================================================
def _candidate_data_roots() -> list[Path]:
    """
    Uygulama veri kökü için olası adayları öncelik sırasıyla üretir.
    """
    adaylar: list[Path] = []

    if platform == "android":
        try:
            android_private = str(os.environ.get("ANDROID_PRIVATE", "") or "").strip()
            if android_private:
                adaylar.append(Path(android_private))
        except Exception:
            pass

        try:
            app_storage = str(os.environ.get("APP_STORAGE_PATH", "") or "").strip()
            if app_storage:
                adaylar.append(Path(app_storage))
        except Exception:
            pass

    try:
        adaylar.append(Path.home())
    except Exception:
        pass

    try:
        adaylar.append(Path.cwd())
    except Exception:
        pass

    uniq: list[Path] = []
    seen: set[str] = set()

    for aday in adaylar:
        key = str(aday).strip()
        if key and key not in seen:
            uniq.append(aday)
            seen.add(key)

    return uniq


def _uygulama_veri_koku() -> Path:
    """
    Yazılabilir ilk uygulama veri kökünü döndürür.

    Öncelik:
    1) Android private app alanı
    2) APP_STORAGE_PATH
    3) home
    4) cwd
    """
    hatalar: list[str] = []

    for aday in _candidate_data_roots():
        try:
            if not _path_exists(aday):
                aday.mkdir(parents=True, exist_ok=True)

            if not _path_is_dir(aday):
                raise ValueError("Dizin değil")

            root = aday / "fonksiyon_degistirici_veri"
            _assert_dir_writable(root)
            return root
        except Exception as exc:
            hatalar.append(f"{aday} -> {exc}")

    try:
        root = Path("fonksiyon_degistirici_veri")
        _assert_dir_writable(root)
        return root
    except Exception as exc:
        raise DosyaServisiHatasi(
            "Uygulama veri kökü hazırlanamadı. Denenen yollar:\n"
            + "\n".join(hatalar + [f"relative -> {exc}"])
        ) from exc


# =========================================================
# READ
# =========================================================
def read_text(file_path: str | Path, encoding: str = "utf-8") -> str:
    path_obj = _normalize_path(file_path)

    if not _path_exists(path_obj):
        raise DosyaServisiHatasi(f"Dosya bulunamadı: {path_obj}")

    if not _path_is_file(path_obj):
        raise DosyaServisiHatasi(f"Geçerli bir dosya değil: {path_obj}")

    denenecek_encodingler: list[str] = []
    for enc in [encoding, "utf-8", "utf-8-sig", "latin-1"]:
        temiz = str(enc or "").strip()
        if temiz and temiz not in denenecek_encodingler:
            denenecek_encodingler.append(temiz)

    son_hata: Exception | None = None

    for enc in denenecek_encodingler:
        try:
            return path_obj.read_text(encoding=enc)
        except UnicodeDecodeError as exc:
            son_hata = exc
            continue
        except Exception as exc:
            raise DosyaServisiHatasi(
                f"Dosya okunamadı: {path_obj}"
            ) from exc

    raise DosyaServisiHatasi(
        f"Dosya okunamadı (encoding): {path_obj}"
    ) from son_hata


# =========================================================
# WRITE
# =========================================================
def write_text(file_path: str | Path, content: str, encoding: str = "utf-8") -> None:
    path_obj = _normalize_path(file_path)

    if _path_exists(path_obj) and not _path_is_file(path_obj):
        raise DosyaServisiHatasi(f"Geçerli dosya değil: {path_obj}")

    parent = path_obj.parent
    try:
        _assert_dir_writable(parent)
    except DosyaServisiHatasi:
        raise
    except Exception as exc:
        raise DosyaServisiHatasi(
            f"Hedef klasör hazırlanamadı: {parent}"
        ) from exc

    temp_path = parent / (
        f".{path_obj.name}.{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.tmp"
    )

    hedef = str(content or "")
    hedef_hash = _hash_text(hedef)

    try:
        with open(temp_path, "w", encoding=encoding, newline="") as file_obj:
            file_obj.write(hedef)
            file_obj.flush()
            try:
                os.fsync(file_obj.fileno())
            except Exception:
                pass

        os.replace(temp_path, path_obj)

        okunan = read_text(path_obj, encoding=encoding)
        if _hash_text(okunan) != hedef_hash:
            raise DosyaServisiHatasi("Yazma doğrulaması başarısız.")

    except Exception as exc:
        try:
            if temp_path.exists():
                temp_path.unlink()
        except Exception:
            pass

        if isinstance(exc, DosyaServisiHatasi):
            raise

        raise DosyaServisiHatasi(
            f"Dosya yazılamadı: {path_obj}"
        ) from exc


# =========================================================
# BACKUP
# =========================================================
def backup_file(file_path: str | Path) -> str:
    """
    Verilen yerel dosyanın yedeğini uygulama içi güvenli yedek klasörüne alır.
    """
    path_obj = _normalize_path(file_path)

    if not _path_exists(path_obj):
        raise DosyaServisiHatasi(f"Dosya yok: {path_obj}")

    if not _path_is_file(path_obj):
        raise DosyaServisiHatasi(f"Geçerli dosya değil: {path_obj}")

    try:
        backup_root = get_app_backups_root()
    except Exception as exc:
        raise DosyaServisiHatasi(
            f"Yedek klasörü hazırlanamadı: {exc}"
        ) from exc

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    yol_hash = _hash_path(path_obj)
    guvenli_ad = path_obj.name.replace("/", "_").replace("\\", "_")
    backup_name = f"{guvenli_ad}.{yol_hash}.{ts}.bak"
    backup_path = backup_root / backup_name

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
        path_obj = _normalize_path(file_path)
        return _path_exists(path_obj) and _path_is_file(path_obj)
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
    """
    Uygulama içi çalışma kopyalarının tutulacağı kökü döndürür.
    """
    try:
        root = _uygulama_veri_koku() / "app_working_imports"
        return _assert_dir_writable(root)
    except Exception as exc:
        raise DosyaServisiHatasi(
            f"Çalışma kökü hazırlanamadı: {exc}"
        ) from exc


def get_app_backups_root() -> Path:
    """
    Uygulama içi yedeklerin tutulacağı kökü döndürür.
    """
    try:
        root = _uygulama_veri_koku() / "app_document_backups"
        return _assert_dir_writable(root)
    except Exception as exc:
        raise DosyaServisiHatasi(
            f"Yedek kökü hazırlanamadı: {exc}"
        ) from exc
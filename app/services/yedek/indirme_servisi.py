# -*- coding: utf-8 -*-
"""
DOSYA: app/services/yedek/indirme_servisi.py

ROL:
- Mevcut bir yedek dosyasını kullanıcı tarafından seçilen hedefe kopyalamak
- Gerekirse varsayılan erişilebilir hedefe fallback yapmak
- Çakışan dosya adlarında güvenli hedef üretmek

MİMARİ:
- Kaynak yalnızca path tabanlı yerel yedek dosyasıdır
- Hedef klasör kullanıcı seçimi veya varsayılan kök olabilir
- Önce binary kopyalama denenir
- Gerekirse text tabanlı güvenli fallback uygulanır

API UYUMLULUK:
- API 35 uyumlu
- Scoped storage ile çakışmaz
- Uygulama içi ve erişilebilir ortak hedefleri destekler

SURUM: 4
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from kivy.utils import platform

from app.services.dosya.servisi import (
    DosyaServisiHatasi,
    get_app_backups_root,
    read_text,
    write_text,
)


class YedekIndirmeServisiHatasi(ValueError):
    """Yedek indirme/kopyalama sırasında oluşan kontrollü hata."""


def _normalize_path(path_value: str | Path) -> Path:
    try:
        raw = str(path_value or "").strip()
    except Exception as exc:
        raise YedekIndirmeServisiHatasi(
            f"Geçersiz yol: {exc}"
        ) from exc

    if not raw:
        raise YedekIndirmeServisiHatasi("Yol boş.")

    return Path(raw)


def _candidate_download_roots() -> list[Path]:
    """
    Olası varsayılan indirme hedeflerini öncelik sırasıyla üretir.

    Öncelik:
    1) Android ortak Download/FonksiyonDegistirici
    2) Uygulamanın güvenli alanında downloads
    3) Android dışı cwd/indirilen_yedekler
    """
    roots: list[Path] = []

    if platform == "android":
        roots.append(Path("/storage/emulated/0/Download/FonksiyonDegistirici"))

        try:
            roots.append(get_app_backups_root() / "downloads")
        except Exception:
            pass
    else:
        roots.append(Path.cwd() / "indirilen_yedekler")

        try:
            roots.append(get_app_backups_root() / "downloads")
        except Exception:
            pass

    uniq: list[Path] = []
    seen: set[str] = set()

    for root in roots:
        key = str(root)
        if key not in seen:
            uniq.append(root)
            seen.add(key)

    return uniq


def _assert_dir_writable(root: Path) -> Path:
    """
    Klasörün yazılabilir olduğunu doğrular.
    """
    try:
        root.mkdir(parents=True, exist_ok=True)

        test_file = root / ".write_test.tmp"
        test_file.write_text("ok", encoding="utf-8")
        try:
            test_file.unlink(missing_ok=True)
        except TypeError:
            if test_file.exists():
                test_file.unlink()

        return root
    except Exception as exc:
        raise YedekIndirmeServisiHatasi(
            f"Hedef klasör yazılabilir değil: {root}"
        ) from exc


def _download_root() -> Path:
    """
    Yazılabilir ilk varsayılan indirme kökünü bulur.
    """
    hatalar: list[str] = []

    for root in _candidate_download_roots():
        try:
            return _assert_dir_writable(root)
        except Exception as exc:
            hatalar.append(f"{root} -> {exc}")

    raise YedekIndirmeServisiHatasi(
        "İndirme klasörü hazırlanamadı. Denenen yollar:\n" + "\n".join(hatalar)
    )


def _unique_target(root: Path, file_name: str) -> Path:
    """
    Aynı isimli dosya varsa çakışmayı önlemek için benzersiz hedef üretir.
    """
    hedef = root / file_name
    if not hedef.exists():
        return hedef

    stem = hedef.stem
    suffix = hedef.suffix
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return root / f"{stem}.{ts}{suffix}"


def _copy_backup_file(kaynak: Path, hedef: Path) -> str:
    """
    Önce binary kopyalama, gerekirse text tabanlı fallback dener.
    """
    try:
        shutil.copy2(kaynak, hedef)
        return str(hedef)
    except Exception:
        pass

    try:
        icerik = read_text(kaynak)
        write_text(hedef, icerik)
        return str(hedef)
    except (DosyaServisiHatasi, Exception) as exc:
        raise YedekIndirmeServisiHatasi(
            f"Yedek indirilemedi: {exc}"
        ) from exc


def yedegi_indir(backup_path: str | Path, hedef_klasor: str | Path) -> str:
    """
    Verilen yedek dosyasını kullanıcı tarafından seçilen hedef klasöre kopyalar.

    Geri dönüş:
    - hedef dosya yolu
    """
    kaynak = _normalize_path(backup_path)

    if not kaynak.exists() or not kaynak.is_file():
        raise YedekIndirmeServisiHatasi("İndirilecek yedek dosya bulunamadı.")

    hedef_root = _normalize_path(hedef_klasor)

    try:
        hedef_root = _assert_dir_writable(hedef_root)
        hedef = _unique_target(hedef_root, kaynak.name)
    except YedekIndirmeServisiHatasi:
        raise
    except Exception as exc:
        raise YedekIndirmeServisiHatasi(
            f"Hedef klasör hazırlanamadı: {exc}"
        ) from exc

    return _copy_backup_file(kaynak, hedef)


def yedegi_indir_varsayilan(backup_path: str | Path) -> str:
    """
    Verilen yedek dosyasını varsayılan erişilebilir hedefe kopyalar.

    Geri dönüş:
    - hedef dosya yolu
    """
    kaynak = _normalize_path(backup_path)

    if not kaynak.exists() or not kaynak.is_file():
        raise YedekIndirmeServisiHatasi("İndirilecek yedek dosya bulunamadı.")

    try:
        hedef_root = _download_root()
        hedef = _unique_target(hedef_root, kaynak.name)
    except YedekIndirmeServisiHatasi:
        raise
    except Exception as exc:
        raise YedekIndirmeServisiHatasi(
            f"Hedef klasör hazırlanamadı: {exc}"
        ) from exc

    return _copy_backup_file(kaynak, hedef)
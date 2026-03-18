# -*- coding: utf-8 -*-
from __future__ import annotations

import shutil
from pathlib import Path

from kivy.utils import platform

from app.services.dosya_servisi import read_text, write_text


class YedekIndirmeServisiHatasi(ValueError):
    pass


def _download_root() -> Path:
    if platform == "android":
        root = Path("/storage/emulated/0/Download/FonksiyonDegistirici")
    else:
        root = Path.cwd() / "indirilen_yedekler"

    root.mkdir(parents=True, exist_ok=True)
    return root


def yedegi_indir(backup_path: str | Path) -> str:
    kaynak = Path(str(backup_path or "").strip())
    if not kaynak.exists() or not kaynak.is_file():
        raise YedekIndirmeServisiHatasi("İndirilecek yedek dosya bulunamadı.")

    hedef = _download_root() / kaynak.name

    try:
        shutil.copy2(kaynak, hedef)
        return str(hedef)
    except Exception:
        try:
            icerik = read_text(kaynak)
            write_text(hedef, icerik)
            return str(hedef)
        except Exception as exc:
            raise YedekIndirmeServisiHatasi(
                f"Yedek indirilemedi: {exc}"
            ) from exc
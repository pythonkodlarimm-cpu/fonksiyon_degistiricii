# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/helpers.py

ROL:
- Dosya seçici için varsayılan başlangıç klasörünü belirlemek

MİMARİ:
- UI katmanı için saf yardımcı (stateless)
- Yönetici (yoneticisi.py) tarafından dolaylı kullanılır
- Platform bağımsız fallback zinciri içerir

API 34 UYUMLULUK:
- Android SAF kısıtları dikkate alınır
- Önce app-private alan, sonra public storage denenir
- Her zaman güvenli fallback garanti edilir

SURUM: 2
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path
from kivy.utils import platform


def _safe_dir(p: Path) -> Path | None:
    try:
        if p.exists() and p.is_dir():
            try:
                return p.resolve()
            except Exception:
                return p
    except Exception:
        pass
    return None


def varsayilan_baslangic_klasoru() -> Path:
    """
    Dosya seçici için başlangıç klasörü.

    Öncelik sırası:
    1. Android app-private storage
    2. Android public storage (/storage/emulated/0)
    3. Home
    4. CWD
    5. "." fallback
    """

    adaylar: list[Path] = []

    if platform == "android":
        try:
            from app.services.android_uri_servisi import get_app_files_dir

            app_dir = get_app_files_dir()
            if app_dir:
                adaylar.append(Path(app_dir))
        except Exception:
            pass

        adaylar.extend([
            Path("/storage/emulated/0"),
            Path("/sdcard"),
        ])

    adaylar.extend([
        Path.home(),
        Path.cwd(),
    ])

    for aday in adaylar:
        sonuc = _safe_dir(aday)
        if sonuc is not None:
            return sonuc

    try:
        return Path.cwd().resolve()
    except Exception:
        return Path(".")
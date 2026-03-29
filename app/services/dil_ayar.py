# -*- coding: utf-8 -*-
"""
DOSYA: app/services/dil_ayar.py

ROL:
- Seçilen dili kalıcı olarak saklar
- Uygulama açıldığında dili geri yükler
- Basit ve güvenli ayar yönetimi sağlar

MİMARİ:
- File-based storage (JSON)
- Atomic write
- Fail-safe read
- Tek sorumluluk

API UYUMLULUK:
- Android API 35 uyumlu
- Pydroid3 / masaüstü uyumlu

SURUM: 1
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Final


DEFAULT_LANG: Final[str] = "en"


def _ayar_dosyasi() -> Path:
    base = Path("/storage/emulated/0/FonksiyonDegistirici/settings")
    base.mkdir(parents=True, exist_ok=True)
    return base / "lang.json"


def dili_kaydet(lang_code: str) -> None:
    path = _ayar_dosyasi()

    data = {
        "lang": str(lang_code or "").strip().lower(),
    }

    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(str(tmp), str(path))


def kayitli_dili_getir() -> str:
    path = _ayar_dosyasi()

    if not path.exists():
        return DEFAULT_LANG

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_LANG

    lang = data.get("lang")

    if not isinstance(lang, str) or not lang.strip():
        return DEFAULT_LANG

    return lang.strip().lower()
# -*- coding: utf-8 -*-
"""
DOSYA: app/services/sistem/ayar_servisi.py

ROL:
- Uygulama ayarlarını yüklemek / kaydetmek
- Şimdilik dil ayarını saklamak
- Uygulama içi güvenli ayar dosyasını yönetmek

MİMARİ:
- Ayar dosyası uygulama veri alanında tutulur
- JSON tabanlı sade ayar yapısı kullanılır
- Bozuk içerikte kontrollü hata veya güvenli fallback döner

API UYUMLULUK:
- API 35 uyumlu
- Scoped storage dostu
- Android ve masaüstü ortamlarında güvenli çalışır

SURUM: 2
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.services.dosya.servisi import get_app_working_root


class AyarServisiHatasi(ValueError):
    pass


def _ayar_dosyasi() -> Path:
    try:
        root = get_app_working_root() / "ayarlar"
        root.mkdir(parents=True, exist_ok=True)
        return root / "settings.json"
    except Exception as exc:
        raise AyarServisiHatasi(
            f"Ayar dosyası yolu hazırlanamadı: {exc}"
        ) from exc


def ayarlari_yukle() -> dict:
    path = _ayar_dosyasi()

    if not path.exists():
        return {}

    try:
        raw = path.read_text(encoding="utf-8").strip()
        if not raw:
            return {}

        data = json.loads(raw)
        if not isinstance(data, dict):
            raise AyarServisiHatasi("Ayar dosyası sözlük formatında değil.")
        return data
    except AyarServisiHatasi:
        raise
    except Exception as exc:
        raise AyarServisiHatasi(f"Ayarlar okunamadı: {exc}") from exc


def ayarlari_kaydet(data: dict) -> None:
    path = _ayar_dosyasi()

    try:
        payload = data if isinstance(data, dict) else {}
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as exc:
        raise AyarServisiHatasi(f"Ayarlar kaydedilemedi: {exc}") from exc


def get_language(default: str = "tr") -> str:
    try:
        data = ayarlari_yukle()
        code = str(data.get("language", default) or default).strip().lower()
        return code or default
    except Exception:
        return default


def set_language(code: str) -> None:
    temiz = str(code or "").strip().lower() or "tr"

    try:
        data = ayarlari_yukle()
    except Exception:
        data = {}

    data["language"] = temiz
    ayarlari_kaydet(data)
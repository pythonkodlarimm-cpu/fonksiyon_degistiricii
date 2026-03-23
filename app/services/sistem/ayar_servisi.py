# -*- coding: utf-8 -*-
"""
DOSYA: app/services/sistem/ayar_servisi.py

ROL:
- Uygulama ayarlarını yüklemek / kaydetmek
- Dil ayarını saklamak
- Desteklenen dil kodlarını merkezi olarak yönetmek
- Uygulama durumunu (app_state) saklamak
- Uygulama içi güvenli ayar dosyasını yönetmek

MİMARİ:
- Ayar dosyası uygulama veri alanında tutulur
- JSON tabanlı sade ayar yapısı kullanılır
- Bozuk içerikte kontrollü hata veya güvenli fallback döner
- Dil ve uygulama durumu aynı settings.json içinde tutulur
- Dil doğrulama tek merkezde yapılır
- UI katmanı doğrudan settings.json yapısını bilmez

API UYUMLULUK:
- API 35 uyumlu
- Scoped storage dostu
- Android ve masaüstü ortamlarında güvenli çalışır

SURUM: 5
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.services.dosya.servisi import get_app_working_root


class AyarServisiHatasi(ValueError):
    pass


# =========================================================
# DIL AYARLARI
# =========================================================
DEFAULT_LANGUAGE: str = "tr"

SUPPORTED_LANGUAGES: tuple[str, ...] = (
    "tr",
    "en",
    "de",
    "fr",
    "es",
    "it",
    "pt",
    "pt-br",
    "nl",
    "ru",
    "uk",
    "pl",
    "cs",
    "sk",
    "sl",
    "hr",
    "sr",
    "bs",
    "mk",
    "bg",
    "ro",
    "hu",
    "el",
    "sq",
    "da",
    "sv",
    "no",
    "fi",
    "is",
    "et",
    "lv",
    "lt",
    "ga",
    "mt",
    "cy",
    "ca",
    "eu",
    "gl",
    "af",
    "sw",
    "zu",
    "xh",
    "am",
    "ar",
    "fa",
    "ur",
    "he",
    "hi",
    "bn",
    "ta",
    "te",
    "ml",
    "kn",
    "gu",
    "mr",
    "pa",
    "or",
    "as",
    "ne",
    "si",
    "my",
    "th",
    "vi",
    "id",
    "ms",
    "tl",
    "zh",
    "zh-cn",
    "zh-tw",
    "ja",
    "ko",
)


def _ayar_dosyasi() -> Path:
    try:
        root = get_app_working_root() / "ayarlar"
        root.mkdir(parents=True, exist_ok=True)
        return root / "settings.json"
    except Exception as exc:
        raise AyarServisiHatasi(
            f"Ayar dosyası yolu hazırlanamadı: {exc}"
        ) from exc


def _normalize_language_code(code: str | None, default: str = DEFAULT_LANGUAGE) -> str:
    temiz = str(code or "").strip().lower()
    fallback = str(default or DEFAULT_LANGUAGE).strip().lower() or DEFAULT_LANGUAGE

    if not temiz:
        return fallback

    temiz = temiz.replace("_", "-")

    if temiz in SUPPORTED_LANGUAGES:
        return temiz

    # dil-bölge kodundan ana dil çıkarımı
    if "-" in temiz:
        kok = temiz.split("-", 1)[0].strip()
        if kok in SUPPORTED_LANGUAGES:
            return kok

    return fallback


def supported_languages() -> list[str]:
    return list(SUPPORTED_LANGUAGES)


def language_supported(code: str) -> bool:
    temiz = str(code or "").strip().lower().replace("_", "-")
    return temiz in SUPPORTED_LANGUAGES


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


def get_language(default: str = DEFAULT_LANGUAGE) -> str:
    fallback = _normalize_language_code(default, DEFAULT_LANGUAGE)

    try:
        data = ayarlari_yukle()
        code = data.get("language", fallback)
        return _normalize_language_code(str(code or ""), fallback)
    except Exception:
        return fallback


def set_language(code: str) -> None:
    temiz = _normalize_language_code(code, DEFAULT_LANGUAGE)

    try:
        data = ayarlari_yukle()
    except Exception:
        data = {}

    data["language"] = temiz
    ayarlari_kaydet(data)


def get_app_state(default: dict | None = None) -> dict:
    try:
        data = ayarlari_yukle()
        fallback = default if isinstance(default, dict) else {}
        state = data.get("app_state", fallback)
        return state if isinstance(state, dict) else fallback
    except Exception:
        return default if isinstance(default, dict) else {}


def set_app_state(state: dict) -> None:
    temiz_state = state if isinstance(state, dict) else {}

    try:
        data = ayarlari_yukle()
    except Exception:
        data = {}

    data["app_state"] = temiz_state
    ayarlari_kaydet(data)


def clear_app_state() -> None:
    try:
        data = ayarlari_yukle()
    except Exception:
        data = {}

    if "app_state" in data:
        del data["app_state"]

    ayarlari_kaydet(data)

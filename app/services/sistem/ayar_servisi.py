# -*- coding: utf-8 -*-
"""
DOSYA: app/services/sistem/ayar_servisi.py

ROL:
- Uygulama ayarlarını yüklemek / kaydetmek
- Dil ayarını saklamak
- diller/ klasöründeki kullanılabilir dil kodlarını otomatik algılamak
- Uygulama durumunu (app_state) saklamak
- Uygulama içi güvenli ayar dosyasını yönetmek

MİMARİ:
- Ayar dosyası uygulama veri alanında tutulur
- JSON tabanlı sade ayar yapısı kullanılır
- Bozuk içerikte kontrollü hata veya güvenli fallback döner
- Dil ve uygulama durumu aynı settings.json içinde tutulur
- Dil doğrulama tek merkezde yapılır
- UI katmanı doğrudan settings.json yapısını bilmez
- Desteklenen diller sabit tuple ile değil, diller klasöründen otomatik keşfedilir
- Yeni bir dil json dosyası eklendiğinde sistem kod değişmeden onu görebilir

API UYUMLULUK:
- API 35 uyumlu
- Scoped storage dostu
- Android ve masaüstü ortamlarında güvenli çalışır

SURUM: 6
TARIH: 2026-03-24
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


def _diller_klasoru() -> Path:
    """
    Bu dosyayla aynı klasördeki diller/ dizinini döndürür.
    """
    return Path(__file__).resolve().parent / "diller"


def _mevcut_dil_kodlarini_tara() -> list[str]:
    """
    diller/ klasöründeki *.json dosyalarından dil kodlarını çıkarır.
    Geçerli json olmayan dosyalar da dosya adı seviyesinde listeye alınır;
    gerçek içerik kontrolü dil_servisi tarafında ayrıca yapılabilir.
    """
    sonuc: list[str] = []
    gorulen: set[str] = set()

    try:
        klasor = _diller_klasoru()
        if not klasor.is_dir():
            return [DEFAULT_LANGUAGE]

        for path in sorted(klasor.glob("*.json")):
            try:
                kod = str(path.stem or "").strip().lower().replace("_", "-")
                if not kod:
                    continue

                if kod not in gorulen:
                    gorulen.add(kod)
                    sonuc.append(kod)
            except Exception:
                continue
    except Exception:
        return [DEFAULT_LANGUAGE]

    if DEFAULT_LANGUAGE not in sonuc:
        sonuc.insert(0, DEFAULT_LANGUAGE)

    return sonuc or [DEFAULT_LANGUAGE]


def _ayar_dosyasi() -> Path:
    try:
        root = get_app_working_root() / "ayarlar"
        root.mkdir(parents=True, exist_ok=True)
        return root / "settings.json"
    except Exception as exc:
        raise AyarServisiHatasi(
            f"Ayar dosyası yolu hazırlanamadı: {exc}"
        ) from exc


def _normalize_language_code(
    code: str | None,
    default: str = DEFAULT_LANGUAGE,
) -> str:
    temiz = str(code or "").strip().lower()
    fallback = str(default or DEFAULT_LANGUAGE).strip().lower() or DEFAULT_LANGUAGE

    if not temiz:
        return fallback

    temiz = temiz.replace("_", "-")

    mevcut_diller = supported_languages()

    if temiz in mevcut_diller:
        return temiz

    # dil-bölge kodundan ana dil çıkarımı
    if "-" in temiz:
        kok = temiz.split("-", 1)[0].strip()
        if kok in mevcut_diller:
            return kok

    return fallback


def supported_languages() -> list[str]:
    return _mevcut_dil_kodlarini_tara()


def language_supported(code: str) -> bool:
    temiz = str(code or "").strip().lower().replace("_", "-")
    if not temiz:
        return False
    return temiz in supported_languages()


# =========================================================
# AYAR OKU / YAZ
# =========================================================
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


# =========================================================
# DIL
# =========================================================
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


# =========================================================
# APP STATE
# =========================================================
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

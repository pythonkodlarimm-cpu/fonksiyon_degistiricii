# -*- coding: utf-8 -*-
"""
DOSYA: app/services/guncelleme/versiyon_kontrol_servisi.py

ROL:
- Uzak version.json dosyasını okuyup uygulama sürümü ile karşılaştırmak
- Yeni sürüm var mı bilgisini üretmek
- Force update ve minimum supported version gibi alanları yorumlamak

MİMARİ:
- UI katmanı bu dosyayı doğrudan bilmez
- Güncelleme yöneticisi üzerinden kullanılır
- Ağ hatalarında güvenli fallback döner

API UYUMLULUK:
- Android API 35 uyumlu
- Platform bağımsızdır
- Kısa timeout ile güvenli çalışır

SURUM: 2
TARIH: 2026-03-23
IMZA: FY.
"""

from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import urlopen

from app.services.guncelleme.ayarlari import (
    GUNCELLEME_BILDIRIM_METNI,
    VERSION_CHECK_TIMEOUT_SECONDS,
    VERSION_JSON_URL,
    play_store_web_url,
)


def _version_tuple(value: str) -> tuple[int, ...]:
    temiz = str(value or "").strip()
    if not temiz:
        return (0,)

    parcalar: list[int] = []

    for parca in temiz.split("."):
        try:
            parcalar.append(int(parca))
        except Exception:
            sayisal = "".join(ch for ch in str(parca) if ch.isdigit())
            parcalar.append(int(sayisal) if sayisal else 0)

    return tuple(parcalar or [0])


def _version_greater(left: str, right: str) -> bool:
    return _version_tuple(left) > _version_tuple(right)


def _version_less(left: str, right: str) -> bool:
    return _version_tuple(left) < _version_tuple(right)


def version_json_indir() -> dict:
    try:
        with urlopen(
            VERSION_JSON_URL,
            timeout=float(VERSION_CHECK_TIMEOUT_SECONDS),
        ) as resp:
            raw = resp.read().decode("utf-8")

        data = json.loads(raw)
        return data if isinstance(data, dict) else {}

    except (URLError, TimeoutError, ValueError, OSError):
        return {}
    except Exception:
        return {}


def guncelleme_durumu_hesapla(mevcut_surum: str) -> dict:
    data = version_json_indir()

    latest_version = str(data.get("latest_version", "") or "").strip()
    min_supported_version = str(
        data.get("min_supported_version", "") or ""
    ).strip()
    force_update = bool(data.get("force_update", False))
    store_url = str(data.get("store_url", "") or "").strip() or play_store_web_url()
    message = str(data.get("message", "") or "").strip() or GUNCELLEME_BILDIRIM_METNI

    mevcut = str(mevcut_surum or "").strip()

    yeni_surume_gecilebilir = False
    destek_disi = False

    if latest_version and mevcut:
        yeni_surume_gecilebilir = _version_greater(latest_version, mevcut)

    if min_supported_version and mevcut:
        destek_disi = _version_less(mevcut, min_supported_version)

    return {
        "ok": bool(data),
        "current_version": mevcut,
        "latest_version": latest_version,
        "min_supported_version": min_supported_version,
        "force_update": force_update,
        "update_available": yeni_surume_gecilebilir,
        "unsupported_version": destek_disi,
        "store_url": store_url,
        "message": message,
    }
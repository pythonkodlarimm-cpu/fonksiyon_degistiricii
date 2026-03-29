# -*- coding: utf-8 -*-
"""
DOSYA: app/services/dil_servisi.py

ROL:
- Dil dosyalarını yükler
- Aktif dili kalıcı olarak kaydeder
- Anahtar bazlı çeviri sağlar
- Mevcut assets/lang yapısını tek kaynak kabul eder

MİMARİ:
- Lazy olmayan net yükleme
- Deterministik davranış
- Tek aktif dil tutulur
- JSON tabanlı dil akışı
- Geriye uyumluluk katmanı içermez

API UYUMLULUK:
- Platform bağımsız
- Android API 35 uyumlu
- Pydroid3 / masaüstü / test ortamı uyumlu

SURUM: 2
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


class DilServisiHatasi(ValueError):
    """
    Dil servisi işlemlerinde oluşan kontrollü hata.
    """


class DilServisi:
    """
    JSON tabanlı dil yükleme ve kayıt servisi.
    """

    __slots__ = (
        "_lang_path",
        "_ayar_dosyasi",
        "_aktif_dil",
        "_veri",
    )

    def __init__(self, lang_path: Path) -> None:
        self._lang_path = Path(lang_path)
        self._ayar_dosyasi = Path(".settings") / "dil.json"
        self._aktif_dil: str = "tr"
        self._veri: dict[str, object] = {}

        self._baslat()

    # =========================================================
    # INTERNAL
    # =========================================================
    def _baslat(self) -> None:
        secili = self._kayitli_dili_oku()
        self._dil_yukle(secili)

    def _kayitli_dili_oku(self) -> str:
        if not self._ayar_dosyasi.exists():
            return "tr"

        try:
            raw = json.loads(self._ayar_dosyasi.read_text(encoding="utf-8"))
            kod = str(raw.get("dil", "tr")).strip().lower()
            return kod or "tr"
        except Exception:
            return "tr"

    def _ayar_kaydet(self, dil_kodu: str) -> None:
        payload = {"dil": dil_kodu}
        tmp = self._ayar_dosyasi.with_suffix(".tmp")

        try:
            self._ayar_dosyasi.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            os.replace(str(tmp), str(self._ayar_dosyasi))
        except Exception as exc:
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass
            raise DilServisiHatasi("Dil ayarı kaydedilemedi.") from exc

    def _dil_dosyasi(self, kod: str) -> Path:
        normalized = str(kod or "").strip().lower()
        if not normalized:
            raise DilServisiHatasi("Dil kodu boş olamaz.")
        return self._lang_path / f"{normalized}.json"

    def _dil_yukle(self, kod: str) -> None:
        dosya = self._dil_dosyasi(kod)

        if not dosya.exists():
            raise DilServisiHatasi(f"Dil dosyası bulunamadı: {dosya}")

        try:
            veri = json.loads(dosya.read_text(encoding="utf-8"))
        except Exception as exc:
            raise DilServisiHatasi(f"Dil dosyası okunamadı: {dosya}") from exc

        if not isinstance(veri, dict):
            raise DilServisiHatasi("Dil dosyası sözlük yapısında olmalıdır.")

        self._veri = veri
        self._aktif_dil = str(kod).strip().lower()

    # =========================================================
    # PUBLIC API
    # =========================================================
    def aktif_dil(self) -> str:
        return self._aktif_dil

    def dil_degistir(self, kod: str) -> None:
        normalized = str(kod or "").strip().lower()
        self._dil_yukle(normalized)
        self._ayar_kaydet(normalized)

    def t(self, key: str, **kwargs) -> str:
        raw_key = str(key or "").strip()
        if not raw_key:
            return ""

        value = self._veri.get(raw_key, raw_key)
        text = str(value)

        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text

        return text

    def tum_diller(self) -> list[dict[str, str]]:
        sonuc: list[dict[str, str]] = []

        if not self._lang_path.exists():
            return sonuc

        for item in sorted(self._lang_path.glob("*.json")):
            try:
                data = json.loads(item.read_text(encoding="utf-8"))
                sonuc.append(
                    {
                        "code": str(data.get("_meta_language_code", item.stem)),
                        "name": str(data.get("_meta_language_name", item.stem)),
                    }
                )
            except Exception:
                continue

        return sonuc
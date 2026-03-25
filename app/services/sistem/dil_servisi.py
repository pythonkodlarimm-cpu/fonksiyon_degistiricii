# -*- coding: utf-8 -*-
"""
DOSYA: app/services/sistem/dil_servisi.py

ROL:
- Uygulamanın dil yükleme ve metin çözümleme akışını yönetmek
- diller/ klasörü içindeki json dosyalarını otomatik algılamak
- Aktif dili bellekte tutmak ve ilgili sözlüğü yüklemek
- Aktif dili ayarlardan yüklemek ve değişince ayarlara kaydetmek
- UI katmanına mevcut diller listesini sunmak
- Eksik anahtarlar için güvenli fallback sağlamak
- Android / APK / AAB ortamında da dil dosyalarını güvenli biçimde bulmak

MİMARİ:
- Dil dosyaları app/services/sistem/diller/ klasöründen otomatik keşfedilir
- Dosya adı dil kodu kabul edilir (tr.json -> tr, en.json -> en)
- Geçersiz / bozuk json dosyaları sessizce atlanır
- Aktif dil yüklenemezse varsayılan dil fallback olarak kullanılır
- Kullanıcıya görünen dil adı önce json meta alanından, sonra iç tablodan çözülür
- Ayar servisi ile aktif dil kalıcı olarak saklanır
- Android paketleme farklarına karşı dil klasörü için çoklu aday yol çözümleme uygulanır

JSON NOTLARI:
- Her dil dosyası bir dict/json object olmalıdır
- İsteğe bağlı meta anahtarları:
  - _meta_language_name
  - _meta_language_code

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez
- APK / AAB içinde paketlenmiş json dosyalarının erişimine uygun yol çözümleme içerir

SURUM: 3
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

import json
from pathlib import Path


class DilServisi:
    VARSAYILAN_DIL = "tr"

    def __init__(self) -> None:
        self._aktif_dil = self.VARSAYILAN_DIL
        self._aktif_sozluk: dict[str, object] = {}
        self._cache: dict[str, dict[str, object]] = {}
        self._languages_dir_cache: Path | None = None

        self._gorunen_dil_adlari = {
            "tr": "Türkçe",
            "en": "English",
            "de": "Deutsch",
            "fr": "Français",
            "es": "Español",
            "it": "Italiano",
            "pt": "Português",
            "pt-br": "Português (Brasil)",
            "nl": "Nederlands",
            "ru": "Русский",
            "uk": "Українська",
            "pl": "Polski",
            "cs": "Čeština",
            "sk": "Slovenčina",
            "sl": "Slovenščina",
            "hr": "Hrvatski",
            "sr": "Srpski",
            "bs": "Bosanski",
            "mk": "Македонски",
            "bg": "Български",
            "ro": "Română",
            "hu": "Magyar",
            "el": "Ελληνικά",
            "sq": "Shqip",
            "da": "Dansk",
            "sv": "Svenska",
            "no": "Norsk",
            "fi": "Suomi",
            "ar": "العربية",
            "fa": "فارسی",
            "ur": "اردو",
            "he": "עברית",
            "hi": "हिन्दी",
            "bn": "বাংলা",
            "ja": "日本語",
            "ko": "한국어",
            "zh": "中文",
            "zh-cn": "简体中文",
            "zh-tw": "繁體中文",
            "id": "Bahasa Indonesia",
            "ms": "Bahasa Melayu",
            "vi": "Tiếng Việt",
            "th": "ไทย",
        }

        self._aktif_sozluk = self._load_language_dict_with_fallback(self._aktif_dil)

        try:
            self.aktif_dili_ayardan_yukle(default=self.VARSAYILAN_DIL)
        except Exception:
            pass

    # =========================================================
    # PATH
    # =========================================================
    def _base_dir(self) -> Path:
        return Path(__file__).resolve().parent

    def _candidate_languages_dirs(self) -> list[Path]:
        """
        Dil klasörü için olası aday yolları döndürür.

        Android/AAB ortamında yol çözümleme bazen farklı davranabildiği için
        birden fazla güvenli aday kontrol edilir.
        """
        base_dir = self._base_dir()

        adaylar = [
            base_dir / "diller",
            Path(__file__).resolve().parent / "diller",
            Path(__file__).parent / "diller",
        ]

        sonuc: list[Path] = []
        gorulen: set[str] = set()

        for path in adaylar:
            try:
                key = str(path.resolve())
            except Exception:
                key = str(path)

            if key in gorulen:
                continue

            gorulen.add(key)
            sonuc.append(path)

        return sonuc

    def _languages_dir(self) -> Path:
        """
        Kullanılabilir ilk dil klasörünü bulur.

        Hiçbiri bulunamazsa varsayılan ana klasör döner.
        """
        try:
            if self._languages_dir_cache is not None:
                return self._languages_dir_cache
        except Exception:
            self._languages_dir_cache = None

        for path in self._candidate_languages_dirs():
            try:
                if path.is_dir():
                    self._languages_dir_cache = path
                    return path
            except Exception:
                continue

        varsayilan = self._base_dir() / "diller"
        self._languages_dir_cache = varsayilan
        return varsayilan

    # =========================================================
    # AYAR SERVISI
    # =========================================================
    def _ayar_get_language(self, default: str | None = None) -> str:
        try:
            from app.services.sistem.ayar_servisi import get_language

            return str(get_language(default=default or self.VARSAYILAN_DIL) or "")
        except Exception:
            return str(default or self.VARSAYILAN_DIL)

    def _ayar_set_language(self, code: str) -> None:
        try:
            from app.services.sistem.ayar_servisi import set_language

            set_language(code)
        except Exception:
            pass

    # =========================================================
    # NORMALIZE
    # =========================================================
    def _normalize_code(self, code: str) -> str:
        temiz = str(code or "").strip().lower()
        temiz = temiz.replace("\\", "").replace("/", "")
        temiz = temiz.replace(".json", "")
        temiz = temiz.replace("_", "-")
        return temiz

    def _language_file_path(self, code: str) -> Path:
        return self._languages_dir() / f"{self._normalize_code(code)}.json"

    # =========================================================
    # JSON LOAD
    # =========================================================
    def _safe_read_json(self, path: Path) -> dict[str, object]:
        try:
            if not path.is_file():
                return {}

            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)

            if isinstance(data, dict):
                return data

            return {}
        except Exception:
            return {}

    def _is_valid_language_dict(self, data) -> bool:
        return isinstance(data, dict) and len(data) > 0

    def _load_language_dict(self, code: str) -> dict[str, object]:
        temiz_kod = self._normalize_code(code)
        if not temiz_kod:
            return {}

        try:
            cached = self._cache.get(temiz_kod, None)
            if cached is not None:
                return dict(cached)
        except Exception:
            pass

        path = self._language_file_path(temiz_kod)
        data = self._safe_read_json(path)

        if not self._is_valid_language_dict(data):
            self._cache[temiz_kod] = {}
            return {}

        self._cache[temiz_kod] = dict(data)
        return dict(data)

    def _load_language_dict_with_fallback(self, code: str) -> dict[str, object]:
        data = self._load_language_dict(code)
        if data:
            return data

        if self._normalize_code(code) != self.VARSAYILAN_DIL:
            fallback = self._load_language_dict(self.VARSAYILAN_DIL)
            if fallback:
                return fallback

        return {}

    # =========================================================
    # META
    # =========================================================
    def _extract_language_name(self, code: str, data: dict[str, object]) -> str:
        try:
            meta_name = str(data.get("_meta_language_name", "") or "").strip()
            if meta_name:
                return meta_name
        except Exception:
            pass

        temiz_kod = self._normalize_code(code)

        try:
            tablo_adi = str(self._gorunen_dil_adlari.get(temiz_kod, "") or "").strip()
            if tablo_adi:
                return tablo_adi
        except Exception:
            pass

        return temiz_kod.upper() if temiz_kod else "UNKNOWN"

    def _extract_language_code(self, path: Path, data: dict[str, object]) -> str:
        try:
            meta_code = self._normalize_code(
                str(data.get("_meta_language_code", "") or "")
            )
            if meta_code:
                return meta_code
        except Exception:
            pass

        return self._normalize_code(path.stem)

    # =========================================================
    # PUBLIC - ACTIVE LANGUAGE
    # =========================================================
    def aktif_dil(self) -> str:
        return str(self._aktif_dil or self.VARSAYILAN_DIL)

    def aktif_dili_ayardan_yukle(self, default: str = "") -> str:
        varsayilan = (
            self._normalize_code(default or self.VARSAYILAN_DIL) or self.VARSAYILAN_DIL
        )
        ayar_kodu = self._normalize_code(self._ayar_get_language(varsayilan))

        if self.set_active_language(ayar_kodu, save_to_settings=False):
            return self._aktif_dil

        self.set_active_language(varsayilan, save_to_settings=False)
        return self._aktif_dil

    def set_active_language(self, code: str, save_to_settings: bool = True) -> bool:
        temiz_kod = self._normalize_code(code)
        if not temiz_kod:
            return False

        data = self._load_language_dict(temiz_kod)
        if not data:
            return False

        self._aktif_dil = temiz_kod
        self._aktif_sozluk = dict(data)

        if save_to_settings:
            self._ayar_set_language(temiz_kod)

        return True

    def dil_degistir(self, code: str) -> bool:
        return self.set_active_language(code, save_to_settings=True)

    def dil_destekleniyor_mu(self, code: str) -> bool:
        temiz_kod = self._normalize_code(code)
        if not temiz_kod:
            return False

        return bool(self._load_language_dict(temiz_kod))

    def dil_var_mi(self, code: str) -> bool:
        return self.dil_destekleniyor_mu(code)

    # =========================================================
    # PUBLIC - TEXT
    # =========================================================
    def metin(self, anahtar: str, varsayilan: str = "") -> str:
        key = str(anahtar or "").strip()
        if not key:
            return str(varsayilan or "")

        try:
            value = self._aktif_sozluk.get(key, None)
            if value is not None:
                return str(value)
        except Exception:
            pass

        try:
            if self._aktif_dil != self.VARSAYILAN_DIL:
                fallback_dict = self._load_language_dict(self.VARSAYILAN_DIL)
                fallback_value = fallback_dict.get(key, None)
                if fallback_value is not None:
                    return str(fallback_value)
        except Exception:
            pass

        return str(varsayilan or key)

    # =========================================================
    # PUBLIC - LANGUAGE LIST
    # =========================================================
    def mevcut_dilleri_listele(self) -> list[dict[str, str]]:
        sonuc: list[dict[str, str]] = []
        gorulen_kodlar: set[str] = set()

        try:
            diller_klasoru = self._languages_dir()
            if not diller_klasoru.is_dir():
                return sonuc

            for path in sorted(diller_klasoru.glob("*.json")):
                data = self._safe_read_json(path)
                if not self._is_valid_language_dict(data):
                    continue

                kod = self._extract_language_code(path, data)
                if not kod or kod in gorulen_kodlar:
                    continue

                gorulen_kodlar.add(kod)

                dil_adi = self._extract_language_name(kod, data)

                sonuc.append(
                    {
                        "code": kod,
                        "name": dil_adi,
                        "local_name": dil_adi,
                        "file": path.name,
                        "selected": "1" if kod == self.aktif_dil() else "0",
                        "active": "1",
                    }
                )
        except Exception:
            return []

        return sonuc

    def mevcut_dil_kodlari(self) -> list[str]:
        try:
            return [item["code"] for item in self.mevcut_dilleri_listele()]
        except Exception:
            return []

    def desteklenen_diller(
        self,
        sadece_aktifler: bool = False,
    ) -> dict[str, dict[str, object]]:
        sonuc: dict[str, dict[str, object]] = {}

        try:
            for item in self.mevcut_dilleri_listele():
                kod = str(item.get("code", "") or "").strip()
                if not kod:
                    continue

                aktif = str(item.get("active", "1")) == "1"
                if sadece_aktifler and not aktif:
                    continue

                yerel_ad = str(
                    item.get("local_name", "") or item.get("name", "") or kod
                )
                ad = str(item.get("name", "") or yerel_ad or kod)

                sonuc[kod] = {
                    "ad": ad,
                    "yerel_ad": yerel_ad,
                    "aktif": aktif,
                    "secili": kod == self.aktif_dil(),
                }
        except Exception:
            return {}

        return sonuc

    def dil_adi(self, code: str, default: str = "") -> str:
        temiz = self._normalize_code(code)
        if not temiz:
            return str(default or "")

        try:
            bilgiler = self.desteklenen_diller(sadece_aktifler=False)
            bilgi = bilgiler.get(temiz, {})
            ad = str(
                bilgi.get("yerel_ad", "") or bilgi.get("ad", "") or ""
            ).strip()
            if ad:
                return ad
        except Exception:
            pass

        try:
            tablo_adi = str(self._gorunen_dil_adlari.get(temiz, "") or "").strip()
            if tablo_adi:
                return tablo_adi
        except Exception:
            pass

        return str(default or temiz.upper())

    # =========================================================
    # CACHE
    # =========================================================
    def cache_temizle(self) -> None:
        self._cache = {}
        self._languages_dir_cache = None

    def dilleri_yeniden_tara(self) -> list[dict[str, str]]:
        aktif = self.aktif_dil()
        self.cache_temizle()

        yeni_liste = self.mevcut_dilleri_listele()

        if self.dil_destekleniyor_mu(aktif):
            self._aktif_dil = aktif
            self._aktif_sozluk = self._load_language_dict_with_fallback(aktif)
        else:
            self._aktif_dil = self.VARSAYILAN_DIL
            self._aktif_sozluk = self._load_language_dict_with_fallback(
                self.VARSAYILAN_DIL
            )

        return yeni_liste

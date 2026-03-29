# -*- coding: utf-8 -*-
"""
DOSYA: app/core/dil_ekle/dil_gelistirici.py

ROL:
- assets/lang klasöründeki dil dosyalarını yönetir
- Mevcut dil dosyalarını otomatik algılar
- Referans dil dosyasına göre eksik key analizleri yapar
- Yeni key ekleme ve mevcut dillere yayma işlemlerini yürütür
- Yeni dil dosyası oluşturur
- Dil json dosyalarını güvenli biçimde okuyup yazar

MİMARİ:
- Core katmanıdır
- UI bilmez
- Service katmanı üzerinden kullanılmak üzere tasarlanmıştır
- Fail-soft davranır
- JSON içeriklerini deterministik sırada yazar
- Mevcut meta anahtarlarını ve key yapısını korumaya odaklanır

SURUM: 1
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import Any

META_KEY_PREFIX = "_meta_"
VARSAYILAN_DIL_KLASORU = os.path.join("assets", "lang")
JSON_SUFFIX = ".json"


class DilGelistiriciHatasi(Exception):
    """
    Dil geliştirici işlemleri için temel hata türü.
    """


def _mutlak_yol(*parcalar: str) -> str:
    """
    Bu dosyanın konumuna göre proje içi mutlak yol üretir.
    app/core/dil_ekle/dil_gelistirici.py -> proje_koku/app/core/dil_ekle/...
    """
    burasi = os.path.abspath(os.path.dirname(__file__))
    core_klasoru = os.path.abspath(os.path.join(burasi, ".."))
    app_klasoru = os.path.abspath(os.path.join(core_klasoru, ".."))
    proje_koku = os.path.abspath(os.path.join(app_klasoru, ".."))
    return os.path.abspath(os.path.join(proje_koku, *parcalar))


def varsayilan_lang_klasoru() -> str:
    """
    Varsayılan dil klasörünün mutlak yolunu döndürür.
    """
    return _mutlak_yol(VARSAYILAN_DIL_KLASORU)


def lang_klasoru_coz(lang_klasoru: str | None = None) -> str:
    """
    Verilen dil klasörü yolunu çözer.
    Relative ise proje köküne göre mutlak yola çevirir.
    """
    raw = str(lang_klasoru or "").strip()

    if not raw:
        return varsayilan_lang_klasoru()

    if os.path.isabs(raw):
        return os.path.abspath(raw)

    return _mutlak_yol(raw)


def _guvenli_dict_kopyasi(veri: dict[str, Any] | None) -> dict[str, Any]:
    """
    Dict verisini güvenli kopyalar.
    """
    return deepcopy(dict(veri or {}))


def _json_sirali_yapi(veri: dict[str, Any]) -> dict[str, Any]:
    """
    JSON yazımı için meta anahtarları üstte tutar, diğer anahtarları mevcut sırayla bırakır.
    Python 3.7+ dict sırası korunduğu için ek sıralama uygulanmaz.
    """
    meta = {}
    normal = {}

    for anahtar, deger in veri.items():
        if str(anahtar).startswith(META_KEY_PREFIX):
            meta[anahtar] = deger
        else:
            normal[anahtar] = deger

    sonuc = {}
    sonuc.update(meta)
    sonuc.update(normal)
    return sonuc


def _klasor_varligini_sagla(klasor_yolu: str) -> None:
    """
    Klasör yoksa oluşturur.
    """
    os.makedirs(klasor_yolu, exist_ok=True)


def _gecerli_dil_kodu_mu(dil_kodu: str) -> bool:
    """
    Dil kodu için temel güvenlik kontrolü yapar.
    Örnek geçerli değerler: tr, en, pt-br, zh-cn
    """
    raw = str(dil_kodu or "").strip().lower()
    if not raw:
        return False

    izinli = "abcdefghijklmnopqrstuvwxyz0123456789-_"
    return all(ch in izinli for ch in raw)


def _key_gecerli_mi(key: str) -> bool:
    """
    Key için temel doğrulama yapar.
    """
    raw = str(key or "").strip()
    if not raw:
        return False
    if "\n" in raw or "\r" in raw or "\t" in raw:
        return False
    return True


def _dosya_json_mu(dosya_adi: str) -> bool:
    """
    Dosyanın geçerli json dil dosyası olup olmadığını döndürür.
    """
    raw = str(dosya_adi or "").strip()
    return bool(raw) and raw.lower().endswith(JSON_SUFFIX)


def dil_kodundan_dosya_adi(dil_kodu: str) -> str:
    """
    Dil kodundan json dosya adı üretir.
    """
    raw = str(dil_kodu or "").strip().lower()
    if not _gecerli_dil_kodu_mu(raw):
        raise DilGelistiriciHatasi(f"Gecersiz dil kodu: {dil_kodu!r}")
    return f"{raw}{JSON_SUFFIX}"


def dil_kodunu_dosya_adindan_al(dosya_adi: str) -> str:
    """
    Dosya adından dil kodunu üretir.
    """
    raw = str(dosya_adi or "").strip()
    if not _dosya_json_mu(raw):
        raise DilGelistiriciHatasi(f"Gecersiz dil dosyasi: {dosya_adi!r}")
    return raw[: -len(JSON_SUFFIX)].strip().lower()


def dil_dosyasi_yolu(dil_kodu: str, lang_klasoru: str | None = None) -> str:
    """
    Dil koduna göre hedef json dosyasının mutlak yolunu döndürür.
    """
    klasor = lang_klasoru_coz(lang_klasoru)
    return os.path.join(klasor, dil_kodundan_dosya_adi(dil_kodu))


def json_oku(dosya_yolu: str) -> dict[str, Any]:
    """
    JSON dosyasını dict olarak okur.
    """
    yol = os.path.abspath(str(dosya_yolu or "").strip())
    if not yol:
        raise DilGelistiriciHatasi("JSON okuma icin dosya yolu bos.")
    if not os.path.isfile(yol):
        raise DilGelistiriciHatasi(f"JSON dosyasi bulunamadi: {yol}")

    try:
        with open(yol, "r", encoding="utf-8") as f:
            veri = json.load(f)
    except json.JSONDecodeError as exc:
        raise DilGelistiriciHatasi(f"JSON parse hatasi: {yol} | {exc}") from exc
    except Exception as exc:
        raise DilGelistiriciHatasi(f"JSON okuma hatasi: {yol} | {exc}") from exc

    if not isinstance(veri, dict):
        raise DilGelistiriciHatasi(
            f"JSON kok veri tipi dict olmali: {yol}"
        )

    return veri


def json_yaz(dosya_yolu: str, veri: dict[str, Any]) -> str:
    """
    JSON verisini dosyaya UTF-8 ve deterministik formatta yazar.
    """
    yol = os.path.abspath(str(dosya_yolu or "").strip())
    if not yol:
        raise DilGelistiriciHatasi("JSON yazma icin dosya yolu bos.")

    if not isinstance(veri, dict):
        raise DilGelistiriciHatasi("JSON yazma verisi dict olmali.")

    _klasor_varligini_sagla(os.path.dirname(yol))

    yazilacak = _json_sirali_yapi(_guvenli_dict_kopyasi(veri))

    try:
        with open(yol, "w", encoding="utf-8") as f:
            json.dump(
                yazilacak,
                f,
                ensure_ascii=False,
                indent=2,
            )
            f.write("\n")
    except Exception as exc:
        raise DilGelistiriciHatasi(f"JSON yazma hatasi: {yol} | {exc}") from exc

    return yol


def dil_dosyalarini_listele(lang_klasoru: str | None = None) -> list[dict[str, Any]]:
    """
    Lang klasöründeki tüm json dil dosyalarını algılar.

    Dönen kayıt örneği:
    {
        "dil_kodu": "tr",
        "dosya_adi": "tr.json",
        "dosya_yolu": "/.../assets/lang/tr.json",
        "dil_adi": "Türkçe",
        "key_sayisi": 120,
        "meta_key_sayisi": 2
    }
    """
    klasor = lang_klasoru_coz(lang_klasoru)
    if not os.path.isdir(klasor):
        return []

    sonuc: list[dict[str, Any]] = []

    for ad in sorted(os.listdir(klasor), key=lambda x: x.lower()):
        if not _dosya_json_mu(ad):
            continue

        tam_yol = os.path.join(klasor, ad)

        try:
            veri = json_oku(tam_yol)
        except Exception:
            veri = {}

        dil_kodu = ""
        try:
            dil_kodu = dil_kodunu_dosya_adindan_al(ad)
        except Exception:
            dil_kodu = ""

        meta_sayisi = 0
        key_sayisi = 0

        for anahtar in veri.keys():
            if str(anahtar).startswith(META_KEY_PREFIX):
                meta_sayisi += 1
            else:
                key_sayisi += 1

        sonuc.append(
            {
                "dil_kodu": dil_kodu,
                "dosya_adi": ad,
                "dosya_yolu": tam_yol,
                "dil_adi": str(veri.get("_meta_language_name", "") or "").strip(),
                "key_sayisi": key_sayisi,
                "meta_key_sayisi": meta_sayisi,
            }
        )

    return sonuc


def dil_kodlarini_listele(lang_klasoru: str | None = None) -> list[str]:
    """
    Algılanan dil kodlarını döndürür.
    """
    kayitlar = dil_dosyalarini_listele(lang_klasoru)
    return [
        str(k.get("dil_kodu", "") or "").strip()
        for k in kayitlar
        if k.get("dil_kodu")
    ]


def dil_dosyasi_var_mi(dil_kodu: str, lang_klasoru: str | None = None) -> bool:
    """
    Belirli dil dosyasının varlığını kontrol eder.
    """
    try:
        yol = dil_dosyasi_yolu(dil_kodu, lang_klasoru)
    except Exception:
        return False
    return os.path.isfile(yol)


def dil_verisini_yukle(
    dil_kodu: str,
    lang_klasoru: str | None = None,
) -> dict[str, Any]:
    """
    Verilen dil koduna ait json içeriğini yükler.
    """
    yol = dil_dosyasi_yolu(dil_kodu, lang_klasoru)
    return json_oku(yol)


def dil_keylerini_getir(
    dil_kodu: str,
    lang_klasoru: str | None = None,
    *,
    meta_dahil: bool = False,
) -> list[str]:
    """
    Belirli dil dosyasındaki key listesini döndürür.
    """
    veri = dil_verisini_yukle(dil_kodu, lang_klasoru)
    sonuc: list[str] = []

    for anahtar in veri.keys():
        if not meta_dahil and str(anahtar).startswith(META_KEY_PREFIX):
            continue
        sonuc.append(str(anahtar))

    return sonuc


def keyler_arasi_eksikleri_bul(
    referans_veri: dict[str, Any],
    hedef_veri: dict[str, Any],
) -> list[str]:
    """
    Referans veride olup hedef veride olmayan keyleri döndürür.
    Meta keyler hariç tutulur.
    """
    referans = dict(referans_veri or {})
    hedef = dict(hedef_veri or {})
    eksikler: list[str] = []

    for anahtar in referans.keys():
        anahtar_str = str(anahtar)
        if anahtar_str.startswith(META_KEY_PREFIX):
            continue
        if anahtar_str not in hedef:
            eksikler.append(anahtar_str)

    return eksikler


def eksik_keyleri_bul(
    referans_dil_kodu: str,
    hedef_dil_kodu: str,
    lang_klasoru: str | None = None,
) -> list[str]:
    """
    Referans dil dosyasına göre hedef dilde eksik keyleri bulur.
    """
    referans = dil_verisini_yukle(referans_dil_kodu, lang_klasoru)
    hedef = dil_verisini_yukle(hedef_dil_kodu, lang_klasoru)
    return keyler_arasi_eksikleri_bul(referans, hedef)


def tum_dillerde_eksik_analizi(
    referans_dil_kodu: str,
    lang_klasoru: str | None = None,
) -> list[dict[str, Any]]:
    """
    Referans dile göre tüm dillerin eksik key analizini döndürür.

    Dönen kayıt örneği:
    {
        "dil_kodu": "de",
        "eksik_keyler": ["save", "cancel"],
        "eksik_sayisi": 2
    }
    """
    referans_veri = dil_verisini_yukle(referans_dil_kodu, lang_klasoru)
    diller = dil_kodlarini_listele(lang_klasoru)
    sonuc: list[dict[str, Any]] = []

    for dil_kodu in diller:
        if dil_kodu == referans_dil_kodu:
            continue

        try:
            hedef_veri = dil_verisini_yukle(dil_kodu, lang_klasoru)
            eksikler = keyler_arasi_eksikleri_bul(referans_veri, hedef_veri)
        except Exception:
            eksikler = []

        sonuc.append(
            {
                "dil_kodu": dil_kodu,
                "eksik_keyler": eksikler,
                "eksik_sayisi": len(eksikler),
            }
        )

    sonuc.sort(key=lambda x: (int(x.get("eksik_sayisi", 0)), str(x.get("dil_kodu", ""))))
    sonuc.reverse()
    return sonuc


def tek_dile_key_ekle(
    dil_kodu: str,
    key: str,
    deger: Any = "",
    lang_klasoru: str | None = None,
    *,
    varsa_uzerine_yaz: bool = False,
) -> dict[str, Any]:
    """
    Tek bir dil dosyasına yeni key ekler.
    """
    raw_key = str(key or "").strip()
    if not _key_gecerli_mi(raw_key):
        raise DilGelistiriciHatasi(f"Gecersiz key: {key!r}")

    veri = dil_verisini_yukle(dil_kodu, lang_klasoru)

    if raw_key in veri and not varsa_uzerine_yaz:
        raise DilGelistiriciHatasi(
            f"Key zaten var: dil={dil_kodu!r}, key={raw_key!r}"
        )

    veri[raw_key] = deger
    yol = dil_dosyasi_yolu(dil_kodu, lang_klasoru)
    json_yaz(yol, veri)

    return {
        "dil_kodu": dil_kodu,
        "key": raw_key,
        "dosya_yolu": yol,
        "yazildi": True,
    }


def coklu_dillere_key_ekle(
    key: str,
    dil_deger_haritasi: dict[str, Any],
    lang_klasoru: str | None = None,
    *,
    eksik_olanlara_ekle: bool = True,
    varsa_uzerine_yaz: bool = False,
) -> list[dict[str, Any]]:
    """
    Aynı key'i birden fazla dil dosyasına ekler.
    """
    raw_key = str(key or "").strip()
    if not _key_gecerli_mi(raw_key):
        raise DilGelistiriciHatasi(f"Gecersiz key: {key!r}")

    if not isinstance(dil_deger_haritasi, dict) or not dil_deger_haritasi:
        raise DilGelistiriciHatasi("dil_deger_haritasi bos olamaz.")

    sonuc: list[dict[str, Any]] = []

    for dil_kodu, deger in dil_deger_haritasi.items():
        veri = dil_verisini_yukle(dil_kodu, lang_klasoru)

        if raw_key in veri:
            if eksik_olanlara_ekle and not varsa_uzerine_yaz:
                sonuc.append(
                    {
                        "dil_kodu": dil_kodu,
                        "key": raw_key,
                        "yazildi": False,
                        "neden": "zaten_var",
                    }
                )
                continue

        veri[raw_key] = deger
        yol = dil_dosyasi_yolu(dil_kodu, lang_klasoru)
        json_yaz(yol, veri)

        sonuc.append(
            {
                "dil_kodu": dil_kodu,
                "key": raw_key,
                "dosya_yolu": yol,
                "yazildi": True,
            }
        )

    return sonuc


def tum_dillere_key_ekle(
    key: str,
    varsayilan_deger: Any = "",
    lang_klasoru: str | None = None,
    *,
    referans_dil_kodu: str | None = None,
    referans_degeri_kullan: bool = True,
    varsa_uzerine_yaz: bool = False,
) -> list[dict[str, Any]]:
    """
    Bir key'i algılanan tüm dil dosyalarına ekler.
    """
    raw_key = str(key or "").strip()
    if not _key_gecerli_mi(raw_key):
        raise DilGelistiriciHatasi(f"Gecersiz key: {key!r}")

    diller = dil_kodlarini_listele(lang_klasoru)
    sonuc: list[dict[str, Any]] = []

    for dil_kodu in diller:
        veri = dil_verisini_yukle(dil_kodu, lang_klasoru)

        if raw_key in veri and not varsa_uzerine_yaz:
            sonuc.append(
                {
                    "dil_kodu": dil_kodu,
                    "key": raw_key,
                    "yazildi": False,
                    "neden": "zaten_var",
                }
            )
            continue

        if (
            referans_dil_kodu
            and referans_degeri_kullan
            and dil_kodu == str(referans_dil_kodu).strip().lower()
        ):
            yazilacak_deger = varsayilan_deger
        else:
            yazilacak_deger = varsayilan_deger

        veri[raw_key] = yazilacak_deger
        yol = dil_dosyasi_yolu(dil_kodu, lang_klasoru)
        json_yaz(yol, veri)

        sonuc.append(
            {
                "dil_kodu": dil_kodu,
                "key": raw_key,
                "dosya_yolu": yol,
                "yazildi": True,
            }
        )

    return sonuc


def eksik_keyleri_hedef_dile_ekle(
    referans_dil_kodu: str,
    hedef_dil_kodu: str,
    lang_klasoru: str | None = None,
    *,
    bos_deger_kullan: bool = True,
    varsa_uzerine_yaz: bool = False,
) -> dict[str, Any]:
    """
    Referans dilde olup hedef dilde olmayan keyleri hedef dosyaya ekler.
    """
    referans = dil_verisini_yukle(referans_dil_kodu, lang_klasoru)
    hedef = dil_verisini_yukle(hedef_dil_kodu, lang_klasoru)

    eklenenler: list[str] = []

    for anahtar, referans_deger in referans.items():
        anahtar_str = str(anahtar)
        if anahtar_str.startswith(META_KEY_PREFIX):
            continue

        if anahtar_str in hedef and not varsa_uzerine_yaz:
            continue

        if anahtar_str not in hedef or varsa_uzerine_yaz:
            hedef[anahtar_str] = "" if bos_deger_kullan else referans_deger
            eklenenler.append(anahtar_str)

    yol = dil_dosyasi_yolu(hedef_dil_kodu, lang_klasoru)
    json_yaz(yol, hedef)

    return {
        "referans_dil_kodu": referans_dil_kodu,
        "hedef_dil_kodu": hedef_dil_kodu,
        "eklenen_keyler": eklenenler,
        "eklenen_sayisi": len(eklenenler),
        "dosya_yolu": yol,
    }


def yeni_dil_sablonu_uret(
    referans_dil_kodu: str,
    yeni_dil_kodu: str,
    yeni_dil_adi: str,
    lang_klasoru: str | None = None,
    *,
    bos_deger_kullan: bool = True,
) -> dict[str, Any]:
    """
    Referans dilden yeni dil için başlangıç şablonu üretir.
    """
    raw_kod = str(yeni_dil_kodu or "").strip().lower()
    raw_ad = str(yeni_dil_adi or "").strip()

    if not _gecerli_dil_kodu_mu(raw_kod):
        raise DilGelistiriciHatasi(f"Gecersiz yeni dil kodu: {yeni_dil_kodu!r}")

    if not raw_ad:
        raise DilGelistiriciHatasi("Yeni dil adi bos olamaz.")

    referans = dil_verisini_yukle(referans_dil_kodu, lang_klasoru)
    sonuc: dict[str, Any] = {}

    for anahtar, deger in referans.items():
        anahtar_str = str(anahtar)

        if anahtar_str == "_meta_language_code":
            sonuc[anahtar_str] = raw_kod
            continue

        if anahtar_str == "_meta_language_name":
            sonuc[anahtar_str] = raw_ad
            continue

        if anahtar_str.startswith(META_KEY_PREFIX):
            sonuc[anahtar_str] = deepcopy(deger)
            continue

        sonuc[anahtar_str] = "" if bos_deger_kullan else deepcopy(deger)

    if "_meta_language_code" not in sonuc:
        sonuc["_meta_language_code"] = raw_kod

    if "_meta_language_name" not in sonuc:
        sonuc["_meta_language_name"] = raw_ad

    return sonuc


def yeni_dil_dosyasi_olustur(
    referans_dil_kodu: str,
    yeni_dil_kodu: str,
    yeni_dil_adi: str,
    lang_klasoru: str | None = None,
    *,
    bos_deger_kullan: bool = True,
    varsa_uzerine_yaz: bool = False,
) -> dict[str, Any]:
    """
    Yeni dil dosyası oluşturur.
    """
    raw_kod = str(yeni_dil_kodu or "").strip().lower()

    if dil_dosyasi_var_mi(raw_kod, lang_klasoru) and not varsa_uzerine_yaz:
        raise DilGelistiriciHatasi(
            f"Dil dosyasi zaten var: {raw_kod!r}"
        )

    veri = yeni_dil_sablonu_uret(
        referans_dil_kodu=referans_dil_kodu,
        yeni_dil_kodu=raw_kod,
        yeni_dil_adi=yeni_dil_adi,
        lang_klasoru=lang_klasoru,
        bos_deger_kullan=bos_deger_kullan,
    )

    yol = dil_dosyasi_yolu(raw_kod, lang_klasoru)
    json_yaz(yol, veri)

    return {
        "dil_kodu": raw_kod,
        "dil_adi": str(yeni_dil_adi or "").strip(),
        "dosya_yolu": yol,
        "olusturuldu": True,
    }


def dil_ozeti_getir(
    dil_kodu: str,
    lang_klasoru: str | None = None,
) -> dict[str, Any]:
    """
    Dil dosyasına dair özet bilgi döndürür.
    """
    veri = dil_verisini_yukle(dil_kodu, lang_klasoru)

    meta_key_sayisi = 0
    key_sayisi = 0

    for anahtar in veri.keys():
        if str(anahtar).startswith(META_KEY_PREFIX):
            meta_key_sayisi += 1
        else:
            key_sayisi += 1

    return {
        "dil_kodu": str(veri.get("_meta_language_code", dil_kodu) or "").strip(),
        "dil_adi": str(veri.get("_meta_language_name", "") or "").strip(),
        "dosya_yolu": dil_dosyasi_yolu(dil_kodu, lang_klasoru),
        "key_sayisi": key_sayisi,
        "meta_key_sayisi": meta_key_sayisi,
    }


__all__ = (
    "DilGelistiriciHatasi",
    "META_KEY_PREFIX",
    "VARSAYILAN_DIL_KLASORU",
    "varsayilan_lang_klasoru",
    "lang_klasoru_coz",
    "dil_kodundan_dosya_adi",
    "dil_kodunu_dosya_adindan_al",
    "dil_dosyasi_yolu",
    "json_oku",
    "json_yaz",
    "dil_dosyalarini_listele",
    "dil_kodlarini_listele",
    "dil_dosyasi_var_mi",
    "dil_verisini_yukle",
    "dil_keylerini_getir",
    "keyler_arasi_eksikleri_bul",
    "eksik_keyleri_bul",
    "tum_dillerde_eksik_analizi",
    "tek_dile_key_ekle",
    "coklu_dillere_key_ekle",
    "tum_dillere_key_ekle",
    "eksik_keyleri_hedef_dile_ekle",
    "yeni_dil_sablonu_uret",
    "yeni_dil_dosyasi_olustur",
    "dil_ozeti_getir",
)
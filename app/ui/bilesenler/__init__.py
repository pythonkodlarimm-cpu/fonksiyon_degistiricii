# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/bilesenler/__init__.py

ROL:
- UI bileşenleri için merkezi ve kontrollü giriş noktası sağlar
- Bileşenleri lazy import ile yükler
- Tekrarlı import maliyetini azaltır
- Net ve deterministic API sunar

MİMARİ:
- Strict API (__all__)
- Lazy import (__getattr__)
- Type-safe cache
- Tek çözümleme sonrası cache kullanımı
- Geriye uyumluluk katmanı içermez
- Belirsiz export yoktur

SURUM: 3
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Callable, Final, TypeAlias

_NesneTipi: TypeAlias = object

__all__: Final[tuple[str, ...]] = (
    "AksiyonIkonButonu",
    "AltAksiyonCubugu",
    "BilgiKutusu",
    "DosyaYoluAlani",
    "FonksiyonListesi",
    "HataKarti",
    "KodPaneli",
    "ListePaneli",
    "UstToolbar",
)

__lazy_cache: dict[str, _NesneTipi] = {}

__import_map: dict[str, Callable[[], _NesneTipi]] = {
    "AksiyonIkonButonu": lambda: __import_aksiyon_ikon_butonu(),
    "AltAksiyonCubugu": lambda: __import_alt_aksiyon_cubugu(),
    "BilgiKutusu": lambda: __import_bilgi_kutusu(),
    "DosyaYoluAlani": lambda: __import_dosya_yolu_alani(),
    "FonksiyonListesi": lambda: __import_fonksiyon_listesi(),
    "HataKarti": lambda: __import_hata_karti(),
    "KodPaneli": lambda: __import_kod_paneli(),
    "ListePaneli": lambda: __import_liste_paneli(),
    "UstToolbar": lambda: __import_ust_toolbar(),
}


def __import_aksiyon_ikon_butonu():
    from app.ui.bilesenler.aksiyon_ikon_butonu import AksiyonIkonButonu

    return AksiyonIkonButonu


def __import_alt_aksiyon_cubugu():
    from app.ui.bilesenler.alt_aksiyon_cubugu import AltAksiyonCubugu

    return AltAksiyonCubugu


def __import_bilgi_kutusu():
    from app.ui.bilesenler.bilgi_kutusu import BilgiKutusu

    return BilgiKutusu


def __import_dosya_yolu_alani():
    from app.ui.bilesenler.dosya_yolu_alani import DosyaYoluAlani

    return DosyaYoluAlani


def __import_fonksiyon_listesi():
    from app.ui.bilesenler.fonksiyon_listesi import FonksiyonListesi

    return FonksiyonListesi


def __import_hata_karti():
    from app.ui.bilesenler.hata_karti import HataKarti

    return HataKarti


def __import_kod_paneli():
    from app.ui.bilesenler.kod_paneli import KodPaneli

    return KodPaneli


def __import_liste_paneli():
    from app.ui.bilesenler.liste_paneli import ListePaneli

    return ListePaneli


def __import_ust_toolbar():
    from app.ui.bilesenler.ust_toolbar import UstToolbar

    return UstToolbar


def __getattr__(name: str) -> _NesneTipi:
    """
    Lazy import resolver.

    İlk erişimde ilgili bileşeni yükler ve cache'e alır.
    Sonraki erişimlerde doğrudan cache döner.
    """
    cached = __lazy_cache.get(name)
    if cached is not None:
        return cached

    resolver = __import_map.get(name)
    if resolver is None:
        raise AttributeError(
            f"{__name__!r} paketinde '{name}' export edilmemiş. "
            f"Geçerli exportlar: {', '.join(__all__)}"
        )

    obj = resolver()
    __lazy_cache[name] = obj
    return obj


def __dir__() -> list[str]:
    """
    IDE ve introspection için export listesini döndürür.
    """
    return list(__all__)

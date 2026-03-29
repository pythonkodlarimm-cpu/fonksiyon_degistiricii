# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ekranlar/ana_ekran_paketi/__init__.py

ROL:
- Ana ekran paketi için kontrollü tek giriş sağlar
- Paket alt modüllerini lazy import ile çözümler
- Tekrar eden import maliyetini azaltır
- Net ve deterministic API sunar

MİMARİ:
- Strict API (__all__)
- Lazy import (__getattr__)
- Type-safe cache
- Tek çözümleme sonrası cache kullanımı
- Geriye uyumluluk katmanı içermez
- Belirsiz export yoktur
- Alt kontrol paneli export edilmez; yerleşim içinde doğrudan kurulur

SURUM: 6
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Final, TypeAlias, Callable

_NesneTipi: TypeAlias = object
_ResolverTipi: TypeAlias = Callable[[], _NesneTipi]

__all__: Final[tuple[str, ...]] = (
    "AnaEkranAksiyonMixin",
    "AnaEkranYardimciMixin",
    "AnaEkranYerlesimMixin",
)

__lazy_cache: dict[str, _NesneTipi] = {}


def __import_aksiyon() -> _NesneTipi:
    from app.ui.ekranlar.ana_ekran_paketi.aksiyonlar import AnaEkranAksiyonMixin

    return AnaEkranAksiyonMixin


def __import_yardimci() -> _NesneTipi:
    from app.ui.ekranlar.ana_ekran_paketi.yardimci import AnaEkranYardimciMixin

    return AnaEkranYardimciMixin


def __import_yerlesim() -> _NesneTipi:
    from app.ui.ekranlar.ana_ekran_paketi.yerlesim import AnaEkranYerlesimMixin

    return AnaEkranYerlesimMixin


__import_map: Final[dict[str, _ResolverTipi]] = {
    "AnaEkranAksiyonMixin": __import_aksiyon,
    "AnaEkranYardimciMixin": __import_yardimci,
    "AnaEkranYerlesimMixin": __import_yerlesim,
}


def __getattr__(name: str) -> _NesneTipi:
    """
    Lazy import resolver.

    İlk erişimde ilgili modülü yükler ve cache'e alır.
    Sonraki erişimlerde direkt cache döner.
    """
    obj = __lazy_cache.get(name)
    if obj is not None:
        return obj

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
    return sorted(__all__)

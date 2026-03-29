# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ekranlar/ana_ekran_paketi/aksiyonlar_paketi/__init__.py

ROL:
- Ana ekran aksiyon alt paketinin public API yüzeyini tanımlar
- Alt aksiyon mixin sınıflarını dışa açar
- Base aksiyon (feedback pipeline) mixin'ini de dahil eder
- Üst katmanın tek noktadan import yapmasını sağlar

MİMARİ:
- UI alt paket giriş dosyasıdır
- Strict API (__all__) kullanır
- Lazy import (__getattr__) uygular
- Type-safe cache ile tek çözümleme sonrası cache kullanır
- Deterministik export yüzeyi sunar
- Geriye uyumluluk katmanı içermez
- Belirsiz export veya fallback içermez

SURUM: 3
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Final, TypeAlias, Callable

_NesneTipi: TypeAlias = object
_ResolverTipi: TypeAlias = Callable[[], _NesneTipi]

__all__: Final[tuple[str, ...]] = (
    "AnaEkranBaseAksiyonMixin",
    "AnaEkranSecimAksiyonMixin",
    "AnaEkranMenuAksiyonMixin",
    "AnaEkranTaramaAksiyonMixin",
    "AnaEkranGuncellemeAksiyonMixin",
    "AnaEkranDilAksiyonMixin",
    "AnaEkranYedekAksiyonMixin",
    "AnaEkranGelistiriciAksiyonMixin",
)

__lazy_cache: dict[str, _NesneTipi] = {}


def __import_base() -> _NesneTipi:
    from app.ui.ekranlar.ana_ekran_paketi.aksiyonlar_paketi.base_aksiyon import (
        AnaEkranBaseAksiyonMixin,
    )

    return AnaEkranBaseAksiyonMixin


def __import_secim() -> _NesneTipi:
    from app.ui.ekranlar.ana_ekran_paketi.aksiyonlar_paketi.secim_aksiyonlari import (
        AnaEkranSecimAksiyonMixin,
    )

    return AnaEkranSecimAksiyonMixin


def __import_menu() -> _NesneTipi:
    from app.ui.ekranlar.ana_ekran_paketi.aksiyonlar_paketi.menu_aksiyonlari import (
        AnaEkranMenuAksiyonMixin,
    )

    return AnaEkranMenuAksiyonMixin


def __import_tarama() -> _NesneTipi:
    from app.ui.ekranlar.ana_ekran_paketi.aksiyonlar_paketi.tarama_aksiyonlari import (
        AnaEkranTaramaAksiyonMixin,
    )

    return AnaEkranTaramaAksiyonMixin


def __import_guncelleme() -> _NesneTipi:
    from app.ui.ekranlar.ana_ekran_paketi.aksiyonlar_paketi.guncelleme_aksiyonlari import (
        AnaEkranGuncellemeAksiyonMixin,
    )

    return AnaEkranGuncellemeAksiyonMixin


def __import_dil() -> _NesneTipi:
    from app.ui.ekranlar.ana_ekran_paketi.aksiyonlar_paketi.dil_aksiyonlari import (
        AnaEkranDilAksiyonMixin,
    )

    return AnaEkranDilAksiyonMixin


def __import_yedek() -> _NesneTipi:
    from app.ui.ekranlar.ana_ekran_paketi.aksiyonlar_paketi.yedek_aksiyonlari import (
        AnaEkranYedekAksiyonMixin,
    )

    return AnaEkranYedekAksiyonMixin


def __import_gelistirici() -> _NesneTipi:
    from app.ui.ekranlar.ana_ekran_paketi.aksiyonlar_paketi.gelistirici_aksiyonlari import (
        AnaEkranGelistiriciAksiyonMixin,
    )

    return AnaEkranGelistiriciAksiyonMixin


__import_map: Final[dict[str, _ResolverTipi]] = {
    "AnaEkranBaseAksiyonMixin": __import_base,
    "AnaEkranSecimAksiyonMixin": __import_secim,
    "AnaEkranMenuAksiyonMixin": __import_menu,
    "AnaEkranTaramaAksiyonMixin": __import_tarama,
    "AnaEkranGuncellemeAksiyonMixin": __import_guncelleme,
    "AnaEkranDilAksiyonMixin": __import_dil,
    "AnaEkranYedekAksiyonMixin": __import_yedek,
    "AnaEkranGelistiriciAksiyonMixin": __import_gelistirici,
}


def __getattr__(name: str) -> _NesneTipi:
    """
    Lazy import resolver.
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

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/tarama_gecis_ve_liste_acma/__init__.py

ROL:
- tarama_gecis_ve_liste_acma paketinin dışa açılan ana giriş noktasıdır
- Root tarama geçiş ve liste açma mixin sınıfını lazy import ile erişilebilir kılar
- İlk erişimden sonra import sonucunu cache içinde tutar
- Paket import edildiğinde alt modülü gereksiz yere yüklemez

MİMARİ:
- __getattr__ ile attribute bazlı lazy load uygulanır
- İlk yüklenen sınıf globals() içine yazılarak cache'lenir
- Sonraki erişimlerde tekrar import yapılmaz
- __all__ ile public API sabit tutulur
- Büyük ve modüler root mimarisi ile uyumludur

KULLANIM:
- from app.ui.root_paketi.root.root_akisi.tarama_gecis_ve_liste_acma import RootTaramaGecisVeListeAcmaMixin

NOT:
- İlk erişimde gerçek import yapılır
- Sonraki erişimlerde cache'ten döner
- Böylece startup yükü azalır, tekrar import maliyeti düşer

SURUM: 2
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

__all__ = ["RootTaramaGecisVeListeAcmaMixin"]


def __getattr__(name: str):
    """
    Lazy import + cache mekanizması.

    İstenen attribute ilk kez erişildiğinde ilgili modül yüklenir.
    Yüklenen nesne globals() içine yazılarak cache'lenir.
    """
    if name == "RootTaramaGecisVeListeAcmaMixin":
        from .tarama_gecis_ve_liste_acma import RootTaramaGecisVeListeAcmaMixin

        globals()["RootTaramaGecisVeListeAcmaMixin"] = (
            RootTaramaGecisVeListeAcmaMixin
        )
        return RootTaramaGecisVeListeAcmaMixin

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__():
    """
    IDE / introspection tarafında public API görünürlüğünü korur.
    """
    return sorted(set(globals().keys()) | set(__all__))

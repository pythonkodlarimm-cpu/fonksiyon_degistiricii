# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/dil_yardimcilari/__init__.py

ROL:
- dil_yardimcilari paketinin dışa açılan ana giriş noktasıdır
- Root dil yardımcı mixin sınıfını lazy import ile erişilebilir kılar
- İlk erişimden sonra import sonucunu cache içinde tutar
- Paket import edildiğinde alt modülü gereksiz yere yüklemez

MİMARİ:
- __getattr__ ile attribute bazlı lazy load uygulanır
- İlk yüklenen sınıf globals() içine yazılarak cache'lenir
- Sonraki erişimlerde tekrar import yapılmaz
- __all__ ile public API sabit tutulur
- Büyük ve modüler root mimarisi ile uyumludur

KULLANIM:
- from app.ui.root_paketi.root.root_akisi.dil_yardimcilari import RootDilYardimcilariMixin

NOT:
- İlk erişimde gerçek import yapılır
- Sonraki erişimlerde cache'ten döner
- Böylece startup yükü azalır, tekrar import maliyeti düşer

SURUM: 3
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

__all__ = ["RootDilYardimcilariMixin"]


def __getattr__(name: str):
    """
    Lazy import + cache mekanizması.

    İstenen attribute ilk kez erişildiğinde ilgili modül yüklenir.
    Yüklenen nesne globals() içine yazılarak cache'lenir.
    """
    if name == "RootDilYardimcilariMixin":
        from .dil_yardimcilari import RootDilYardimcilariMixin

        globals()["RootDilYardimcilariMixin"] = RootDilYardimcilariMixin
        return RootDilYardimcilariMixin

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__():
    """
    IDE / introspection tarafında public API görünürlüğünü korur.
    """
    return sorted(set(globals().keys()) | set(__all__))

# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/__init__.py

ROL:
- root paketinin dışa açılan ana giriş noktasıdır
- RootWidget, RootAkisiYoneticisi ve RootRootYoneticisi sınıflarını lazy import ile erişilebilir kılar
- İlk erişimden sonra import sonucunu cache içinde tutar
- Paket import edildiğinde alt modülleri gereksiz yere yüklemez

MİMARİ:
- __getattr__ ile attribute bazlı lazy load uygulanır
- İlk yüklenen nesne globals() içine yazılarak cache'lenir
- Sonraki erişimlerde tekrar import yapılmaz
- __all__ ile public API sabit tutulur
- APK/build sürecinde gereksiz import yükünü azaltır
- Gerçek klasör yapısı:
    - app/ui/root_paketi/root/root.py
    - app/ui/root_paketi/root/yoneticisi.py
    - app/ui/root_paketi/root/root_akisi/

KULLANIM:
- from app.ui.root_paketi.root import RootWidget
- from app.ui.root_paketi.root import RootAkisiYoneticisi
- from app.ui.root_paketi.root import RootRootYoneticisi

NOT:
- RootRootYoneticisi adı burada root klasörü içindeki yönetici için kullanılmıştır
- app/ui/root_paketi/yoneticisi.py ise üst seviye root_paketi yöneticisidir
- İsim çakışmasını önlemek için bu pakette yönetici farklı adla export edilmiştir

SURUM: 1
TARIH: 2026-03-24
IMZA: FY.
"""

from __future__ import annotations

__all__ = ["RootWidget", "RootAkisiYoneticisi", "RootRootYoneticisi"]


def __getattr__(name: str):
    """
    Lazy import + cache mekanizması.

    İstenen attribute ilk kez erişildiğinde ilgili modül yüklenir.
    Yüklenen nesne globals() içine yazılarak cache'lenir.
    """
    if name == "RootWidget":
        from .root import RootWidget

        globals()["RootWidget"] = RootWidget
        return RootWidget

    if name == "RootAkisiYoneticisi":
        from .root_akisi import RootAkisiYoneticisi

        globals()["RootAkisiYoneticisi"] = RootAkisiYoneticisi
        return RootAkisiYoneticisi

    if name == "RootRootYoneticisi":
        from .yoneticisi import RootYoneticisi as RootRootYoneticisi

        globals()["RootRootYoneticisi"] = RootRootYoneticisi
        return RootRootYoneticisi

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__():
    """
    IDE / introspection tarafında public API görünürlüğünü korur.
    """
    return sorted(set(globals().keys()) | set(__all__))

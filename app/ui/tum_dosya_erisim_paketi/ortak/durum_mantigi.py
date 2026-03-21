# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/ortak/durum_mantigi.py

ROL:
- Tüm dosya erişimi durumunu merkezi olarak okumak
- Android yöneticisi üzerinden gelen bilgiyi UI katmanına sade biçimde taşımak
- Platform dışı ortamlarda güvenli fallback sağlamak

MİMARİ:
- Doğrudan servis import etmez
- Sadece android/yoneticisi.py üzerinden erişir
- UI katmanı bu modüle doğrudan değil, ortak/yoneticisi.py üzerinden erişmelidir

API UYUMLULUK:
- Android API 35 ile uyumludur
- Android dışı ortamlarda güvenli biçimde False döner
- Hata durumunda debug callback varsa bilgi geçer, yoksa sessiz fallback uygular

SURUM: 3
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from kivy.utils import platform


def _debug_yaz(debug, message: str) -> None:
    try:
        if callable(debug):
            debug(str(message))
    except Exception:
        pass


def erisim_durumu_getir(debug=None):
    """
    Tüm dosya erişimi durumunu döndürür.

    Dönüş:
    - True  -> erişim açık
    - False -> erişim kapalı veya Android dışı ortam
    - None  -> durum okunamadı
    """
    if platform != "android":
        return False

    try:
        from app.services.android import AndroidYoneticisi

        android_yoneticisi = AndroidYoneticisi()
        return bool(android_yoneticisi.tum_dosya_erisim_izni_var_mi())

    except Exception as exc:
        _debug_yaz(debug, f"Durum okuma hatası: {exc}")
        return None


def erisim_durumu_metni(durum) -> str:
    """
    Erişim durumunu kullanıcı dostu kısa metne çevirir.
    """
    if durum is True:
        return "Tüm dosya erişimi açık."
    if durum is False:
        return "Tüm dosya erişimi kapalı."
    return "Tüm dosya erişimi durumu okunamadı."


def erisim_destekleniyor_mu() -> bool:
    """
    Mevcut platformda tüm dosya erişimi kontrol akışı destekleniyor mu.
    """
    if platform != "android":
        return False

    try:
        from app.services.android import AndroidYoneticisi

        android_yoneticisi = AndroidYoneticisi()
        return bool(android_yoneticisi.tum_dosya_erisim_destekleniyor_mu())
    except Exception:
        return False
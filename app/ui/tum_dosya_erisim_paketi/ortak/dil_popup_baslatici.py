# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/ortak/dil_popup_baslatici.py

ROL:
- Dil popup akışı için placeholder / stub modül
- Henüz implement edilmemiş özelliğin sistemle uyumlu çalışmasını sağlar

DAVRANIŞ:
- Hiçbir şey yapmaz (no-op)
- Hata fırlatmaz
- İleride gerçek implementasyonla değiştirilebilir

NOT:
- Bu modül bilinçli olarak pasif tutulur
- Yoneticisi üzerinden çağrıldığında sistem kırılmaz

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations


def open_language_popup(*_args, **_kwargs):
    """
    Placeholder fonksiyon.
    Gerçek popup implement edilene kadar sistem uyumluluğu sağlar.
    """
    return None


def show_language_popup(*_args, **_kwargs):
    """
    Alternatif isim desteği (yonetici fallback için).
    """
    return None


def launch_language_popup(*_args, **_kwargs):
    """
    Alternatif isim desteği (yonetici fallback için).
    """
    return None
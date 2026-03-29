# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ortak/ui_thread.py

ROL:
- UI ile ilgili callback ve görsel güncelleme işlemlerini güvenli biçimde
  ana Kivy thread üzerinde çalıştırır
- Background thread / popup callback / servis callback kaynaklı
  "Cannot change graphics instruction outside the main Kivy thread"
  hatasını önlemek için ortak yardımcı katman sağlar
- UI tarafında tek merkezden thread-safe çalıştırma kuralı sunar

MİMARİ:
- UI ortak katmanıdır
- Servis katmanını bilmez
- Kivy Clock üzerinden ana thread'e schedule eder
- Zaten ana thread'deyse çağrıyı doğrudan çalıştırır
- Fail-soft davranır
- Deterministik akış hedefler
- Geriye uyumluluk katmanı içermez

KULLANIM:
- UI güncelleyen callback'ler doğrudan çalıştırılmamalıdır
- Bunun yerine ui_thread_uzerinde_calistir(...) kullanılmalıdır

SURUM: 1
TARIH: 2026-03-29
IMZA: FY.
"""

from __future__ import annotations

import threading
from typing import Callable, TypeVar

from kivy.clock import Clock


T = TypeVar("T")


def ana_thread_mi() -> bool:
    """
    Mevcut akış ana UI thread üzerinde mi kontrol eder.
    """
    try:
        return threading.current_thread() is threading.main_thread()
    except Exception:
        return False


def ui_thread_uzerinde_calistir(
    callback: Callable[..., T] | None,
    *args,
    delay: float = 0.0,
    **kwargs,
) -> bool:
    """
    Callback'i güvenli biçimde ana Kivy thread üzerinde çalıştırır.

    Kurallar:
    - Zaten ana thread'deyse doğrudan çalıştırır
    - Değilse Clock.schedule_once ile ana thread'e alır
    - Hata yutmaz; schedule edilen callback içinde yukarı taşır

    Args:
        callback:
            Çalıştırılacak fonksiyon.
        *args:
            Callback positional argümanları.
        delay:
            Clock.schedule_once gecikmesi.
        **kwargs:
            Callback keyword argümanları.

    Returns:
        bool:
            Çağrı planlandı / çalıştırıldıysa True, callback yoksa False.
    """
    if callback is None:
        return False

    if ana_thread_mi() and float(delay) <= 0.0:
        callback(*args, **kwargs)
        return True

    def _runner(_dt: float) -> None:
        callback(*args, **kwargs)

    Clock.schedule_once(_runner, float(delay))
    return True
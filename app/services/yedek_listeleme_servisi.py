# -*- coding: utf-8 -*-
"""
DOSYA: app/services/yedek_silme_servisi.py

ROL:
- Tek .bak dosyasını silmek
- Birden fazla .bak dosyasını toplu silmek
- Tüm listelenebilir yedekleri silmek

SURUM: 2
TARIH: 2026-03-18
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path

from app.services.yedek_listeleme_servisi import yedekleri_listele


class YedekSilmeServisiHatasi(ValueError):
    """Yedek silme işlemleri sırasında oluşan kontrollü hata."""


def _normalize_backup_path(backup_path: str | Path) -> Path:
    """
    Verilen yolu doğrular ve geçerli bir .bak dosyasına dönüştürür.
    """
    try:
        path_obj = Path(str(backup_path or "").strip())
    except Exception as exc:
        raise YedekSilmeServisiHatasi(
            f"Geçersiz yedek yolu: {exc}"
        ) from exc

    if not str(path_obj).strip():
        raise YedekSilmeServisiHatasi("Yedek yolu boş.")

    if not path_obj.exists() or not path_obj.is_file():
        raise YedekSilmeServisiHatasi("Silinecek yedek dosyası bulunamadı.")

    if not path_obj.name.lower().endswith(".bak"):
        raise YedekSilmeServisiHatasi("Yalnızca .bak uzantılı dosyalar silinebilir.")

    return path_obj


def yedegi_sil(backup_path: str | Path) -> str:
    """
    Tek bir .bak dosyasını siler.

    Geri dönüş:
    - silinen dosya yolu
    """
    path_obj = _normalize_backup_path(backup_path)

    try:
        silinen = str(path_obj)
        path_obj.unlink()
        return silinen
    except Exception as exc:
        raise YedekSilmeServisiHatasi(
            f"Yedek silinemedi: {exc}"
        ) from exc


def coklu_yedek_sil(paths: list[str | Path]) -> int:
    """
    Verilen yedek yollarını toplu siler.

    Geri dönüş:
    - başarıyla silinen dosya sayısı
    """
    if not paths:
        return 0

    silinen_sayi = 0
    hatalar: list[str] = []

    for p in paths:
        try:
            yedegi_sil(p)
            silinen_sayi += 1
        except Exception as exc:
            hatalar.append(str(exc))

    if silinen_sayi <= 0 and hatalar:
        raise YedekSilmeServisiHatasi(
            "Toplu silme başarısız: " + " | ".join(hatalar)
        )

    return silinen_sayi


def tum_yedekleri_sil() -> int:
    """
    Listeleme servisinin gördüğü tüm .bak dosyalarını siler.

    Geri dönüş:
    - silinen toplam dosya sayısı
    """
    try:
        yedekler = yedekleri_listele()
    except Exception as exc:
        raise YedekSilmeServisiHatasi(
            f"Yedekler alınamadı: {exc}"
        ) from exc

    if not yedekler:
        return 0

    return coklu_yedek_sil(yedekler)

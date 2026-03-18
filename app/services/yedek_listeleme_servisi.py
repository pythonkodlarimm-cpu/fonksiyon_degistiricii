# -*- coding: utf-8 -*-
"""
DOSYA: app/services/yedek_listeleme_servisi.py

ROL:
- Yedeklenen dosyaları listelemek
- Yedek klasörünü hazırlamak
- Dosyaları tarih sırasına göre sıralamak
- Hata ayıklama için güvenli log üretmek

MİMARİ:
- Ortak backup klasörü kullanılır
- Yalnızca dosyalar listelenir
- En yeni yedek en üstte olacak şekilde sıralanır
- Hatalı/bozuk kayıtlar listelemeyi komple düşürmez

HEDEF KLASÖR:
- /storage/emulated/0/FonksiyonDegistirici/backups

API UYUMLULUK:
- API 30+ uyumlu
- API 34 test senaryosuna uygun
- Path tabanlı görünür yedek klasörü kullanır

SURUM: 2
TARIH: 2026-03-18
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path


class YedekListelemeServisiHatasi(ValueError):
    """Yedek listeleme sırasında oluşan kontrollü hata."""


def _debug(message: str) -> None:
    try:
        print("[YEDEK_LISTELEME]", str(message))
    except Exception:
        pass


def _backup_root() -> Path:
    """
    Yedek klasörünü döndürür.

    Yoksa oluşturur.
    """
    try:
        root = Path("/storage/emulated/0/FonksiyonDegistirici/backups")
        root.mkdir(parents=True, exist_ok=True)
        _debug(f"backup root hazır: {root}")
        return root
    except Exception as exc:
        raise YedekListelemeServisiHatasi(
            f"Yedek klasörü hazırlanamadı: {exc}"
        ) from exc


def _guvenli_stat_mtime(path_obj: Path) -> float:
    """
    Dosya mtime bilgisini güvenli biçimde döndürür.

    Hata olursa 0 döner, böylece sıralama tamamen çökmez.
    """
    try:
        return float(path_obj.stat().st_mtime)
    except Exception:
        return 0.0


def yedekleri_listele() -> list[Path]:
    """
    Yedek dosyalarını listeler.

    Dönüş:
    - Path listesi (en yeni en üstte)

    API NOTU:
    - Sadece dosyalar listelenir
    - mtime ile sıralanır
    - Bozuk kayıtlar yüzünden tüm listeleme çökmez
    """
    root = _backup_root()

    try:
        dosyalar: list[Path] = []

        for p in root.iterdir():
            try:
                if p.is_file():
                    dosyalar.append(p)
            except Exception as exc:
                _debug(f"öğe atlandı: {p} | hata: {exc}")

        dosyalar.sort(
            key=_guvenli_stat_mtime,
            reverse=True,
        )

        _debug(f"toplam yedek sayısı: {len(dosyalar)}")
        for item in dosyalar[:10]:
            _debug(f"yedek: {item.name}")

        return dosyalar

    except Exception as exc:
        raise YedekListelemeServisiHatasi(
            f"Yedekler listelenemedi: {exc}"
        ) from exc


def yedek_sayisi() -> int:
    """
    Toplam yedek sayısını döndürür.
    """
    try:
        sayi = len(yedekleri_listele())
        _debug(f"yedek sayısı: {sayi}")
        return sayi
    except Exception as exc:
        _debug(f"yedek sayısı alınamadı: {exc}")
        return 0
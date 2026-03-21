# -*- coding: utf-8 -*-
"""
DOSYA: app/services/yedek/listeleme_servisi.py

ROL:
- Sabit yedek klasöründeki yedek dosyalarını akıllı şekilde listelemek
- Tarih, zaman aralığı ve dosya adına göre filtrelemek
- Dosyaları tarih sırasına göre sıralamak
- UI katmanı için zengin metadata üretmek
- Hata ayıklama için güvenli log üretmek

MİMARİ:
- Tek sabit backup kökü kullanılır
- Recursive genel tarama yapılmaz
- Sadece uygulamanın güvenli yedek alanı taranır
- En yeni yedek en üstte olacak şekilde sıralanır
- Hatalı/bozuk kayıtlar listelemeyi komple düşürmez
- Aynı dosya birden fazla kez eklenmez
- Yedek adı içinden zaman damgası ayrıştırılır
- Circular import riskini azaltmak için dosya servisi lazy import ile çağrılır

API UYUMLULUK:
- API 35 uyumlu
- Scoped storage dostu
- Hızlı popup açılışı için optimize edilmiştir
- AdMob entegrasyonundan bağımsız çalışır
- Reklam katmanı olsa da servis davranışı değişmez

DESTEKLENEN FİLTRELER:
- bugün
- dün
- son N gün
- belirli tarih
- dosya adı arama
- belirli gün gruplama

YENİ DOSYA ADI DESTEĞİ:
- ornek.py.ab12cd34ef.20260318_163012.bak

ESKİ DOSYA ADI DESTEĞİ:
- ornek.py.20260318_163012.bak

SURUM: 9
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path


class YedekListelemeServisiHatasi(ValueError):
    """Yedek listeleme sırasında oluşan kontrollü hata."""


# =========================================================
# MODELS
# =========================================================
@dataclass(slots=True)
class YedekKaydi:
    path: Path
    display_name: str
    source_hash: str
    backup_datetime: datetime
    date_key: str
    time_key: str
    timestamp_key: str
    size_bytes: int
    root_label: str

    @property
    def file_name(self) -> str:
        return self.path.name

    @property
    def display_date_text(self) -> str:
        return self.backup_datetime.strftime("%d.%m.%Y")

    @property
    def display_time_text(self) -> str:
        return self.backup_datetime.strftime("%H:%M")

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "file_name": self.file_name,
            "display_name": self.display_name,
            "source_hash": self.source_hash,
            "backup_datetime": self.backup_datetime,
            "date_key": self.date_key,
            "time_key": self.time_key,
            "timestamp_key": self.timestamp_key,
            "size_bytes": self.size_bytes,
            "root_label": self.root_label,
            "display_date_text": self.display_date_text,
            "display_time_text": self.display_time_text,
        }


# =========================================================
# DEBUG
# =========================================================
def _debug(message: str) -> None:
    try:
        print("[YEDEK_LISTELEME]", str(message))
    except Exception:
        pass


# =========================================================
# ROOT HELPERS
# =========================================================
def _get_app_backups_root() -> Path:
    try:
        from app.services.dosya.servisi import get_app_backups_root

        root = get_app_backups_root()
        if isinstance(root, Path):
            return root
        return Path(str(root))
    except Exception as exc:
        raise YedekListelemeServisiHatasi(
            f"Yedek kökü alınamadı: {exc}"
        ) from exc


# =========================================================
# SAFE FILE HELPERS
# =========================================================
def _guvenli_stat_mtime(path_obj: Path) -> float:
    try:
        return float(path_obj.stat().st_mtime)
    except Exception:
        return 0.0


def _guvenli_size(path_obj: Path) -> int:
    try:
        return int(path_obj.stat().st_size)
    except Exception:
        return 0


def _is_backup_file(path_obj: Path) -> bool:
    try:
        return path_obj.is_file() and path_obj.name.lower().endswith(".bak")
    except Exception:
        return False


# =========================================================
# FILENAME PARSE
# =========================================================
_YENI_FORMAT_RE = re.compile(
    r"^(?P<display_name>.+)\.(?P<source_hash>[0-9a-fA-F]{10})\.(?P<ts>\d{8}_\d{6})\.bak$"
)

_ESKI_FORMAT_RE = re.compile(
    r"^(?P<display_name>.+)\.(?P<ts>\d{8}_\d{6})\.bak$"
)


def _parse_timestamp(ts_text: str) -> datetime | None:
    try:
        return datetime.strptime(ts_text, "%Y%m%d_%H%M%S")
    except Exception:
        return None


def _fallback_datetime_from_file(path_obj: Path) -> datetime:
    try:
        return datetime.fromtimestamp(_guvenli_stat_mtime(path_obj))
    except Exception:
        return datetime.now()


def _build_backup_record(path_obj: Path) -> YedekKaydi:
    raw_name = path_obj.name
    display_name = path_obj.stem
    source_hash = ""
    backup_dt: datetime | None = None

    match_new = _YENI_FORMAT_RE.match(raw_name)
    if match_new:
        display_name = str(match_new.group("display_name") or "").strip() or path_obj.stem
        source_hash = str(match_new.group("source_hash") or "").strip()
        backup_dt = _parse_timestamp(str(match_new.group("ts") or "").strip())

    if backup_dt is None:
        match_old = _ESKI_FORMAT_RE.match(raw_name)
        if match_old:
            display_name = str(match_old.group("display_name") or "").strip() or path_obj.stem
            source_hash = ""
            backup_dt = _parse_timestamp(str(match_old.group("ts") or "").strip())

    if backup_dt is None:
        backup_dt = _fallback_datetime_from_file(path_obj)

    return YedekKaydi(
        path=path_obj,
        display_name=display_name,
        source_hash=source_hash,
        backup_datetime=backup_dt,
        date_key=backup_dt.strftime("%Y-%m-%d"),
        time_key=backup_dt.strftime("%H:%M:%S"),
        timestamp_key=backup_dt.strftime("%Y%m%d_%H%M%S"),
        size_bytes=_guvenli_size(path_obj),
        root_label="Uygulama Yedekleri",
    )


# =========================================================
# COLLECT
# =========================================================
def _tum_yedek_kayitlari() -> list[YedekKaydi]:
    try:
        root = _get_app_backups_root()
    except Exception as exc:
        _debug(f"yedek kökü alınamadı: {exc}")
        return []

    try:
        if not root.exists() or not root.is_dir():
            _debug(f"yedek kökü yok/uygun değil: {root}")
            return []
    except Exception:
        return []

    kayitlar: list[YedekKaydi] = []
    gorulenler: set[str] = set()

    try:
        for path_obj in root.iterdir():
            try:
                if not _is_backup_file(path_obj):
                    continue

                try:
                    key = str(path_obj.resolve())
                except Exception:
                    key = str(path_obj)

                if key in gorulenler:
                    continue

                kayitlar.append(_build_backup_record(path_obj))
                gorulenler.add(key)
            except Exception as exc:
                _debug(f"yedek kaydı atlandı: {path_obj} | hata: {exc}")
    except Exception as exc:
        _debug(f"yedek klasörü taranamadı: {root} | hata: {exc}")

    kayitlar.sort(
        key=lambda item: (item.backup_datetime, item.file_name.casefold()),
        reverse=True,
    )
    _debug(f"toplam yedek sayısı: {len(kayitlar)}")
    return kayitlar


# =========================================================
# FILTER
# =========================================================
def _normalize_query(text: str | None) -> str:
    return str(text or "").strip().casefold()


def _normalize_date_input(tarih: str | datetime | None) -> str | None:
    if tarih is None:
        return None

    if isinstance(tarih, datetime):
        return tarih.strftime("%Y-%m-%d")

    raw = str(tarih).strip()
    if not raw:
        return None

    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except Exception:
            continue

    return None


def _apply_filters(
    kayitlar: list[YedekKaydi],
    tarih: str | datetime | None = None,
    bugun: bool = False,
    dun: bool = False,
    son_gun: int | None = None,
    dosya_adi_query: str | None = None,
) -> list[YedekKaydi]:
    filtreli = list(kayitlar)

    query = _normalize_query(dosya_adi_query)
    if query:
        filtreli = [
            item
            for item in filtreli
            if query in item.display_name.casefold()
            or query in item.file_name.casefold()
        ]

    tarih_key = _normalize_date_input(tarih)

    simdi = datetime.now()
    bugun_key = simdi.strftime("%Y-%m-%d")
    dun_key = (simdi - timedelta(days=1)).strftime("%Y-%m-%d")

    if tarih_key:
        filtreli = [item for item in filtreli if item.date_key == tarih_key]
    elif bugun:
        filtreli = [item for item in filtreli if item.date_key == bugun_key]
    elif dun:
        filtreli = [item for item in filtreli if item.date_key == dun_key]
    elif son_gun is not None:
        try:
            gun = max(1, int(son_gun))
        except Exception:
            gun = 1

        esik = simdi - timedelta(days=gun)
        filtreli = [item for item in filtreli if item.backup_datetime >= esik]

    filtreli.sort(
        key=lambda item: (item.backup_datetime, item.file_name.casefold()),
        reverse=True,
    )
    return filtreli


# =========================================================
# PUBLIC API
# =========================================================
def yedekleri_listele(
    tarih: str | datetime | None = None,
    bugun: bool = False,
    dun: bool = False,
    son_gun: int | None = None,
    dosya_adi_query: str | None = None,
) -> list[Path]:
    try:
        kayitlar = _tum_yedek_kayitlari()
        filtreli = _apply_filters(
            kayitlar=kayitlar,
            tarih=tarih,
            bugun=bugun,
            dun=dun,
            son_gun=son_gun,
            dosya_adi_query=dosya_adi_query,
        )
        return [item.path for item in filtreli]
    except Exception as exc:
        raise YedekListelemeServisiHatasi(
            f"Yedekler listelenemedi: {exc}"
        ) from exc


def yedek_kayitlarini_listele(
    tarih: str | datetime | None = None,
    bugun: bool = False,
    dun: bool = False,
    son_gun: int | None = None,
    dosya_adi_query: str | None = None,
) -> list[YedekKaydi]:
    try:
        kayitlar = _tum_yedek_kayitlari()
        return _apply_filters(
            kayitlar=kayitlar,
            tarih=tarih,
            bugun=bugun,
            dun=dun,
            son_gun=son_gun,
            dosya_adi_query=dosya_adi_query,
        )
    except Exception as exc:
        raise YedekListelemeServisiHatasi(
            f"Yedek kayıtları listelenemedi: {exc}"
        ) from exc


def yedek_kayitlarini_dict_listele(
    tarih: str | datetime | None = None,
    bugun: bool = False,
    dun: bool = False,
    son_gun: int | None = None,
    dosya_adi_query: str | None = None,
) -> list[dict]:
    try:
        return [
            item.to_dict()
            for item in yedek_kayitlarini_listele(
                tarih=tarih,
                bugun=bugun,
                dun=dun,
                son_gun=son_gun,
                dosya_adi_query=dosya_adi_query,
            )
        ]
    except Exception as exc:
        raise YedekListelemeServisiHatasi(
            f"Yedek dict kayıtları listelenemedi: {exc}"
        ) from exc


def yedekleri_tarihe_gore_grupla(
    tarih: str | datetime | None = None,
    bugun: bool = False,
    dun: bool = False,
    son_gun: int | None = None,
    dosya_adi_query: str | None = None,
) -> dict[str, list[YedekKaydi]]:
    try:
        kayitlar = yedek_kayitlarini_listele(
            tarih=tarih,
            bugun=bugun,
            dun=dun,
            son_gun=son_gun,
            dosya_adi_query=dosya_adi_query,
        )

        gruplar: dict[str, list[YedekKaydi]] = {}
        for item in kayitlar:
            gruplar.setdefault(item.date_key, []).append(item)

        return gruplar
    except Exception as exc:
        raise YedekListelemeServisiHatasi(
            f"Yedekler tarihe göre gruplanamadı: {exc}"
        ) from exc


def uygun_tarih_anahtarlari() -> list[str]:
    try:
        keys = {item.date_key for item in _tum_yedek_kayitlari()}
        return sorted(keys, reverse=True)
    except Exception as exc:
        _debug(f"uygun tarih anahtarları alınamadı: {exc}")
        return []


def yedek_sayisi(
    tarih: str | datetime | None = None,
    bugun: bool = False,
    dun: bool = False,
    son_gun: int | None = None,
    dosya_adi_query: str | None = None,
) -> int:
    try:
        sayi = len(
            yedekleri_listele(
                tarih=tarih,
                bugun=bugun,
                dun=dun,
                son_gun=son_gun,
                dosya_adi_query=dosya_adi_query,
            )
        )
        _debug(f"yedek sayısı: {sayi}")
        return sayi
    except Exception as exc:
        _debug(f"yedek sayısı alınamadı: {exc}")
        return 0
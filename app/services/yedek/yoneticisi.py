# -*- coding: utf-8 -*-
"""
DOSYA: app/services/yedek/yoneticisi.py

ROL:
- Yedek katmanına tek giriş noktası sağlamak
- UI ve diğer katmanların alt yedek servis detaylarını bilmesini engellemek
- Listeleme, indirme ve silme akışlarını merkezileştirmek

MİMARİ:
- Alt yedek servislerine lazy import ile erişir
- UI katmanı sadece bu yöneticiyi bilir
- Yedek katmanının iç yapısını dış dünyadan saklar
- Listeleme, indirme ve silme davranışını tek yerden toplar

API UYUMLULUK:
- API 35 uyumlu
- Scoped storage dostu
- Reklam ve UI katmanından bağımsız çalışır

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


class YedekYoneticisi:
    # =========================================================
    # LISTELEME
    # =========================================================
    def yedekleri_listele(
        self,
        tarih: str | datetime | None = None,
        bugun: bool = False,
        dun: bool = False,
        son_gun: int | None = None,
        dosya_adi_query: str | None = None,
    ) -> list[Path]:
        from app.services.yedek.listeleme_servisi import yedekleri_listele
        return yedekleri_listele(
            tarih=tarih,
            bugun=bugun,
            dun=dun,
            son_gun=son_gun,
            dosya_adi_query=dosya_adi_query,
        )

    def yedek_kayitlarini_listele(
        self,
        tarih: str | datetime | None = None,
        bugun: bool = False,
        dun: bool = False,
        son_gun: int | None = None,
        dosya_adi_query: str | None = None,
    ):
        from app.services.yedek.listeleme_servisi import yedek_kayitlarini_listele
        return yedek_kayitlarini_listele(
            tarih=tarih,
            bugun=bugun,
            dun=dun,
            son_gun=son_gun,
            dosya_adi_query=dosya_adi_query,
        )

    def yedek_kayitlarini_dict_listele(
        self,
        tarih: str | datetime | None = None,
        bugun: bool = False,
        dun: bool = False,
        son_gun: int | None = None,
        dosya_adi_query: str | None = None,
    ) -> list[dict]:
        from app.services.yedek.listeleme_servisi import yedek_kayitlarini_dict_listele
        return yedek_kayitlarini_dict_listele(
            tarih=tarih,
            bugun=bugun,
            dun=dun,
            son_gun=son_gun,
            dosya_adi_query=dosya_adi_query,
        )

    def yedekleri_tarihe_gore_grupla(
        self,
        tarih: str | datetime | None = None,
        bugun: bool = False,
        dun: bool = False,
        son_gun: int | None = None,
        dosya_adi_query: str | None = None,
    ):
        from app.services.yedek.listeleme_servisi import yedekleri_tarihe_gore_grupla
        return yedekleri_tarihe_gore_grupla(
            tarih=tarih,
            bugun=bugun,
            dun=dun,
            son_gun=son_gun,
            dosya_adi_query=dosya_adi_query,
        )

    def uygun_tarih_anahtarlari(self) -> list[str]:
        from app.services.yedek.listeleme_servisi import uygun_tarih_anahtarlari
        return uygun_tarih_anahtarlari()

    def yedek_sayisi(
        self,
        tarih: str | datetime | None = None,
        bugun: bool = False,
        dun: bool = False,
        son_gun: int | None = None,
        dosya_adi_query: str | None = None,
    ) -> int:
        from app.services.yedek.listeleme_servisi import yedek_sayisi
        return yedek_sayisi(
            tarih=tarih,
            bugun=bugun,
            dun=dun,
            son_gun=son_gun,
            dosya_adi_query=dosya_adi_query,
        )

    # =========================================================
    # INDIRME
    # =========================================================
    def yedegi_indir(self, backup_path: str | Path, hedef_klasor: str | Path) -> str:
        from app.services.yedek.indirme_servisi import yedegi_indir
        return yedegi_indir(backup_path, hedef_klasor)

    def yedegi_indir_varsayilan(self, backup_path: str | Path) -> str:
        from app.services.yedek.indirme_servisi import yedegi_indir_varsayilan
        return yedegi_indir_varsayilan(backup_path)

    # =========================================================
    # SILME
    # =========================================================
    def yedegi_sil(self, backup_path: str | Path) -> str:
        from app.services.yedek.silme_servisi import yedegi_sil
        return yedegi_sil(backup_path)

    def coklu_yedek_sil(self, paths: list[str | Path]) -> int:
        from app.services.yedek.silme_servisi import coklu_yedek_sil
        return coklu_yedek_sil(paths)

    def tum_yedekleri_sil(self) -> int:
        from app.services.yedek.silme_servisi import tum_yedekleri_sil
        return tum_yedekleri_sil()
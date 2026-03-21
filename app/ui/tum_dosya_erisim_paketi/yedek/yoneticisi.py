# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/yedek/yoneticisi.py

ROL:
- Tüm dosya erişim paketi içindeki yedek UI akışlarına tek giriş noktası sağlamak
- Yedek satırı, indirme işlemi ve dosya yolu açma akışını merkezileştirmek
- Üst katmanın alt modül detaylarını bilmesini engellemek

MİMARİ:
- Lazy import kullanır
- UI katmanı bu alt modüllere doğrudan değil, bu yönetici üzerinden erişir
- Yedekle ilgili tekrar kullanılabilir akışlar burada toplanır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 1
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations


class TumDosyaErisimYedekYoneticisi:
    # =========================================================
    # BACKUP ROW
    # =========================================================
    def yedek_satiri_olustur(self, yedek, on_view, on_download, on_delete):
        from app.ui.tum_dosya_erisim_paketi.yedek.yedek_satiri import (
            build_backup_row,
        )

        return build_backup_row(
            yedek=yedek,
            on_view=on_view,
            on_download=on_download,
            on_delete=on_delete,
        )

    # =========================================================
    # DOWNLOAD ACTION
    # =========================================================
    def yedek_indirme_islemi_baslat(
        self,
        debug,
        yedek,
        hedef_klasor=None,
    ):
        from app.ui.tum_dosya_erisim_paketi.yedek.yedek_indirme_islemi import (
            backup_download_action,
        )

        return backup_download_action(
            debug=debug,
            yedek=yedek,
            hedef_klasor=hedef_klasor,
        )

    # =========================================================
    # FILE MANAGER OPEN
    # =========================================================
    def dosya_yolu_ac(self, path_value, debug=None) -> bool:
        from app.ui.tum_dosya_erisim_paketi.yedek.dosya_yolu_acici import (
            open_path_in_file_manager,
        )

        return bool(
            open_path_in_file_manager(
                path_value=path_value,
                debug=debug,
            )
        )
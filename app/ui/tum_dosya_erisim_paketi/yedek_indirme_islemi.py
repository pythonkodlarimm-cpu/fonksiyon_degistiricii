# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from app.ui.tum_dosya_erisim_paketi.basit_popup import show_simple_popup
from app.ui.tum_dosya_erisim_paketi.indirme_sonuc_popup import (
    show_download_result_popup,
)


def backup_download_action(
    debug,
    yedek: Path,
    hedef_klasor: str | Path | None = None,
):
    try:
        from app.services.yedek_indirme_servisi import (
            yedegi_indir,
            yedegi_indir_varsayilan,
        )

        kullanici_secimli = bool(
            hedef_klasor is not None and str(hedef_klasor).strip()
        )

        if kullanici_secimli:
            hedef = yedegi_indir(yedek, hedef_klasor)
        else:
            hedef = yedegi_indir_varsayilan(yedek)

        try:
            if debug:
                debug(f"Yedek kopyalandı: {hedef}")
        except Exception:
            pass

        show_download_result_popup(
            saved_path=hedef,
            selected_by_user=kullanici_secimli,
        )
        return hedef

    except Exception as exc:
        try:
            if debug:
                debug(f"Yedek indirme hatası: {exc}")
        except Exception:
            pass

        show_simple_popup(
            title_text="İndirme Hatası",
            body_text=f"Yedek kopyalanamadı:\n{exc}",
            icon_name="warning.png",
            auto_close_seconds=1.8,
            compact=True,
        )
        raise
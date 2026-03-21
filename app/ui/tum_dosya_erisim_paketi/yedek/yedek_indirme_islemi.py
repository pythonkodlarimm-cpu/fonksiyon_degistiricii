# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/yedek/yedek_indirme_islemi.py

ROL:
- Seçilen yedeği kullanıcı hedef klasörüne veya varsayılan konuma kopyalamak
- İşlem sonucunu popup ile kullanıcıya göstermek
- Hata durumunda sade uyarı popup'ı açmak

MİMARİ:
- Popup modüllerine doğrudan gitmez
- Popups yoneticisi üzerinden erişir
- Servis katmanına doğrudan eski modül yolu ile değil, YedekYoneticisi üzerinden gider

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 2
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path


def _yedek_yoneticisi():
    from app.services.yedek import YedekYoneticisi
    return YedekYoneticisi()


def _popups_yoneticisi():
    from app.ui.tum_dosya_erisim_paketi.popups import TumDosyaErisimPopupsYoneticisi
    return TumDosyaErisimPopupsYoneticisi()


def _safe_debug(debug, message: str) -> None:
    try:
        if callable(debug):
            debug(str(message))
    except Exception:
        pass


def backup_download_action(
    debug,
    yedek: Path,
    hedef_klasor: str | Path | None = None,
):
    yedek_yoneticisi = _yedek_yoneticisi()
    popups = _popups_yoneticisi()

    try:
        kullanici_secimli = bool(
            hedef_klasor is not None and str(hedef_klasor).strip()
        )

        if kullanici_secimli:
            hedef = yedek_yoneticisi.yedegi_indir(yedek, hedef_klasor)
        else:
            hedef = yedek_yoneticisi.yedegi_indir_varsayilan(yedek)

        _safe_debug(debug, f"Yedek kopyalandı: {hedef}")

        popups.show_download_result_popup(
            saved_path=hedef,
            selected_by_user=kullanici_secimli,
        )
        return hedef

    except Exception as exc:
        _safe_debug(debug, f"Yedek indirme hatası: {exc}")

        popups.show_simple_popup(
            title_text="İndirme Hatası",
            body_text=f"Yedek kopyalanamadı:\n{exc}",
            icon_name="warning.png",
            auto_close_seconds=1.8,
            compact=True,
        )
        raise
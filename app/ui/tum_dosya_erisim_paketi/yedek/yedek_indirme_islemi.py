# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/yedek/yedek_indirme_islemi.py

ROL:
- Seçilen yedeği kullanıcı hedef klasörüne veya varsayılan konuma kopyalamak
- İşlem sonucunu popup ile kullanıcıya göstermek
- Hata durumunda sade uyarı popup'ı açmak

MİMARİ:
- Popup modüllerine doğrudan gitmez
- Popups yöneticisi üzerinden erişir
- Servis katmanına doğrudan eski modül yolu ile değil, YedekYoneticisi üzerinden gider

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez
- Mevcut fonksiyon imzası korunmuştur

SURUM: 3
TARIH: 2026-03-22
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


def _path_to_text(value: str | Path | None) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _path_to_name(value: str | Path | None) -> str:
    metin = _path_to_text(value)
    if not metin:
        return ""
    try:
        return Path(metin).name
    except Exception:
        return metin


def backup_download_action(
    debug,
    yedek: Path,
    hedef_klasor: str | Path | None = None,
):
    """
    Verilen yedek dosyasını indirir / kopyalar.

    Parametre:
    - debug: opsiyonel debug callback
    - yedek: indirilecek .bak dosyası
    - hedef_klasor: kullanıcı tarafından seçilmiş hedef klasör

    Dönüş:
    - hedef: oluşan hedef dosya yolu

    Hata:
    - Exception tekrar yükseltilir
    """

    yedek_yoneticisi = _yedek_yoneticisi()
    popups = _popups_yoneticisi()

    try:
        yedek = Path(yedek)

        if not yedek.exists():
            raise FileNotFoundError(f"Yedek bulunamadı: {yedek}")

        if not yedek.is_file():
            raise FileNotFoundError(f"Geçerli bir yedek dosyası değil: {yedek}")

        hedef_metin = _path_to_text(hedef_klasor)
        kullanici_secimli = bool(hedef_metin)

        _safe_debug(debug, f"İndirme isteği alındı: {yedek}")
        _safe_debug(debug, f"Hedef klasör: {hedef_metin or '[varsayılan]'}")

        if kullanici_secimli:
            hedef = yedek_yoneticisi.yedegi_indir(yedek, hedef_metin)
        else:
            hedef = yedek_yoneticisi.yedegi_indir_varsayilan(yedek)

        hedef = Path(hedef)

        if not hedef.exists():
            raise FileNotFoundError(f"İndirilen hedef dosya oluşmadı: {hedef}")

        _safe_debug(debug, f"Yedek kopyalandı: {hedef}")

        popups.show_download_result_popup(
            saved_path=hedef,
            selected_by_user=kullanici_secimli,
        )

        return hedef

    except Exception as exc:
        _safe_debug(debug, f"Yedek indirme hatası: {exc}")

        hedef_ad = _path_to_name(hedef_klasor)
        ek_metin = ""

        if hedef_ad:
            ek_metin = f"\nHedef klasör: {hedef_ad}"

        popups.show_simple_popup(
            title_text="İndirme Hatası",
            body_text=f"Yedek kopyalanamadı:\n{exc}{ek_metin}",
            icon_name="warning.png",
            auto_close_seconds=1.8,
            compact=True,
        )
        raise
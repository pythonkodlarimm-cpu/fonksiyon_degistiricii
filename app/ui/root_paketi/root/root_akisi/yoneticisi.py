# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/yonetici.py

ROL:
- root_akisi altındaki modüllere merkezi erişim sağlar
- Lazy import ile modülleri yalnızca gerektiğinde yükler
- Başarılı yüklenen modülleri cache içinde tutar
- Alt akış modüllerini root katmanından izole eder
- Fail-soft yaklaşım uygular

MİMARİ:
- Her akış için ayrı accessor metodu vardır
- Modüller ihtiyaç anında yüklenir
- Başarılı import sonrası modül referansı saklanır
- Alt modüllere erişim bu yönetici üzerinden yapılır

ERISILEN AKISLAR:
- dil_yardimcilari
- editor_state
- sistem_ve_app_state
- gecici_status
- guncelleme_cta_ve_surum_kontrol
- gecis_reklami_on_yukleme
- banner_akisi
- tarama_gecis_ve_liste_acma
- dil_akisi
- ui_kurulumu
- app_state_kaydet_geri_yukle

SURUM: 7
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations


class RootAkisiYoneticisi:
    """
    root/root_akisi altındaki modüller için merkezi erişim yöneticisi.
    """

    MODULLER = {
        "dil_yardimcilari": "app.ui.root_paketi.root.root_akisi.dil_yardimcilari",
        "editor_state": "app.ui.root_paketi.root.root_akisi.editor_state",
        "sistem_ve_app_state": "app.ui.root_paketi.root.root_akisi.sistem_ve_app_state",
        "gecici_status": "app.ui.root_paketi.root.root_akisi.gecici_status",
        "guncelleme_cta_ve_surum_kontrol": (
            "app.ui.root_paketi.root.root_akisi.guncelleme_cta_ve_surum_kontrol"
        ),
        "gecis_reklami_on_yukleme": (
            "app.ui.root_paketi.root.root_akisi.gecis_reklami_on_yukleme"
        ),
        "banner_akisi": "app.ui.root_paketi.root.root_akisi.banner_akisi",
        "tarama_gecis_ve_liste_acma": (
            "app.ui.root_paketi.root.root_akisi.tarama_gecis_ve_liste_acma"
        ),
        "dil_akisi": "app.ui.root_paketi.root.root_akisi.dil_akisi",
        "ui_kurulumu": "app.ui.root_paketi.root.root_akisi.ui_kurulumu",
        "app_state_kaydet_geri_yukle": (
            "app.ui.root_paketi.root.root_akisi.app_state_kaydet_geri_yukle"
        ),
    }

    def __init__(self) -> None:
        self._modul_cache: dict[str, object] = {}

    def cache_temizle(self) -> None:
        """
        Tüm modül cache kayıtlarını temizler.
        """
        self._modul_cache = {}

    def _modul_yukle(self, anahtar: str):
        """
        Verilen anahtara karşılık gelen modülü lazy import ile yükler.

        Args:
            anahtar: MODULLER sözlüğündeki modül anahtarı.

        Returns:
            module | None
        """
        if anahtar in self._modul_cache:
            return self._modul_cache.get(anahtar)

        import_yolu = self.MODULLER.get(anahtar)
        if not import_yolu:
            print(f"[ROOT_AKISI] Bilinmeyen modül anahtarı: {anahtar}")
            return None

        try:
            modul = __import__(import_yolu, fromlist=["*"])
        except Exception as exc:
            print(f"[ROOT_AKISI] Modül yüklenemedi: {import_yolu}")
            print(exc)
            self._modul_cache.pop(anahtar, None)
            return None

        self._modul_cache[anahtar] = modul
        return modul

    def dil_yardimcilari(self):
        """
        Dil yardımcıları akış modülünü döndürür.
        """
        return self._modul_yukle("dil_yardimcilari")

    def editor_state(self):
        """
        Editör state akış modülünü döndürür.
        """
        return self._modul_yukle("editor_state")

    def sistem_ve_app_state(self):
        """
        Sistem ve app state akış modülünü döndürür.
        """
        return self._modul_yukle("sistem_ve_app_state")

    def gecici_status(self):
        """
        Geçici status akış modülünü döndürür.
        """
        return self._modul_yukle("gecici_status")

    def guncelleme_cta_ve_surum_kontrol(self):
        """
        Güncelleme CTA ve sürüm kontrol akış modülünü döndürür.
        """
        return self._modul_yukle("guncelleme_cta_ve_surum_kontrol")

    def gecis_reklami_on_yukleme(self):
        """
        Geçiş reklamı ön yükleme akış modülünü döndürür.
        """
        return self._modul_yukle("gecis_reklami_on_yukleme")

    def banner_akisi(self):
        """
        Banner akış modülünü döndürür.
        """
        return self._modul_yukle("banner_akisi")

    def tarama_gecis_ve_liste_acma(self):
        """
        Tarama geçiş ve liste açma akış modülünü döndürür.
        """
        return self._modul_yukle("tarama_gecis_ve_liste_acma")

    def dil_akisi(self):
        """
        Dil akışı modülünü döndürür.
        """
        return self._modul_yukle("dil_akisi")

    def ui_kurulumu(self):
        """
        UI kurulumu akış modülünü döndürür.
        """
        return self._modul_yukle("ui_kurulumu")

    def app_state_kaydet_geri_yukle(self):
        """
        App state kaydet / geri yükle akış modülünü döndürür.
        """
        return self._modul_yukle("app_state_kaydet_geri_yukle")

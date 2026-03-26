# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/yonetici.py

ROL:
- root_akisi altındaki tüm akış modüllerine tek noktadan erişim sağlar
- Lazy import ve cache sistemi ile modülleri yalnızca gerektiğinde yükler
- Alt akış paketlerini root katmanından izole eder
- Tüm akışlara merkezi yöneticiden erişim sağlar
- Erişim politikası olarak alt modüllere bu dosya üzerinden ulaşılmasını hedefler
- Android ve AAB ortamında tekrar eden import maliyetini azaltacak şekilde çalışır

MİMARİ:
- Her akış için ayrı accessor vardır
- Modüller sadece ihtiyaç halinde import edilir
- İlk başarılı import sonrası modül referansı cache içinde tutulur
- Fail-soft yaklaşım uygulanır; hata durumunda log basılır ve None döner
- İstenirse cache temizlenerek modüller yeniden çözümlenebilir
- Alt paketlerin kendi __init__.py lazy export sistemi ile uyumludur
- Cache bozulursa kendini toparlayacak şekilde yeniden resolve yapabilir
- Alt modüllere erişim doğrudan değil, bu yönetici üzerinden yapılmalıdır

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

KULLANIM:
- yonetici = RootAkisiYoneticisi()
- paket = yonetici.dil_yardimcilari()
- paket = yonetici.editor_state()
- paket = yonetici.ui_kurulumu()

NOT:
- Bu dosya widget üretmez
- Bu dosya root örneği oluşturmaz
- Sadece modül erişimini merkezi hale getirir
- root/root_akisi klasör yapısına göre import yolları güncellenmiştir
- Geliştirme sırasında hot-reload veya kısmi dosya değişimlerinde cache temizlenebilir

SURUM: 6
TARIH: 2026-03-26
IMZA: FY.
"""

from __future__ import annotations

import traceback


class RootAkisiYoneticisi:
    """
    root/root_akisi altındaki tüm modüller için merkezi erişim yöneticisi.
    """

    def __init__(self) -> None:
        self._cached_modules: dict[str, object] = {}

    # =========================================================
    # CACHE
    # =========================================================
    def _cache_get(self, import_path: str):
        """
        Modül cache içinden değer döndürür.

        Args:
            import_path: Modül import yolu.

        Returns:
            module | None
        """
        try:
            return self._cached_modules.get(import_path)
        except Exception:
            return None

    def _cache_set(self, import_path: str, module) -> None:
        """
        Modül cache içine değer yazar.

        Args:
            import_path: Modül import yolu.
            module: Cache'lenecek modül.
        """
        try:
            self._cached_modules[import_path] = module
        except Exception:
            pass

    def _cache_delete(self, import_path: str) -> None:
        """
        Tek bir modül cache kaydını siler.

        Args:
            import_path: Modül import yolu.
        """
        try:
            if import_path in self._cached_modules:
                del self._cached_modules[import_path]
        except Exception:
            pass

    def cache_temizle(self) -> None:
        """
        Tüm modül cache'lerini temizler.
        """
        try:
            self._cached_modules = {}
        except Exception:
            pass

    # =========================================================
    # INTERNAL
    # =========================================================
    def _modul_gecerli_mi(self, module) -> bool:
        """
        Cache içindeki modül nesnesinin geçerli olup olmadığını kontrol eder.

        Args:
            module: Kontrol edilecek modül.

        Returns:
            bool
        """
        try:
            return module is not None and hasattr(module, "__name__")
        except Exception:
            return False

    def _yukle(self, import_path: str):
        """
        Modülü lazy import + cache ile yükler.

        Args:
            import_path: Yüklenecek modül yolu.

        Returns:
            module | None
        """
        try:
            cached = self._cache_get(import_path)
            if cached is not None and self._modul_gecerli_mi(cached):
                return cached
        except Exception:
            self._cache_delete(import_path)

        try:
            module = __import__(import_path, fromlist=["*"])

            if not self._modul_gecerli_mi(module):
                print(
                    "[ROOT_AKISI] modül yüklendi ama geçerli görünmedi: "
                    f"{import_path}"
                )
                self._cache_delete(import_path)
                return None

            self._cache_set(import_path, module)
            return module
        except Exception:
            print(f"[ROOT_AKISI] modül yüklenemedi: {import_path}")
            print(traceback.format_exc())
            self._cache_delete(import_path)
            return None

    # =========================================================
    # DIL YARDIMCILARI
    # =========================================================
    def dil_yardimcilari(self):
        """
        Dil yardımcıları akış modülünü döndürür.
        """
        return self._yukle(
            "app.ui.root_paketi.root.root_akisi.dil_yardimcilari"
        )

    # =========================================================
    # EDITOR STATE
    # =========================================================
    def editor_state(self):
        """
        Editör state akış modülünü döndürür.
        """
        return self._yukle(
            "app.ui.root_paketi.root.root_akisi.editor_state"
        )

    # =========================================================
    # SISTEM / APP STATE
    # =========================================================
    def sistem_ve_app_state(self):
        """
        Sistem ve app state akış modülünü döndürür.
        """
        return self._yukle(
            "app.ui.root_paketi.root.root_akisi.sistem_ve_app_state"
        )

    def sistem_state(self):
        """
        Geriye uyumlu kısa ad.
        """
        return self.sistem_ve_app_state()

    # =========================================================
    # GECICI STATUS
    # =========================================================
    def gecici_status(self):
        """
        Geçici status akış modülünü döndürür.
        """
        return self._yukle(
            "app.ui.root_paketi.root.root_akisi.gecici_status"
        )

    # =========================================================
    # GUNCELLEME CTA / SURUM KONTROL
    # =========================================================
    def guncelleme_cta_ve_surum_kontrol(self):
        """
        Güncelleme CTA ve sürüm kontrol akış modülünü döndürür.
        """
        return self._yukle(
            "app.ui.root_paketi.root.root_akisi.guncelleme_cta_ve_surum_kontrol"
        )

    def guncelleme(self):
        """
        Geriye uyumlu kısa ad.
        """
        return self.guncelleme_cta_ve_surum_kontrol()

    # =========================================================
    # GECIS REKLAMI ON YUKLEME
    # =========================================================
    def gecis_reklami_on_yukleme(self):
        """
        Geçiş reklamı ön yükleme akış modülünü döndürür.
        """
        return self._yukle(
            "app.ui.root_paketi.root.root_akisi.gecis_reklami_on_yukleme"
        )

    # =========================================================
    # BANNER AKISI
    # =========================================================
    def banner_akisi(self):
        """
        Banner akış modülünü döndürür.
        """
        return self._yukle(
            "app.ui.root_paketi.root.root_akisi.banner_akisi"
        )

    # =========================================================
    # TARAMA GECIS VE LISTE ACMA
    # =========================================================
    def tarama_gecis_ve_liste_acma(self):
        """
        Tarama geçiş ve liste açma akış modülünü döndürür.
        """
        return self._yukle(
            "app.ui.root_paketi.root.root_akisi.tarama_gecis_ve_liste_acma"
        )

    def tarama_gecis(self):
        """
        Geriye uyumlu kısa ad.
        """
        return self.tarama_gecis_ve_liste_acma()

    # =========================================================
    # DIL AKISI
    # =========================================================
    def dil_akisi(self):
        """
        Dil akışı modülünü döndürür.
        """
        return self._yukle(
            "app.ui.root_paketi.root.root_akisi.dil_akisi"
        )

    # =========================================================
    # UI KURULUMU
    # =========================================================
    def ui_kurulumu(self):
        """
        UI kurulumu akış modülünü döndürür.
        """
        return self._yukle(
            "app.ui.root_paketi.root.root_akisi.ui_kurulumu"
        )

    # =========================================================
    # APP STATE KAYDET / GERI YUKLE
    # =========================================================
    def app_state_kaydet_geri_yukle(self):
        """
        App state kaydet / geri yükle akış modülünü döndürür.
        """
        return self._yukle(
            "app.ui.root_paketi.root.root_akisi.app_state_kaydet_geri_yukle"
        )

    def app_state(self):
        """
        Geriye uyumlu kısa ad.
        """
        return self.app_state_kaydet_geri_yukle()

    # =========================================================
    # ALIAS / TOPLU ERISIM
    # =========================================================
    def dil(self):
        """
        Geriye uyumlu kısa alias.
        """
        return self.dil_akisi()

    def ui(self):
        """
        Geriye uyumlu kısa alias.
        """
        return self.ui_kurulumu()

    def editor(self):
        """
        Geriye uyumlu kısa alias.
        """
        return self.editor_state()

    def tum_moduller(self) -> dict[str, object | None]:
        """
        Tüm root_akisi modüllerini bir sözlük halinde döndürür.

        Returns:
            dict[str, object | None]
        """
        return {
            "dil_yardimcilari": self.dil_yardimcilari(),
            "editor_state": self.editor_state(),
            "sistem_ve_app_state": self.sistem_ve_app_state(),
            "gecici_status": self.gecici_status(),
            "guncelleme_cta_ve_surum_kontrol": self.guncelleme_cta_ve_surum_kontrol(),
            "gecis_reklami_on_yukleme": self.gecis_reklami_on_yukleme(),
            "banner_akisi": self.banner_akisi(),
            "tarama_gecis_ve_liste_acma": self.tarama_gecis_ve_liste_acma(),
            "dil_akisi": self.dil_akisi(),
            "ui_kurulumu": self.ui_kurulumu(),
            "app_state_kaydet_geri_yukle": self.app_state_kaydet_geri_yukle(),
        }

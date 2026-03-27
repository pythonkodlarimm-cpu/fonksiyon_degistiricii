# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/root_paketi/root/root_akisi/editor_state/yonetici.py

ROL:
- Editor state modülü için merkezi erişim sağlar
- RootEditorStateMixin sınıfını lazy import ile yükler
- Modül ve sınıf referansını cache içinde tutar
- Fail-soft yaklaşım uygular

MİMARİ:
- Modül seviyesinde zorunlu import yapmaz
- İhtiyaç anında hedef modülü yükler
- Başarılı yükleme sonrası modül ve sınıf referansını saklar
- Widget üretmez
- Root örneği oluşturmaz

SURUM: 5
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations


class RootEditorStateYonetici:
    """
    Editor state modülü için merkezi erişim yöneticisi.
    """

    MODUL_YOLU = "app.ui.root_paketi.root.root_akisi.editor_state.editor_state"
    SINIF_ADI = "RootEditorStateMixin"

    def __init__(self) -> None:
        self._modul = None
        self._mixin_sinifi = None

    def cache_temizle(self) -> None:
        """
        Modül ve sınıf cache alanlarını temizler.
        """
        self._modul = None
        self._mixin_sinifi = None

    def _modul_yukle(self):
        """
        Hedef modülü lazy import ile yükler.

        Returns:
            module | None
        """
        if self._modul is not None:
            return self._modul

        try:
            modul = __import__(self.MODUL_YOLU, fromlist=[self.SINIF_ADI])
        except Exception as exc:
            print(f"[ROOT_EDITOR_STATE] Modül yüklenemedi: {self.MODUL_YOLU}")
            print(exc)
            self._modul = None
            return None

        if not hasattr(modul, self.SINIF_ADI):
            print(
                "[ROOT_EDITOR_STATE] "
                f"Beklenen sınıf bulunamadı: {self.MODUL_YOLU}.{self.SINIF_ADI}"
            )
            self._modul = None
            return None

        self._modul = modul
        return modul

    def _mixin_sinifini_yukle(self):
        """
        RootEditorStateMixin sınıfını yükler.

        Returns:
            type | None
        """
        if self._mixin_sinifi is not None:
            return self._mixin_sinifi

        modul = self._modul_yukle()
        if modul is None:
            return None

        try:
            sinif = getattr(modul, self.SINIF_ADI, None)
        except Exception as exc:
            print(f"[ROOT_EDITOR_STATE] Sınıf alınamadı: {self.SINIF_ADI}")
            print(exc)
            self._mixin_sinifi = None
            return None

        if sinif is None:
            print(f"[ROOT_EDITOR_STATE] Sınıf bulunamadı: {self.SINIF_ADI}")
            self._mixin_sinifi = None
            return None

        self._mixin_sinifi = sinif
        return sinif

    def modul(self):
        """
        Editor state modül nesnesini döndürür.

        Returns:
            module | None
        """
        return self._modul_yukle()

    def mixin_sinifi(self):
        """
        RootEditorStateMixin sınıfını döndürür.

        Returns:
            type | None
        """
        return self._mixin_sinifini_yukle()

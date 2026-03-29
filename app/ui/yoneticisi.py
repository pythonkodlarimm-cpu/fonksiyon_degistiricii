# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/yoneticisi.py

ROL:
- UI katmanı için merkezi giriş sağlar
- Ana root widget üretimini tek noktada toplar
- UI alt bileşenlerini ve ekranlarını servis odaklı yapıya bağlar
- UI ortak katman guard kontrolünü root üretiminden önce çalıştırır

MİMARİ:
- Lazy load + kesin instance cache
- Deterministik davranış
- UI yalnızca service katmanını bilir
- Core doğrudan UI tarafından kullanılmaz
- UI guard kontrolü UI katmanı içinde yapılır
- Geriye uyumluluk katmanı içermez

SURUM: 3
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.services import ServisYoneticisi

if TYPE_CHECKING:
    from app.ui.ekranlar.ana_ekran import AnaEkran


class UIYoneticisi:
    """
    UI facade yöneticisi.

    Sorumlulukları:
    - servis yöneticisini yaşam döngüsü boyunca tek instance olarak tutmak
    - UI guard kontrolünü bir kez çalıştırmak
    - ana ekran sınıfını lazy import ile çözmek
    - uygulama root widget'ını üretmek
    """

    __slots__ = (
        "_services",
        "_ana_ekran_cls",
        "_guard_kontrol_edildi",
    )

    def __init__(self) -> None:
        """
        UI yöneticisini oluşturur.
        """
        self._services = ServisYoneticisi()
        self._ana_ekran_cls: type[AnaEkran] | None = None
        self._guard_kontrol_edildi: bool = False

    # =========================================================
    # PUBLIC
    # =========================================================
    def servisler(self) -> ServisYoneticisi:
        """
        UI katmanında kullanılacak servis yöneticisini döndürür.

        Returns:
            ServisYoneticisi: Tekil servis yöneticisi instance'ı.
        """
        return self._services

    # =========================================================
    # INTERNAL
    # =========================================================
    def _ui_guard_kontrolu(self) -> None:
        """
        UI ortak katman guard denetimini yalnızca bir kez çalıştırır.

        Guard başarılıysa sonuç cache'lenir ve tekrar çalıştırılmaz.
        """
        if self._guard_kontrol_edildi:
            return

        from app.ui.ortak.guard import ui_guard_kontrolu

        ui_guard_kontrolu()
        self._guard_kontrol_edildi = True

    def _ana_ekran_sinifi(self) -> type[AnaEkran]:
        """
        Ana ekran sınıfını lazy import ile çözer ve cache'ler.

        Returns:
            type[AnaEkran]: Ana ekran sınıfı.
        """
        cls = self._ana_ekran_cls
        if cls is not None:
            return cls

        from app.ui.ekranlar.ana_ekran import AnaEkran

        self._ana_ekran_cls = AnaEkran
        return AnaEkran

    # =========================================================
    # ROOT
    # =========================================================
    def create_root(self) -> AnaEkran:
        """
        Uygulamanın ana root widget'ını üretir.

        Akış:
        - önce UI guard kontrolü yapılır
        - sonra ana ekran sınıfı çözülür
        - en sonunda servisler enjekte edilerek root oluşturulur

        Returns:
            AnaEkran: Uygulamanın ana root widget'ı.
        """
        self._ui_guard_kontrolu()

        ekran_cls = self._ana_ekran_sinifi()
        return ekran_cls(services=self._services)
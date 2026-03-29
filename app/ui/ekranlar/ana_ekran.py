# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ekranlar/ana_ekran.py

ROL:
- Ana ekranın state ve akış yönetimini sağlar
- Yerleşim üretimini yerleşim mixin'ine bırakır
- Aksiyonları aksiyon mixin'leri üzerinden kullanır
- Seçim durumuna göre layout görünümünü kontrol eder
- Aktif işlem başlığını deterministik biçimde üretir
- Dosya seçili değilse ekranı başlangıç durumuna döndürebilir

MİMARİ:
- UI yerleşim kodu içermez
- State merkezidir
- Servis facade ile çalışır
- Yerleşim / aksiyon / yardımcı katmanları ayrıdır
- Deterministik davranır
- Geriye uyumluluk katmanı içermez
- Alt widget referansları yerleşim mixin tarafından set edilir
- _fonksiyon_secildi akışı aksiyon mixin'de kalır; burada ezilmez

TYPE GÜVENLİĞİ:
- State alanları net tiplenmiştir
- UI referansları açıkça tutulur
- Sıfır belirsizlik hedeflenir

SURUM: 21
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Any

from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout

from app.ui.ekranlar.ana_ekran_paketi import (
    AnaEkranAksiyonMixin,
    AnaEkranYardimciMixin,
    AnaEkranYerlesimMixin,
)
from app.ui.ortak.boyutlar import BOSLUK_SM


class AnaEkran(
    BoxLayout,
    AnaEkranYardimciMixin,
    AnaEkranAksiyonMixin,
    AnaEkranYerlesimMixin,
):
    """
    Ana ekran state yöneticisi.
    """

    __slots__ = (
        "_services",
        "_secili_kaynak",
        "_secili_kaynak_tipi",
        "_secili_item",
        "_aktif_islem_kodu",
        "_fonksiyon_listesi",
        "_mevcut_kod_input",
        "_yeni_kod_input",
        "_alt_kontroller",
        "_bilgi",
        "_dosya_alani",
        "_dosya_bilgi_label",
        "_banner_alani",
        "_aktif_islem_baslik_label",
        "_sol_panel",
        "_sag_panel",
        "_rect",
    )

    def __init__(self, *, services, **kwargs):
        """
        Ana ekranı oluşturur.

        Args:
            services:
                Servis yöneticisi / facade nesnesi.
            **kwargs:
                BoxLayout argümanları.
        """
        super().__init__(**kwargs)

        # =====================================================
        # CORE
        # =====================================================
        self._services = services

        # =====================================================
        # STATE
        # =====================================================
        self._secili_kaynak: str = ""
        self._secili_kaynak_tipi: str = ""
        self._secili_item: Any | None = None
        self._aktif_islem_kodu: str = "fonksiyon_degistir"

        # =====================================================
        # UI REFERANSLARI
        # =====================================================
        self._fonksiyon_listesi = None
        self._mevcut_kod_input = None
        self._yeni_kod_input = None
        self._alt_kontroller = None
        self._bilgi = None
        self._dosya_alani = None
        self._dosya_bilgi_label = None
        self._banner_alani = None
        self._aktif_islem_baslik_label = None
        self._sol_panel = None
        self._sag_panel = None
        self._rect = None

        # =====================================================
        # ROOT CONFIG
        # =====================================================
        self.orientation = "vertical"
        self.padding = BOSLUK_SM
        self.spacing = BOSLUK_SM

        try:
            Window.softinput_mode = "below_target"
        except Exception:
            pass

        # =====================================================
        # BUILD
        # =====================================================
        self._arka_plan()
        self._kur()
        self._layout_guncelle()
        self._son_klasor_bilgisi_yukle()

    # =========================================================
    # BASLIK STATE
    # =========================================================
    def aktif_islem_baslik(self) -> str:
        """
        Aktif işlem başlığını deterministik biçimde üretir.
        """
        kod = str(self._aktif_islem_kodu or "").strip()

        if kod == "fonksiyon_degistir":
            text = self._t("operation_function_change")
            return text if text != "operation_function_change" else "Fonksiyon Değiştir"

        if kod == "parca_degistir":
            text = self._t("operation_partial_change")
            return text if text != "operation_partial_change" else "Parça Değiştir"

        if kod == "enjeksiyon":
            text = self._t("operation_injection")
            return text if text != "operation_injection" else "Enjeksiyon"

        text = self._t("menu_operations")
        return text if text != "menu_operations" else "Menü İşlemleri"

    def aktif_islem_baslik_yenile(self) -> None:
        """
        Aktif işlem başlığı etiketini günceller.
        """
        if self._aktif_islem_baslik_label is not None:
            self._aktif_islem_baslik_label.text = self.aktif_islem_baslik()

    def _aktif_islem_basligini_yenile(self) -> None:
        """
        Yerleşim / aksiyon katmanındaki mevcut çağrılar için
        uyumlu yönlendirme metodu.

        Not:
        - State mantığı ana_ekran.py içindedir
        - Gerçek güncelleme aktif_islem_baslik_yenile() ile yapılır
        """
        self.aktif_islem_baslik_yenile()

    # =========================================================
    # DURUM RESET
    # =========================================================
    def _bos_duruma_don(self) -> None:
        """
        Dosya seçili değilse ekranı başlangıç durumuna döndürür.

        İşlev:
        - Seçili fonksiyonu temizler
        - Kod panellerini temizler
        - Fonksiyon listesini sıfırlar
        - Alt aksiyon ve panel görünümünü yeniden hesaplar

        Not:
        - Dosya seçiliyse hiçbir şey yapmaz
        """
        if str(self._secili_kaynak or "").strip():
            return

        self._secili_item = None

        if self._mevcut_kod_input is not None:
            self._mevcut_kod_input.text = ""

        if self._yeni_kod_input is not None:
            self._yeni_kod_input.text = ""

        if self._fonksiyon_listesi is not None:
            self._fonksiyon_listesi.clear_items()

        self._layout_guncelle()

    # =========================================================
    # LAYOUT CONTROL
    # =========================================================
    def _layout_guncelle(self) -> None:
        """
        Seçim durumuna göre layout görünümünü günceller.
        """
        if self._sol_panel is None or self._sag_panel is None:
            return

        dosya_secili = bool(str(self._secili_kaynak or "").strip())
        fonksiyon_secili = self._secili_item is not None

        if self._alt_kontroller is not None:
            self._alt_kontroller.duruma_gore_guncelle(
                dosya_secili=dosya_secili,
                fonksiyon_secili=fonksiyon_secili,
            )

        if not fonksiyon_secili:
            self._sol_panel.size_hint_x = 1
            self._sag_panel.size_hint_x = 0
            self._sag_panel.opacity = 0
            self._sag_panel.disabled = True
        else:
            self._sol_panel.size_hint_x = 0.45
            self._sag_panel.size_hint_x = 0.55
            self._sag_panel.opacity = 1
            self._sag_panel.disabled = False

    def _tarama_sonrasi_layout_reset(self) -> None:
        """
        Yeni tarama sonrası seçim durumunu sıfırlar ve layout'u günceller.
        """
        self._secili_item = None
        self._layout_guncelle()
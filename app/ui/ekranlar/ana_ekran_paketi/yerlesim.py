# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ekranlar/ana_ekran_paketi/yerlesim.py

ROL:
- Ana ekranın yerleşim kurulumunu içerir
- Widget ağaç yapısını tek yerde toplar
- Üst alanı hazır toolbar bileşeni ile kurar
- Banner reklam rezerv alanını oluşturur
- Seçili işlem başlığını dil entegre biçimde gösterir
- Orta alanı kurar
- Alt aksiyon çubuğunu hazır bileşen ile kurar
- Kod panellerini ortak bileşen üzerinden üretir
- Fonksiyon listesini ayrı liste panel bileşeni içinde sunar
- SOL / SAĞ panel referanslarını tutar
- Kod paneli kopyalama aksiyonlarını BilgiKutusu ile entegre eder

MİMARİ:
- Yerleşim sorumluluğu burada tutulur
- Hazır UI bileşenlerini birleştirir
- Callback referansları ekran instance metodlarına doğrudan bağlanır
- Ortak boyut ve renk sabitlerini kullanır
- Geriye uyumluluk katmanı içermez
- Dil entegrasyonunda mevcut anahtar seti korunur
- State / iş akışı mantığı ana_ekran.py içinde kalır
- Bu dosya yalnızca layout ve widget üretir

SURUM: 28
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from app.ui.bilesenler import (
    BilgiKutusu,
    DosyaYoluAlani,
    FonksiyonListesi,
)
from app.ui.bilesenler.alt_aksiyon_cubugu import AltAksiyonCubugu
from app.ui.bilesenler.kod_paneli import KodPaneli
from app.ui.bilesenler.liste_paneli import ListePaneli
from app.ui.bilesenler.ust_toolbar import UstToolbar
from app.ui.ortak.boyutlar import (
    BOSLUK_SM,
    ICON_16,
    ORAN_SAG_PANEL,
    ORAN_SOL_PANEL,
    SPACING_BLOK,
)
from app.ui.ortak.renkler import (
    AYIRICI,
    INPUT_ARKAPLAN,
    INPUT_IPUCU,
    KART,
    KOD_ARKAPLAN,
    METIN,
    METIN_SOLUK,
)


class _BannerRezervAlani(BoxLayout):
    """
    Üst bölümde banner reklam için yer ayıran sade kapsayıcı.
    """

    __slots__ = ("_bg_rect", "_line")

    def __init__(self, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(66))

        super().__init__(**kwargs)

        with self.canvas.before:
            Color(*KART)
            self._bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(18), dp(18), dp(18), dp(18)],
            )

        with self.canvas.after:
            Color(*AYIRICI)
            self._line = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dp(18),
                ),
                width=1.0,
            )

        self.bind(pos=self._yenile, size=self._yenile)

    def _yenile(self, *_args) -> None:
        """
        Arka plan ve kenarlık çizimini günceller.
        """
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._line.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(18),
        )


class AnaEkranYerlesimMixin:
    """
    Ana ekran widget ağacını kuran yerleşim mixin'i.
    """

    # =========================================================
    # ANA KURULUM
    # =========================================================
    def _kur(self) -> None:
        """
        Ana ekran yerleşimini baştan kurar.
        """
        self.clear_widgets()

        self.add_widget(self._ust_toolbar_olustur())
        self.add_widget(self._banner_alani_olustur())
        self.add_widget(self._aktif_islem_basligi_olustur())
        self._dosya_alani_bolumu_kur()
        self.add_widget(self._orta_alan_olustur())
        self.add_widget(self._alt_aksiyon_cubugu_olustur())
        self._bilgi_alani_kur()
        self._baslangic_dosya_yolunu_uygula()

        # ---------------------------------------------------------
        # REKLAMLAR: banner başlat + geçiş reklamı ön yükle
        # ---------------------------------------------------------
        try:
            if hasattr(self, "_services") and self._services is not None:
                reklam_getir = getattr(self._services, "reklam", None)
                if callable(reklam_getir):
                    reklam_yoneticisi = reklam_getir()
                    reklam_yoneticisi.banner_goster_gecikmeli(delay=1.2)
                    reklam_yoneticisi.gecis_reklami_yukle()
        except Exception:
            pass

    # =========================================================
    # ÜST ALAN
    # =========================================================
    def _ust_toolbar_olustur(self) -> UstToolbar:
        """
        Üst toolbar bileşenini üretir.
        """
        return UstToolbar(
            on_menu=self._menu,
            t=self._t,
        )

    def _banner_alani_olustur(self) -> _BannerRezervAlani:
        """
        Banner reklam için üstte rezerv alan üretir.
        """
        self._banner_alani = _BannerRezervAlani()
        return self._banner_alani

    def _aktif_islem_basligi_olustur(self) -> Label:
        """
        Seçili işlem başlığını gösteren etiketi üretir.
        """
        self._aktif_islem_baslik_label = Label(
            text=self.aktif_islem_baslik(),
            color=METIN_SOLUK,
            size_hint_y=None,
            height=ICON_16 + BOSLUK_SM + dp(6),
            halign="left",
            valign="middle",
            font_size=dp(14),
            bold=True,
        )
        self._aktif_islem_baslik_label.bind(
            size=lambda inst, _val: setattr(inst, "text_size", inst.size)
        )
        return self._aktif_islem_baslik_label

    # =========================================================
    # DOSYA ALANI
    # =========================================================
    def _dosya_alani_bolumu_kur(self) -> None:
        """
        Dosya yolu alanı ve dosya durum bilgisini kurar.
        """
        self._dosya_alani = DosyaYoluAlani(t=self._t)
        self.add_widget(self._dosya_alani)

        self._dosya_bilgi_label = Label(
            text=self._t("file_waiting"),
            color=METIN_SOLUK,
            size_hint_y=None,
            height=ICON_16 + BOSLUK_SM,
            halign="left",
            valign="middle",
        )
        self._dosya_bilgi_label.bind(
            size=lambda inst, _val: setattr(inst, "text_size", inst.size)
        )
        self.add_widget(self._dosya_bilgi_label)

    # =========================================================
    # ORTA ALAN
    # =========================================================
    def _orta_alan_olustur(self) -> BoxLayout:
        """
        Sol fonksiyon listesi ve sağ kod panelleri alanını üretir.
        """
        orta = BoxLayout(
            orientation="horizontal",
            spacing=SPACING_BLOK,
        )

        self._sol_panel = self._sol_panel_olustur()
        self._sag_panel = self._sag_panel_olustur()

        orta.add_widget(self._sol_panel)
        orta.add_widget(self._sag_panel)

        return orta

    def _sol_panel_olustur(self) -> ListePaneli:
        """
        Sol panelde fonksiyon listesini kart görünümünde üretir.
        """
        baslik = self._t("function_list_title")
        if baslik == "function_list_title":
            baslik = self._t("functions")
        if baslik == "functions":
            baslik = "Fonksiyonlar"

        sol_panel = ListePaneli(
            title=baslik,
            t=self._t,
            size_hint_x=ORAN_SOL_PANEL,
        )

        self._fonksiyon_listesi = FonksiyonListesi(
            t=self._t,
            on_select=self._fonksiyon_secildi,
        )
        sol_panel.add_widget(self._fonksiyon_listesi)

        return sol_panel

    def _mevcut_kod_kopyalandi(self) -> None:
        """
        Mevcut kod paneli kopyalama geri bildirimi üretir.
        """
        mesaj = self._t("current_code_copied")
        if mesaj == "current_code_copied":
            mesaj = "Mevcut kod kopyalandı."

        if self._bilgi is not None:
            self._bilgi.mesaj(
                mesaj,
                ikon="copy.png",
                pulse=True,
                hata=False,
            )

    def _yeni_kod_kopyalandi(self) -> None:
        """
        Yeni kod paneli kopyalama geri bildirimi üretir.
        """
        mesaj = self._t("new_code_copied")
        if mesaj == "new_code_copied":
            mesaj = "Yeni kod kopyalandı."

        if self._bilgi is not None:
            self._bilgi.mesaj(
                mesaj,
                ikon="copy.png",
                pulse=True,
                hata=False,
            )

    def _sag_panel_olustur(self) -> BoxLayout:
        """
        Sağ panelde mevcut kod ve yeni kod panellerini üretir.
        """
        sag_panel = BoxLayout(
            orientation="vertical",
            spacing=SPACING_BLOK,
            size_hint_x=ORAN_SAG_PANEL,
        )

        mevcut_panel = KodPaneli(
            title=self._t("current_code"),
            readonly=True,
            hint_text=self._t("preview_empty"),
            background_color=KOD_ARKAPLAN,
            foreground_color=METIN,
            hint_text_color=INPUT_IPUCU,
            t=self._t,
            on_copy=self._mevcut_kod_kopyalandi,
        )

        yeni_panel = KodPaneli(
            title=self._t("new_function_code"),
            readonly=False,
            hint_text=self._t("new_function_hint"),
            background_color=INPUT_ARKAPLAN,
            foreground_color=METIN,
            hint_text_color=INPUT_IPUCU,
            t=self._t,
            on_copy=self._yeni_kod_kopyalandi,
        )

        self._mevcut_kod_input = mevcut_panel.input_widget
        self._yeni_kod_input = yeni_panel.input_widget

        sag_panel.add_widget(mevcut_panel)
        sag_panel.add_widget(yeni_panel)

        return sag_panel

    # =========================================================
    # ALT AKSİYON
    # =========================================================
    def _alt_aksiyon_cubugu_olustur(self) -> AltAksiyonCubugu:
        """
        Alt aksiyon çubuğunu üretir.
        """
        self._alt_kontroller = AltAksiyonCubugu(
            on_dosya_sec=self._dosya_sec,
            on_kontrol=self._kontrol,
            on_guncelle=self._guncelle,
            on_geri_yukle=self._geri_yukle,
            on_temizle=self._temizle,
            on_yapistir=self._yapistir,
            t=self._t,
        )
        return self._alt_kontroller

    # =========================================================
    # ALT BİLGİ
    # =========================================================
    def _bilgi_alani_kur(self) -> None:
        """
        Alt bilgi kutusunu kurar.
        """
        self._bilgi = BilgiKutusu(t=self._t)
        self._bilgi.mesaj(self._t("app_ready"))
        self.add_widget(self._bilgi)

    # =========================================================
    # BAŞLANGIÇ DURUMU
    # =========================================================
    def _baslangic_dosya_yolunu_uygula(self) -> None:
        """
        Önceden seçili kaynak varsa dosya alanına uygular.
        """
        if self._dosya_alani is not None:
            self._dosya_alani.dosya_yolu_ayarla(self._secili_kaynak or "")
# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/ekranlar/gelistirici_ayarlar.py

ROL:
- Dil geliştirici ekranını oluşturur
- assets/lang klasöründeki dil dosyalarını listeler
- Referans dile göre eksik key analizini gösterir
- Eksik key listesini kopyalanabilir hale getirir
- Yeni key ekleme ve toplu yapıştırma akışını sağlar
- Yeni dil dosyası oluşturma akışını sade biçimde sunar
- Geri dönüş aksiyonu ile ana ekrana dönmeyi destekler

MİMARİ:
- UI katmanıdır
- Service katmanını bilir, core bilmez
- dil_gelistirici servisi üzerinden çalışır
- Fail-soft davranır
- Geriye uyumluluk katmanı içermez
- create_root ile dış katmana tek giriş sunar
- Deterministik ve sade ekran akışı hedeflenir

ENTEGRASYON:
- app/services/yoneticisi.py içindeki dil_gelistirici() servisini kullanır
- app/ui/ekranlar/ana_ekran_paketi/aksiyonlar_paketi/gelistirici_aksiyonlari.py
  içinden create_root(...) ile açılır

SURUM: 4
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Callable

from kivy.core.clipboard import Clipboard
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput


def _tr_fallback(t: Callable[[str], str] | None, key: str, fallback: str) -> str:
    """
    Çeviri anahtarı varsa kullanır, yoksa fallback döndürür.
    """
    if t is None:
        return fallback

    try:
        text = str(t(key) or "").strip()
    except Exception:
        return fallback

    if not text or text == key:
        return fallback
    return text


def _label_sol(
    *,
    text: str,
    height,
    font_size,
    bold: bool = False,
) -> Label:
    """
    Sol hizalı standart label üretir.
    """
    widget = Label(
        text=str(text or ""),
        halign="left",
        valign="middle",
        size_hint_y=None,
        height=height,
        font_size=font_size,
        bold=bold,
    )
    widget.bind(size=lambda inst, _v: setattr(inst, "text_size", inst.size))
    return widget


class GelistiriciAyarlarEkrani(BoxLayout):
    """
    Dil geliştirici ekranı.
    """

    __slots__ = (
        "_services",
        "_t",
        "_dil_servisi",
        "_on_geri",
        "_referans_spinner",
        "_hedef_spinner",
        "_durum_label",
        "_eksik_label",
        "_key_input",
        "_referans_deger_input",
        "_diger_deger_input",
        "_toplu_key_input",
        "_yeni_dil_kodu_input",
        "_yeni_dil_adi_input",
    )

    def __init__(
        self,
        *,
        servisler,
        t: Callable[[str], str] | None = None,
        on_geri: Callable[[], None] | None = None,
        **kwargs,
    ) -> None:
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("spacing", dp(8))
        kwargs.setdefault("padding", dp(10))

        super().__init__(**kwargs)

        self._services = servisler
        self._t = t
        self._on_geri = on_geri
        self._dil_servisi = self._services.dil_gelistirici()

        self._referans_spinner: Spinner | None = None
        self._hedef_spinner: Spinner | None = None
        self._durum_label: Label | None = None
        self._eksik_label: Label | None = None
        self._key_input: TextInput | None = None
        self._referans_deger_input: TextInput | None = None
        self._diger_deger_input: TextInput | None = None
        self._toplu_key_input: TextInput | None = None
        self._yeni_dil_kodu_input: TextInput | None = None
        self._yeni_dil_adi_input: TextInput | None = None

        self._kur()
        self._dilleri_yukle()
        self._analizi_yenile()

    # =========================================================
    # KURULUM
    # =========================================================
    def _kur(self) -> None:
        """
        Ekran yerleşimini kurar.
        """
        self.clear_widgets()

        self.add_widget(self._ust_bilgi_alani())

        govde_scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(6),
        )

        govde = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
        )
        govde.bind(minimum_height=lambda inst, val: setattr(inst, "height", val))

        govde.add_widget(self._dil_secim_alani())
        govde.add_widget(self._eksik_key_alani())
        govde.add_widget(self._key_ekleme_alani())
        govde.add_widget(self._toplu_yapistirma_alani())
        govde.add_widget(self._yeni_dil_alani())
        govde.add_widget(self._alt_aksiyon_alani())

        govde_scroll.add_widget(govde)
        self.add_widget(govde_scroll)

    def _ust_bilgi_alani(self) -> BoxLayout:
        alan = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(92),
            spacing=dp(4),
        )

        baslik = _label_sol(
            text=_tr_fallback(
                self._t,
                "developer_settings",
                "Dil Geliştirici",
            ),
            height=dp(32),
            font_size=dp(18),
            bold=True,
        )

        aciklama = Label(
            text=_tr_fallback(
                self._t,
                "developer_language_tools_desc",
                "assets/lang içindeki dil dosyalarını yönetin, eksik keyleri görün, yeni key ve yeni dil oluşturun.",
            ),
            halign="left",
            valign="top",
            size_hint_y=None,
            height=dp(56),
            font_size=dp(12),
        )
        aciklama.bind(size=lambda inst, _v: setattr(inst, "text_size", inst.size))

        alan.add_widget(baslik)
        alan.add_widget(aciklama)
        return alan

    def _dil_secim_alani(self) -> BoxLayout:
        kart = BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None,
            height=dp(114),
        )

        satir1 = _label_sol(
            text=(
                _tr_fallback(self._t, "language", "Dil")
                + " / "
                + _tr_fallback(self._t, "select_language", "Dil Seç")
            ),
            height=dp(24),
            font_size=dp(14),
            bold=True,
        )

        satir2 = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(40),
        )

        self._referans_spinner = Spinner(
            text="tr",
            values=(),
            size_hint_x=0.5,
        )
        self._referans_spinner.bind(text=lambda *_: self._analizi_yenile())

        self._hedef_spinner = Spinner(
            text="en",
            values=(),
            size_hint_x=0.5,
        )
        self._hedef_spinner.bind(text=lambda *_: self._analizi_yenile())

        satir2.add_widget(self._referans_spinner)
        satir2.add_widget(self._hedef_spinner)

        self._durum_label = Label(
            text="",
            halign="left",
            valign="top",
            size_hint_y=None,
            height=dp(40),
            font_size=dp(12),
        )
        self._durum_label.bind(
            size=lambda inst, _v: setattr(inst, "text_size", inst.size)
        )

        kart.add_widget(satir1)
        kart.add_widget(satir2)
        kart.add_widget(self._durum_label)

        return kart

    def _eksik_key_alani(self) -> BoxLayout:
        kart = BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None,
            height=dp(270),
        )

        baslik = _label_sol(
            text=_tr_fallback(
                self._t,
                "missing_keys",
                "Eksik Keyler",
            ),
            height=dp(28),
            font_size=dp(14),
            bold=True,
        )

        scroll = ScrollView(
            size_hint_y=None,
            height=dp(190),
            bar_width=dp(6),
        )

        self._eksik_label = Label(
            text="",
            halign="left",
            valign="top",
            size_hint_y=None,
            font_size=dp(12),
        )
        self._eksik_label.bind(
            width=lambda inst, val: setattr(inst, "text_size", (val, None))
        )
        self._eksik_label.bind(
            texture_size=lambda inst, val: setattr(inst, "height", max(dp(60), val[1]))
        )

        scroll.add_widget(self._eksik_label)

        buton_satiri = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(42),
        )

        kopyala_buton = Button(
            text=_tr_fallback(self._t, "copy", "Kopyala"),
        )
        kopyala_buton.bind(on_release=lambda *_: self._eksik_keyleri_kopyala())

        eksikleri_ekle_buton = Button(
            text=_tr_fallback(self._t, "restore", "Eksikleri Ekle"),
        )
        eksikleri_ekle_buton.bind(
            on_release=lambda *_: self._eksikleri_secili_dile_ekle()
        )

        buton_satiri.add_widget(kopyala_buton)
        buton_satiri.add_widget(eksikleri_ekle_buton)

        kart.add_widget(baslik)
        kart.add_widget(scroll)
        kart.add_widget(buton_satiri)
        return kart

    def _key_ekleme_alani(self) -> BoxLayout:
        kart = BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None,
            height=dp(186),
        )

        baslik = _label_sol(
            text=_tr_fallback(
                self._t,
                "add_key",
                "Yeni Key Ekle",
            ),
            height=dp(28),
            font_size=dp(14),
            bold=True,
        )

        self._key_input = TextInput(
            hint_text="key_name",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
        )

        self._referans_deger_input = TextInput(
            hint_text=_tr_fallback(
                self._t,
                "reference_value",
                "Referans dil değeri",
            ),
            multiline=False,
            size_hint_y=None,
            height=dp(40),
        )

        self._diger_deger_input = TextInput(
            hint_text=_tr_fallback(
                self._t,
                "other_languages_value",
                "Diğer diller için değer",
            ),
            multiline=False,
            size_hint_y=None,
            height=dp(40),
        )

        buton_satiri = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(42),
        )

        ekle_buton = Button(
            text=_tr_fallback(self._t, "save", "Kaydet"),
        )
        ekle_buton.bind(on_release=lambda *_: self._keyi_tum_dillere_ekle())

        seciliye_buton = Button(
            text="Seçili Dile Ekle",
        )
        seciliye_buton.bind(on_release=lambda *_: self._keyi_secili_dile_ekle())

        buton_satiri.add_widget(ekle_buton)
        buton_satiri.add_widget(seciliye_buton)

        kart.add_widget(baslik)
        kart.add_widget(self._key_input)
        kart.add_widget(self._referans_deger_input)
        kart.add_widget(self._diger_deger_input)
        kart.add_widget(buton_satiri)

        return kart

    def _toplu_yapistirma_alani(self) -> BoxLayout:
        kart = BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None,
            height=dp(210),
        )

        baslik = _label_sol(
            text="Toplu Yapıştır / JSON Satırları",
            height=dp(28),
            font_size=dp(14),
            bold=True,
        )

        self._toplu_key_input = TextInput(
            hint_text=(
                '"scan_completed": "Сканування завершено.",\n'
                '"selected_function": "Вибрана функція: -",'
            ),
            multiline=True,
            size_hint_y=None,
            height=dp(120),
        )

        buton_satiri = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(42),
        )

        secili_dile_buton = Button(
            text="Yapıştırılanı Seçili Dile Ekle",
        )
        secili_dile_buton.bind(
            on_release=lambda *_: self._yapistirilani_secili_dile_ekle()
        )

        temizle_buton = Button(
            text=_tr_fallback(self._t, "clear", "Temizle"),
        )
        temizle_buton.bind(on_release=lambda *_: self._toplu_alani_temizle())

        buton_satiri.add_widget(secili_dile_buton)
        buton_satiri.add_widget(temizle_buton)

        kart.add_widget(baslik)
        kart.add_widget(self._toplu_key_input)
        kart.add_widget(buton_satiri)
        return kart

    def _yeni_dil_alani(self) -> BoxLayout:
        kart = BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None,
            height=dp(144),
        )

        baslik = _label_sol(
            text=_tr_fallback(
                self._t,
                "create_new_language",
                "Yeni Dil Oluştur",
            ),
            height=dp(28),
            font_size=dp(14),
            bold=True,
        )

        self._yeni_dil_kodu_input = TextInput(
            hint_text="ör. de / fr / pt-br",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
        )

        self._yeni_dil_adi_input = TextInput(
            hint_text=_tr_fallback(self._t, "language_name", "Dil adı"),
            multiline=False,
            size_hint_y=None,
            height=dp(40),
        )

        olustur_buton = Button(
            text=_tr_fallback(self._t, "create", "Oluştur"),
            size_hint_y=None,
            height=dp(42),
        )
        olustur_buton.bind(on_release=lambda *_: self._yeni_dil_olustur())

        kart.add_widget(baslik)
        kart.add_widget(self._yeni_dil_kodu_input)
        kart.add_widget(self._yeni_dil_adi_input)
        kart.add_widget(olustur_buton)

        return kart

    def _alt_aksiyon_alani(self) -> BoxLayout:
        alan = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(42),
        )

        if callable(self._on_geri):
            geri_buton = Button(
                text=_tr_fallback(self._t, "back", "Geri"),
            )
            geri_buton.bind(on_release=lambda *_: self._geri())
            alan.add_widget(geri_buton)

        yenile_buton = Button(
            text=_tr_fallback(self._t, "update", "Güncelle"),
        )
        yenile_buton.bind(on_release=lambda *_: self._yenile())

        alan.add_widget(yenile_buton)
        return alan

    # =========================================================
    # YARDIMCILAR
    # =========================================================
    def _mesaj(self, text: str) -> None:
        """
        Durum bilgisini günceller.
        """
        if self._durum_label is not None:
            self._durum_label.text = str(text or "")

    def _referans_dil(self) -> str:
        if self._referans_spinner is None:
            return "tr"
        return str(self._referans_spinner.text or "").strip()

    def _hedef_dil(self) -> str:
        if self._hedef_spinner is None:
            return "en"
        return str(self._hedef_spinner.text or "").strip()

    def _hedef_dosya_adi(self) -> str:
        """
        Seçili hedef dilin dosya adını döndürür.
        """
        hedef = self._hedef_dil()
        if not hedef:
            return ""
        try:
            yol = self._dil_servisi.dil_dosyasi_yolu(hedef)
            return os.path.basename(str(yol or "").strip())
        except Exception:
            return f"{hedef}.json"

    def _eksik_keyleri_listesi(self) -> list[str]:
        """
        Eksik key label içeriğini satırlardan çözer.
        """
        if self._eksik_label is None:
            return []

        raw = str(self._eksik_label.text or "").strip()
        if not raw or raw == "Eksik key yok." or raw == "Referans ve hedef dil aynı.":
            return []

        sonuc: list[str] = []
        for satir in raw.splitlines():
            temiz = satir.strip()
            if temiz.startswith("•"):
                temiz = temiz[1:].strip()
            if temiz:
                sonuc.append(temiz)
        return sonuc

    def _eksik_key_kopya_metni(self) -> str:
        """
        Eksik key listesinin kopyalanacak metnini üretir.
        """
        keyler = self._eksik_keyleri_listesi()
        hedef_dosya = self._hedef_dosya_adi()
        referans = self._referans_dil()
        hedef = self._hedef_dil()

        satirlar = [
            f"hedef_dosya: {hedef_dosya}",
            f"referans_dil: {referans}",
            f"hedef_dil: {hedef}",
            "eksik_keyler:",
        ]
        satirlar.extend(keyler)
        return "\n".join(satirlar)

    def _yapistirilan_keyleri_ayikla(self, metin: str) -> dict[str, str]:
        """
        Yapıştırılan metinden key-value çiftlerini çözer.

        Desteklenen örnekler:
        - "key": "value",
        - çok satırlı JSON parçası
        - tam JSON obje
        """
        raw = str(metin or "").strip()
        if not raw:
            return {}

        try:
            veri = json.loads(raw)
            if isinstance(veri, dict):
                return {str(k): str(v) for k, v in veri.items()}
        except Exception:
            pass

        try:
            sarili = "{\n" + raw.rstrip(", \n\r\t") + "\n}"
            veri = json.loads(sarili)
            if isinstance(veri, dict):
                return {str(k): str(v) for k, v in veri.items()}
        except Exception:
            pass

        sonuc: dict[str, str] = {}
        desen = re.compile(
            r'^\s*"(?P<key>[^"]+)"\s*:\s*"(?P<val>(?:[^"\\]|\\.)*)"\s*,?\s*$'
        )

        for satir in raw.splitlines():
            eslesme = desen.match(satir.strip())
            if not eslesme:
                continue

            key = str(eslesme.group("key") or "").strip()
            val = str(eslesme.group("val") or "")
            val = bytes(val, "utf-8").decode("unicode_escape")

            if key:
                sonuc[key] = val

        return sonuc

    # =========================================================
    # VERI YUKLEME
    # =========================================================
    def _dilleri_yukle(self) -> None:
        """
        Dil listesini servisten yükler.
        """
        Logger.info("GelistiriciAyarlar: _dilleri_yukle girdi.")

        try:
            kodlar = list(self._dil_servisi.dil_kodlarini_listele() or [])
        except Exception as exc:
            Logger.exception(f"GelistiriciAyarlar: dil listesi yuklenemedi: {exc}")
            self._mesaj(f"Dil listesi yüklenemedi: {exc}")
            return

        if not kodlar:
            self._mesaj("Hiç dil dosyası bulunamadı.")
            return

        kodlar = sorted(
            set(
                str(k or "").strip()
                for k in kodlar
                if str(k or "").strip()
            )
        )

        if self._referans_spinner is not None:
            self._referans_spinner.values = kodlar
            if self._referans_spinner.text not in kodlar:
                self._referans_spinner.text = "tr" if "tr" in kodlar else kodlar[0]

        if self._hedef_spinner is not None:
            self._hedef_spinner.values = kodlar
            varsayilan = "en" if "en" in kodlar else kodlar[0]

            if (
                self._referans_spinner is not None
                and varsayilan == self._referans_spinner.text
                and len(kodlar) > 1
            ):
                varsayilan = kodlar[1]

            if self._hedef_spinner.text not in kodlar:
                self._hedef_spinner.text = varsayilan

    def _analizi_yenile(self) -> None:
        """
        Seçilen referans ve hedef dile göre eksik key analizini yeniler.
        """
        Logger.info("GelistiriciAyarlar: _analizi_yenile girdi.")

        referans = self._referans_dil()
        hedef = self._hedef_dil()

        if not referans or not hedef:
            self._mesaj("Dil seçimi eksik.")
            return

        if referans == hedef:
            if self._eksik_label is not None:
                self._eksik_label.text = "Referans ve hedef dil aynı."
            self._mesaj("Aynı dil seçildi.")
            return

        try:
            eksikler = self._dil_servisi.eksik_keyleri_getir(referans, hedef)
        except Exception as exc:
            Logger.exception(
                f"GelistiriciAyarlar: eksik key analizi hatasi: {exc}"
            )
            self._mesaj(f"Eksik key analizi yapılamadı: {exc}")
            return

        if self._eksik_label is not None:
            if eksikler:
                self._eksik_label.text = "\n".join(f"• {key}" for key in eksikler)
            else:
                self._eksik_label.text = "Eksik key yok."

        self._mesaj(
            f"Referans: {referans} | Hedef: {hedef} | Eksik: {len(eksikler)}"
        )

    # =========================================================
    # AKSIYONLAR
    # =========================================================
    def _geri(self) -> None:
        """
        Önceki ekrana dönüş aksiyonu.
        """
        Logger.info("GelistiriciAyarlar: _geri girdi.")
        if callable(self._on_geri):
            try:
                self._on_geri()
            except Exception as exc:
                Logger.exception(f"GelistiriciAyarlar: geri aksiyonu hatasi: {exc}")
                self._mesaj(f"Geri dönüş yapılamadı: {exc}")

    def _yenile(self) -> None:
        """
        Tüm ekran verisini yeniler.
        """
        Logger.info("GelistiriciAyarlar: _yenile girdi.")
        self._dilleri_yukle()
        self._analizi_yenile()

    def _eksik_keyleri_kopyala(self) -> None:
        """
        Eksik key listesini panoya kopyalar.
        """
        Logger.info("GelistiriciAyarlar: _eksik_keyleri_kopyala girdi.")
        keyler = self._eksik_keyleri_listesi()

        if not keyler:
            self._mesaj("Kopyalanacak eksik key yok.")
            return

        try:
            Clipboard.copy(self._eksik_key_kopya_metni())
            self._mesaj(
                f"{len(keyler)} eksik key ve hedef dosya adı kopyalandı."
            )
        except Exception as exc:
            Logger.exception(f"GelistiriciAyarlar: kopyalama hatasi: {exc}")
            self._mesaj(f"Kopyalama yapılamadı: {exc}")

    def _toplu_alani_temizle(self) -> None:
        """
        Toplu yapıştırma alanını temizler.
        """
        if self._toplu_key_input is not None:
            self._toplu_key_input.text = ""
        self._mesaj("Yapıştırma alanı temizlendi.")

    def _keyi_secili_dile_ekle(self) -> None:
        """
        Yazılan key'i sadece hedef dile ekler.
        """
        Logger.info("GelistiriciAyarlar: _keyi_secili_dile_ekle girdi.")

        key = str(self._key_input.text or "").strip() if self._key_input else ""
        deger = (
            str(self._diger_deger_input.text or "").strip()
            if self._diger_deger_input is not None
            else ""
        )
        hedef = self._hedef_dil()

        if not key:
            self._mesaj("Key boş olamaz.")
            return

        try:
            sonuc = self._dil_servisi.tek_dile_key_ekle(
                hedef,
                key,
                deger,
                varsa_uzerine_yaz=False,
            )
            self._mesaj(f"Key eklendi: {sonuc.get('key', key)} -> {hedef}")
            self._analizi_yenile()
        except Exception as exc:
            Logger.exception(f"GelistiriciAyarlar: tek_dile_key_ekle hata: {exc}")
            self._mesaj(f"Key eklenemedi: {exc}")

    def _keyi_tum_dillere_ekle(self) -> None:
        """
        Yazılan key'i tüm dillere ekler.
        """
        Logger.info("GelistiriciAyarlar: _keyi_tum_dillere_ekle girdi.")

        key = str(self._key_input.text or "").strip() if self._key_input else ""
        referans_dil = self._referans_dil()
        referans_deger = (
            str(self._referans_deger_input.text or "").strip()
            if self._referans_deger_input is not None
            else ""
        )
        diger_deger = (
            str(self._diger_deger_input.text or "").strip()
            if self._diger_deger_input is not None
            else ""
        )

        if not key:
            self._mesaj("Key boş olamaz.")
            return

        try:
            sonuc = self._dil_servisi.yeni_keyi_tum_dillere_ekle(
                key,
                referans_dil_kodu=referans_dil,
                referans_deger=referans_deger,
                diger_diller_degeri=diger_deger,
                varsa_uzerine_yaz=False,
            )
            self._mesaj(f"Tüm dillere işlendi: {len(sonuc)} kayıt")
            self._analizi_yenile()
        except Exception as exc:
            Logger.exception(
                f"GelistiriciAyarlar: tum dillere key ekleme hatasi: {exc}"
            )
            self._mesaj(f"Tüm dillere key eklenemedi: {exc}")

    def _yapistirilani_secili_dile_ekle(self) -> None:
        """
        Yapıştırılan JSON benzeri satırları çözüp seçili hedef dile ekler.
        """
        Logger.info("GelistiriciAyarlar: _yapistirilani_secili_dile_ekle girdi.")

        raw = (
            str(self._toplu_key_input.text or "").strip()
            if self._toplu_key_input
            else ""
        )
        hedef = self._hedef_dil()

        if not raw:
            self._mesaj("Yapıştırılacak içerik boş.")
            return

        try:
            kayitlar = self._yapistirilan_keyleri_ayikla(raw)
        except Exception as exc:
            Logger.exception(f"GelistiriciAyarlar: yapistirma parse hatasi: {exc}")
            self._mesaj(f"Yapıştırılan içerik çözülemedi: {exc}")
            return

        if not kayitlar:
            self._mesaj("Geçerli key-değer çifti bulunamadı.")
            return

        basarili = 0
        hatalar: list[str] = []

        for key, deger in kayitlar.items():
            try:
                self._dil_servisi.tek_dile_key_ekle(
                    hedef,
                    key,
                    deger,
                    varsa_uzerine_yaz=False,
                )
                basarili += 1
            except Exception as exc:
                hatalar.append(f"{key}: {exc}")

        self._analizi_yenile()

        if hatalar:
            self._mesaj(
                f"{basarili} kayıt eklendi, {len(hatalar)} kayıt atlandı."
            )
            return

        self._mesaj(f"{hedef} diline {basarili} kayıt eklendi.")

    def _eksikleri_secili_dile_ekle(self) -> None:
        """
        Referans dilde olup hedef dilde eksik olan keyleri hedef dile ekler.
        """
        Logger.info("GelistiriciAyarlar: _eksikleri_secili_dile_ekle girdi.")

        referans = self._referans_dil()
        hedef = self._hedef_dil()

        if referans == hedef:
            self._mesaj("Aynı dil için eksik ekleme yapılamaz.")
            return

        try:
            sonuc = self._dil_servisi.eksik_keyleri_hedef_dile_ekle(
                referans,
                hedef,
                bos_deger_kullan=True,
                varsa_uzerine_yaz=False,
            )
            adet = int(sonuc.get("eklenen_sayisi", 0))
            self._mesaj(f"{hedef} diline {adet} eksik key eklendi.")
            self._analizi_yenile()
        except Exception as exc:
            Logger.exception(
                f"GelistiriciAyarlar: eksik key ekleme hatasi: {exc}"
            )
            self._mesaj(f"Eksik keyler eklenemedi: {exc}")

    def _yeni_dil_olustur(self) -> None:
        """
        Yeni dil dosyası oluşturur.
        """
        Logger.info("GelistiriciAyarlar: _yeni_dil_olustur girdi.")

        referans = self._referans_dil()
        yeni_kod = (
            str(self._yeni_dil_kodu_input.text or "").strip().lower()
            if self._yeni_dil_kodu_input is not None
            else ""
        )
        yeni_ad = (
            str(self._yeni_dil_adi_input.text or "").strip()
            if self._yeni_dil_adi_input is not None
            else ""
        )

        if not yeni_kod:
            self._mesaj("Yeni dil kodu boş olamaz.")
            return

        if not yeni_ad:
            self._mesaj("Yeni dil adı boş olamaz.")
            return

        try:
            sonuc = self._dil_servisi.yeni_dil_olustur(
                referans,
                yeni_kod,
                yeni_ad,
                bos_deger_kullan=True,
                varsa_uzerine_yaz=False,
            )
            self._mesaj(
                f"Yeni dil oluşturuldu: {sonuc.get('dil_kodu', yeni_kod)}"
            )
            self._dilleri_yukle()
            if self._hedef_spinner is not None:
                self._hedef_spinner.text = yeni_kod
            self._analizi_yenile()
        except Exception as exc:
            Logger.exception(
                f"GelistiriciAyarlar: yeni dil olusturma hatasi: {exc}"
            )
            self._mesaj(f"Yeni dil oluşturulamadı: {exc}")


def create_root(
    *,
    servisler,
    t: Callable[[str], str] | None = None,
    on_geri: Callable[[], None] | None = None,
) -> GelistiriciAyarlarEkrani:
    """
    Dil geliştirici ekranı root widget'ını üretir.
    """
    return GelistiriciAyarlarEkrani(
        servisler=servisler,
        t=t,
        on_geri=on_geri,
    )


__all__ = (
    "GelistiriciAyarlarEkrani",
    "create_root",
)
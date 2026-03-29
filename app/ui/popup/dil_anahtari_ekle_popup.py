# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/popup/dil_anahtari_ekle_popup.py

ROL:
- Geliştirici modunda kullanılmak üzere "Dil Anahtarı Ekle" popup'ını sağlar
- Kullanıcının yeni çeviri anahtarı eklemesini sağlar
- Tek dil veya tüm dillere anahtar ekleme akışı sunar
- Servis katmanındaki DilAnahtariServisi ile entegre çalışır

ÖZELLİKLER:
- Anahtar (key) girişi
- Değer (value) girişi
- Dil seçimi (tek dil ekleme için)
- "Tüm dillere ekle" seçeneği
- Hata ve başarı geri bildirimi

MİMARİ:
- UI katmanıdır
- Servis katmanını doğrudan kullanmaz → dışarıdan enjekte edilir
- Deterministik davranır
- Geriye uyumluluk katmanı içermez
- Yan etkisizdir (callback bazlı)

BAĞIMLILIKLAR:
- DilAnahtariServisi (services)
- ikon_yolu (ikon yönetimi)
- ortak renk sistemi

KULLANIM:
popup = dil_anahtari_ekle_popup(
    servis=servis_yoneticisi.dil_anahtari(),
    t=ceviri_fonksiyonu
)

popup.open()

SURUM: 1
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from typing import Callable

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from app.ui.ortak.renkler import KART, METIN, METIN_SOLUK


def dil_anahtari_ekle_popup(
    *,
    servis,
    t: Callable[[str], str] | None = None,
) -> Popup:
    """
    Dil anahtarı ekleme popup'ı oluşturur.

    Parametreler:
    - servis: DilAnahtariServisi instance (zorunlu)
    - t: çeviri fonksiyonu (opsiyonel)

    Dönüş:
    - Popup instance
    """

    cevir = t or (lambda x, **_: x)

    root = BoxLayout(
        orientation="vertical",
        spacing=dp(10),
        padding=dp(12),
    )

    # =========================================================
    # BAŞLIK
    # =========================================================
    title = Label(
        text=cevir("add_language_key") or "Dil Anahtarı Ekle",
        size_hint_y=None,
        height=dp(30),
        bold=True,
        color=METIN,
    )

    root.add_widget(title)

    # =========================================================
    # INPUTLAR
    # =========================================================
    key_input = TextInput(
        hint_text="Anahtar (örn: save_button)",
        multiline=False,
        size_hint_y=None,
        height=dp(42),
    )

    value_input = TextInput(
        hint_text="Değer (örn: Kaydet)",
        multiline=False,
        size_hint_y=None,
        height=dp(42),
    )

    root.add_widget(key_input)
    root.add_widget(value_input)

    # =========================================================
    # DİL SEÇİMİ
    # =========================================================
    dil_listesi = servis.listele_dil_dosyalari()
    dil_kodlari = [d["code"] for d in dil_listesi]

    dil_spinner = Spinner(
        text=dil_kodlari[0] if dil_kodlari else "tr",
        values=dil_kodlari,
        size_hint_y=None,
        height=dp(42),
    )

    root.add_widget(dil_spinner)

    # =========================================================
    # TÜM DİLLER CHECKBOX
    # =========================================================
    tum_layout = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(40),
        spacing=dp(8),
    )

    tum_checkbox = CheckBox(size_hint=(None, None), size=(dp(24), dp(24)))

    tum_label = Label(
        text=cevir("add_to_all_languages") or "Tüm dillere ekle",
        color=METIN_SOLUK,
        halign="left",
        valign="middle",
    )
    tum_label.bind(size=lambda inst, val: setattr(inst, "text_size", inst.size))

    tum_layout.add_widget(tum_checkbox)
    tum_layout.add_widget(tum_label)

    root.add_widget(tum_layout)

    # =========================================================
    # SONUÇ LABEL
    # =========================================================
    sonuc_label = Label(
        text="",
        color=METIN_SOLUK,
        size_hint_y=None,
        height=dp(30),
    )

    root.add_widget(sonuc_label)

    # =========================================================
    # AKSİYON
    # =========================================================
    def _ekle(_):
        key = key_input.text.strip()
        value = value_input.text.strip()

        if not key:
            sonuc_label.text = "Anahtar boş olamaz"
            return

        try:
            if tum_checkbox.active:
                sonuc = servis.tum_dillere_anahtar_ekle(
                    anahtar=key,
                    varsayilan_deger=value,
                )
                sonuc_label.text = f"Eklendi ({sonuc['added_count']} dil)"
            else:
                sonuc = servis.anahtar_ekle(
                    dil_kodu=dil_spinner.text,
                    anahtar=key,
                    deger=value,
                )
                sonuc_label.text = f"Eklendi ({sonuc['code']})"

        except Exception as e:
            sonuc_label.text = str(e)

    # =========================================================
    # BUTONLAR
    # =========================================================
    btn_layout = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(42),
        spacing=dp(8),
    )

    ekle_btn = Button(
        text=cevir("add") or "Ekle",
    )
    ekle_btn.bind(on_release=_ekle)

    kapat_btn = Button(
        text=cevir("close") or "Kapat",
    )

    popup = Popup(
        title="",
        content=root,
        size_hint=(0.9, 0.7),
        auto_dismiss=True,
    )

    kapat_btn.bind(on_release=lambda *_: popup.dismiss())

    btn_layout.add_widget(ekle_btn)
    btn_layout.add_widget(kapat_btn)

    root.add_widget(btn_layout)

    return popup


__all__ = ("dil_anahtari_ekle_popup",)
# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/popup/test_dosya_sec_popup.py

ROL:
- Test / geliştirici modu için ayrı popup tabanlı dosya seçici sağlar
- Android/Pydroid ortamında FileChooser yerine manuel listeleme kullanır
- Klasör gezme, yukarı çıkma ve dosya seçme akışı sunar
- Seçilen path bilgisini callback ile dışarı verir

MİMARİ:
- UI katmanıdır
- IO tarafında yalnızca listeleme yapar
- Test/geliştirici kullanımına yöneliktir
- Üretim Android akışında kullanılmaz
- Geriye uyumluluk katmanı içermez

SURUM: 2
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

from app.ui.ortak.boyutlar import (
    BOSLUK_SM,
    YUKSEKLIK_BUTON,
)
from app.ui.ortak.renkler import (
    BUTON,
    KART,
    METIN,
)
from app.ui.ortak.stiller import rounded_bg


def test_popup_dosya_sec(
    *,
    services,
    on_secildi: Callable[[str], None],
    title: str = "Dosya Seç",
) -> None:
    """
    Test / geliştirici modu için popup dosya seçiciyi açar.
    """
    Logger.info("TestDosyaSecPopup: popup acilacak")

    baslangic_yolu = _popup_baslangic_yolu(
        _servisten_baslangic_yolu_al(services)
    )
    mevcut_klasor = Path(baslangic_yolu)

    root = BoxLayout(
        orientation="vertical",
        spacing=BOSLUK_SM,
        padding=BOSLUK_SM,
    )
    rounded_bg(root, bg_color=KART, line_color=KART)

    baslik = Label(
        text="TEST MODU DOSYA SECICI AKTIF",
        color=METIN,
        bold=True,
        size_hint_y=None,
        height=YUKSEKLIK_BUTON,
        halign="left",
        valign="middle",
    )
    baslik.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))
    root.add_widget(baslik)

    konum_label = Label(
        text=f"Konum: {mevcut_klasor}",
        color=METIN,
        size_hint_y=None,
        height=YUKSEKLIK_BUTON * 2,
        halign="left",
        valign="middle",
    )
    konum_label.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))
    root.add_widget(konum_label)

    secim_label = Label(
        text="Seçim: -",
        color=METIN,
        size_hint_y=None,
        height=YUKSEKLIK_BUTON,
        halign="left",
        valign="middle",
    )
    secim_label.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))
    root.add_widget(secim_label)

    ust_btnler = BoxLayout(
        orientation="horizontal",
        spacing=BOSLUK_SM,
        size_hint_y=None,
        height=YUKSEKLIK_BUTON,
    )

    yukari_btn = Button(
        text="Yukarı",
        color=METIN,
        background_normal="",
        background_down="",
        background_color=BUTON,
    )
    yenile_btn = Button(
        text="Yenile",
        color=METIN,
        background_normal="",
        background_down="",
        background_color=BUTON,
    )

    ust_btnler.add_widget(yukari_btn)
    ust_btnler.add_widget(yenile_btn)
    root.add_widget(ust_btnler)

    scroll = ScrollView()
    root.add_widget(scroll)

    liste_container = BoxLayout(
        orientation="vertical",
        spacing=BOSLUK_SM,
        size_hint_y=None,
    )
    liste_container.bind(
        minimum_height=lambda inst, val: setattr(inst, "height", val)
    )
    scroll.add_widget(liste_container)

    alt_btnler = BoxLayout(
        orientation="horizontal",
        spacing=BOSLUK_SM,
        size_hint_y=None,
        height=YUKSEKLIK_BUTON,
    )

    iptal_btn = Button(
        text="İptal",
        color=METIN,
        background_normal="",
        background_down="",
        background_color=BUTON,
    )
    sec_btn = Button(
        text="Seç",
        color=METIN,
        background_normal="",
        background_down="",
        background_color=BUTON,
    )

    alt_btnler.add_widget(iptal_btn)
    alt_btnler.add_widget(sec_btn)
    root.add_widget(alt_btnler)

    popup = Popup(
        title=f"{title} [TEST MODU]",
        content=root,
        size_hint=(0.95, 0.95),
        separator_height=1,
        title_color=METIN,
    )

    secili_dosya: dict[str, str] = {"path": ""}

    def _secim_yaz(path: str) -> None:
        raw = str(path or "").strip()
        secili_dosya["path"] = raw
        secim_label.text = f"Seçim: {raw or '-'}"

    def _klasor_yukle(hedef: Path) -> None:
        nonlocal mevcut_klasor

        try:
            hedef = hedef.resolve()
        except Exception:
            hedef = Path(str(hedef or "/"))

        if not hedef.exists() or not hedef.is_dir():
            Logger.warning(f"TestDosyaSecPopup: gecersiz klasor: {hedef}")
            return

        mevcut_klasor = hedef
        konum_label.text = f"Konum: {mevcut_klasor}"
        _secim_yaz("")

        liste_container.clear_widgets()

        try:
            klasorler: list[Path] = []
            dosyalar: list[Path] = []

            for item in hedef.iterdir():
                try:
                    if item.is_dir():
                        klasorler.append(item)
                    elif item.is_file():
                        dosyalar.append(item)
                except Exception:
                    continue

            klasorler.sort(key=lambda p: p.name.lower())
            dosyalar.sort(key=lambda p: p.name.lower())

            toplam = 0

            for klasor in klasorler:
                btn = Button(
                    text=f"[Klasör] {klasor.name}",
                    markup=False,
                    color=METIN,
                    size_hint_y=None,
                    height=YUKSEKLIK_BUTON,
                    halign="left",
                    valign="middle",
                    background_normal="",
                    background_down="",
                    background_color=BUTON,
                )
                btn.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))
                btn.bind(on_release=lambda _btn, p=klasor: _klasor_yukle(p))
                liste_container.add_widget(btn)
                toplam += 1

            for dosya in dosyalar:
                btn = Button(
                    text=dosya.name,
                    color=METIN,
                    size_hint_y=None,
                    height=YUKSEKLIK_BUTON,
                    halign="left",
                    valign="middle",
                    background_normal="",
                    background_down="",
                    background_color=BUTON,
                )
                btn.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))
                btn.bind(
                    on_release=lambda _btn, p=dosya: _secim_yaz(str(p))
                )
                liste_container.add_widget(btn)
                toplam += 1

            if toplam == 0:
                bos = Label(
                    text="Bu klasörde gösterilecek öğe yok.",
                    color=METIN,
                    size_hint_y=None,
                    height=YUKSEKLIK_BUTON,
                    halign="left",
                    valign="middle",
                )
                bos.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))
                liste_container.add_widget(bos)

            Logger.info(
                f"TestDosyaSecPopup: klasor yuklendi={hedef} oge_sayisi={toplam}"
            )

        except Exception as exc:
            Logger.exception(f"TestDosyaSecPopup: klasor yukleme hatasi: {exc}")
            hata = Label(
                text=f"Hata: {exc}",
                color=METIN,
                size_hint_y=None,
                height=YUKSEKLIK_BUTON * 2,
                halign="left",
                valign="middle",
            )
            hata.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))
            liste_container.add_widget(hata)

    def _yukari(_btn) -> None:
        parent = mevcut_klasor.parent
        if parent and parent != mevcut_klasor:
            _klasor_yukle(parent)

    def _yenile(_btn) -> None:
        _klasor_yukle(mevcut_klasor)

    def _sec(_btn) -> None:
        raw = str(secili_dosya["path"] or "").strip()
        Logger.info(f"TestDosyaSecPopup: sec butonu secim={raw!r}")
        popup.dismiss()
        on_secildi(raw)

    def _iptal(_btn) -> None:
        Logger.info("TestDosyaSecPopup: iptal")
        popup.dismiss()
        on_secildi("")

    yukari_btn.bind(on_release=_yukari)
    yenile_btn.bind(on_release=_yenile)
    sec_btn.bind(on_release=_sec)
    iptal_btn.bind(on_release=_iptal)

    _klasor_yukle(mevcut_klasor)

    popup.open()
    Logger.info("TestDosyaSecPopup: popup acildi")


def _servisten_baslangic_yolu_al(services) -> str | None:
    """
    Servisten son kayıtlı başlangıç yolunu alır.
    """
    try:
        return services.son_klasor().picker_baslangic_kaynagi()
    except Exception as exc:
        Logger.warning(f"TestDosyaSecPopup: servis baslangic yolu alinamadi: {exc}")
        return None


def _popup_baslangic_yolu(start_path: str | None) -> str:
    """
    Popup için güvenli başlangıç klasörü çözer.
    """
    adaylar: list[str] = []

    raw = str(start_path or "").strip()
    if raw and not raw.startswith("content://"):
        adaylar.append(raw)

    adaylar.extend(
        [
            "/storage/emulated/0",
            "/storage/emulated/0/Download",
            "/storage/emulated/0/Documents",
            "/sdcard",
            "/storage/self/primary",
            "/",
        ]
    )

    for aday in adaylar:
        try:
            p = Path(aday)
            if p.exists() and p.is_dir():
                return str(p)
        except Exception:
            continue

    return "/"
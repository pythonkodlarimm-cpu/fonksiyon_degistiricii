# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/popup/dosya_sec_popup.py

ROL:
- Platforma ve moda göre uygun dosya seçiciyi açar
- Test modu açıksa manuel popup picker kullanır
- Test modu kapalıysa Android'de SAF picker akışını çalıştırır
- Android dışı ortamlarda manuel popup picker kullanır
- Seçim sonrası callback çalıştırır
- Dil entegrasyonuna uyumludur

MİMARİ:
- UI katmanıdır
- IO işlemi yapmaz
- Test ve üretim akışını tek noktadan yönetir
- Path / URI ayrımını taşıyıcı olarak korur
- Geriye uyumluluk katmanı içermez

NOT:
- Test modundaki manuel popup picker path döndürür
- Android üretim akışı çoğunlukla content:// URI döndürür
- Çağıran katman bu farkı services üzerinden çözmelidir

SURUM: 12
TARIH: 2026-03-28
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from kivy.logger import Logger
from kivy.utils import platform

from app.config import ayri_popup_dosya_secici_kullan


def dosya_sec(
    *,
    services,
    on_secildi: Callable[[str], None],
    title: str = "Dosya Seç",
) -> None:
    """
    Uygun dosya seçiciyi açar.

    Karar:
    - Test modu açıksa: manuel popup picker
    - Test modu kapalı + Android: SAF picker
    - Diğer ortamlar: manuel popup picker
    """
    t = services.dil_servisi().t

    secici_baslik = str(t("file_picker_title") or title or "Dosya Seçici")
    if secici_baslik == "file_picker_title":
        secici_baslik = str(title or "Dosya Seçici")

    Logger.info(
        f"DosyaSecPopup: giris platform={platform} "
        f"test_popup={ayri_popup_dosya_secici_kullan()}"
    )

    if ayri_popup_dosya_secici_kullan():
        Logger.info("DosyaSecPopup: test modunda manuel popup picker kullaniliyor")
        _manuel_popup_picker(
            services=services,
            on_secildi=on_secildi,
            title=secici_baslik,
        )
        return

    if platform == "android":
        Logger.info("DosyaSecPopup: android SAF picker secildi")
        _android_picker(
            services=services,
            on_secildi=on_secildi,
        )
        return

    Logger.info("DosyaSecPopup: desktop manuel popup picker secildi")
    _manuel_popup_picker(
        services=services,
        on_secildi=on_secildi,
        title=secici_baslik,
    )


def _android_picker(
    *,
    services,
    on_secildi: Callable[[str], None],
) -> None:
    """
    Android SAF picker açar.
    """
    Logger.info("DosyaSecPopup: _android_picker girdi")

    android = services.android()

    try:
        initial_uri = services.son_klasor().android_picker_baslangic_uri()
        Logger.info(f"DosyaSecPopup: initial_uri={initial_uri!r}")
    except Exception as exc:
        Logger.warning(f"DosyaSecPopup: initial_uri alinamadi: {exc}")
        initial_uri = None

    def _callback(uri: str) -> None:
        raw = str(uri or "").strip()
        Logger.info(f"DosyaSecPopup: android callback uri={raw!r}")
        on_secildi(raw)

    android.open_file_picker(
        _callback,
        initial_uri=initial_uri,
        mime_types=[
            "text/x-python",
            "text/plain",
            "application/json",
            "*/*",
        ],
    )

    Logger.info("DosyaSecPopup: android.open_file_picker cagrildi")


def _manuel_popup_picker(
    *,
    services,
    on_secildi: Callable[[str], None],
    title: str,
) -> None:
    """
    Test modu için manuel popup picker açar.
    """
    from kivy.metrics import dp
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.popup import Popup
    from kivy.uix.scrollview import ScrollView

    Logger.info("DosyaSecPopup: _manuel_popup_picker girdi")

    t = services.dil_servisi().t

    def _tr(key: str, fallback: str) -> str:
        text = str(t(key) or "").strip()
        if not text or text == key:
            return fallback
        return text

    baslangic_yolu = _popup_baslangic_yolu(
        _servisten_baslangic_yolu_al(services)
    )
    mevcut_klasor = Path(baslangic_yolu)

    root = BoxLayout(
        orientation="vertical",
        spacing=dp(8),
        padding=dp(8),
    )

    durum_label = Label(
        text=_tr("test_file_picker_title", "Test Dosya Seçici"),
        size_hint_y=None,
        height=dp(44),
        halign="left",
        valign="middle",
    )
    durum_label.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))
    root.add_widget(durum_label)

    konum_label = Label(
        text=f"{_tr('target_folder', 'Hedef klasör')}: {mevcut_klasor}",
        size_hint_y=None,
        height=dp(64),
        halign="left",
        valign="middle",
    )
    konum_label.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))
    root.add_widget(konum_label)

    secim_label = Label(
        text=f"{_tr('selected_prefix', 'Seçildi:')} -",
        size_hint_y=None,
        height=dp(44),
        halign="left",
        valign="middle",
    )
    secim_label.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))
    root.add_widget(secim_label)

    ust_butonlar = BoxLayout(
        orientation="horizontal",
        spacing=dp(8),
        size_hint_y=None,
        height=dp(48),
    )

    yukari_btn = Button(text=_tr("back", "Yukarı"))
    yenile_btn = Button(text=_tr("update", "Yenile"))

    ust_butonlar.add_widget(yukari_btn)
    ust_butonlar.add_widget(yenile_btn)
    root.add_widget(ust_butonlar)

    scroll = ScrollView()
    root.add_widget(scroll)

    liste_container = BoxLayout(
        orientation="vertical",
        spacing=dp(8),
        size_hint_y=None,
    )
    liste_container.bind(
        minimum_height=lambda inst, val: setattr(inst, "height", val)
    )
    scroll.add_widget(liste_container)

    alt_butonlar = BoxLayout(
        orientation="horizontal",
        spacing=dp(8),
        size_hint_y=None,
        height=dp(48),
    )

    iptal_btn = Button(text=_tr("cancel", "Vazgeç"))
    sec_btn = Button(text=_tr("select_file", "Dosya Seç"))

    alt_butonlar.add_widget(iptal_btn)
    alt_butonlar.add_widget(sec_btn)
    root.add_widget(alt_butonlar)

    test_modu_etiketi = _tr("test", "Test")
    popup = Popup(
        title=f"{title} [{test_modu_etiketi}]",
        content=root,
        size_hint=(0.95, 0.95),
    )

    secili_dosya: dict[str, str] = {"path": ""}

    def _secim_yaz(path: str) -> None:
        raw = str(path or "").strip()
        secili_dosya["path"] = raw
        secim_label.text = f"{_tr('selected_prefix', 'Seçildi:')} {raw or '-'}"

    def _satir_butonu_olustur(text: str, callback) -> Button:
        btn = Button(
            text=text,
            size_hint_y=None,
            height=dp(48),
            halign="left",
            valign="middle",
        )
        btn.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))
        btn.bind(on_release=callback)
        return btn

    def _gorunur_mu(item: Path) -> bool:
        ad = item.name.strip()
        if not ad:
            return False

        if ad.startswith("."):
            return False

        return True

    def _dosya_gosterilsin_mi(item: Path) -> bool:
        if not item.is_file():
            return False
        return item.suffix.lower() in {
            ".py",
            ".txt",
            ".json",
            ".md",
            ".log",
            ".cfg",
            ".ini",
            ".yaml",
            ".yml",
        }

    def _klasor_yukle(hedef: Path) -> None:
        nonlocal mevcut_klasor

        try:
            hedef = hedef.resolve()
        except Exception:
            hedef = Path(str(hedef or "/"))

        if not hedef.exists() or not hedef.is_dir():
            Logger.warning(f"DosyaSecPopup: gecersiz klasor={hedef}")
            return

        mevcut_klasor = hedef
        konum_label.text = f"{_tr('target_folder', 'Hedef klasör')}: {mevcut_klasor}"
        _secim_yaz("")
        liste_container.clear_widgets()

        try:
            klasorler: list[Path] = []
            dosyalar: list[Path] = []

            for item in hedef.iterdir():
                try:
                    if not _gorunur_mu(item):
                        continue

                    if item.is_dir():
                        klasorler.append(item)
                    elif _dosya_gosterilsin_mi(item):
                        dosyalar.append(item)
                except Exception:
                    continue

            klasorler.sort(key=lambda p: p.name.lower())
            dosyalar.sort(key=lambda p: p.name.lower())

            toplam = 0

            for klasor in klasorler:
                btn = _satir_butonu_olustur(
                    f"[{_tr('list', 'Liste')}] {klasor.name}",
                    lambda _btn, p=klasor: _klasor_yukle(p),
                )
                liste_container.add_widget(btn)
                toplam += 1

            for dosya in dosyalar:
                btn = _satir_butonu_olustur(
                    dosya.name,
                    lambda _btn, p=dosya: _secim_yaz(str(p)),
                )
                liste_container.add_widget(btn)
                toplam += 1

            if toplam == 0:
                bos = Label(
                    text=_tr("no_backups_for_filter", "Bu filtre için yedek bulunamadı."),
                    size_hint_y=None,
                    height=dp(48),
                    halign="left",
                    valign="middle",
                )
                bos.bind(size=lambda inst, _val: setattr(inst, "text_size", inst.size))
                liste_container.add_widget(bos)

            Logger.info(
                f"DosyaSecPopup: klasor yuklendi={hedef} oge_sayisi={toplam}"
            )

        except Exception as exc:
            Logger.exception(f"DosyaSecPopup: klasor yukleme hatasi: {exc}")
            hata = Label(
                text=f"{_tr('error_title', 'Hata Detayı')}: {exc}",
                size_hint_y=None,
                height=dp(96),
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
        Logger.info(f"DosyaSecPopup: sec butonu secim={raw!r}")
        popup.dismiss()
        on_secildi(raw)

    def _iptal(_btn) -> None:
        Logger.info("DosyaSecPopup: iptal")
        popup.dismiss()
        on_secildi("")

    yukari_btn.bind(on_release=_yukari)
    yenile_btn.bind(on_release=_yenile)
    sec_btn.bind(on_release=_sec)
    iptal_btn.bind(on_release=_iptal)

    _klasor_yukle(mevcut_klasor)

    popup.open()
    Logger.info("DosyaSecPopup: manuel popup acildi")


def _servisten_baslangic_yolu_al(services) -> str | None:
    """
    Servisten son kayıtlı başlangıç yolunu alır.
    """
    try:
        return services.son_klasor().picker_baslangic_kaynagi()
    except Exception as exc:
        Logger.warning(f"DosyaSecPopup: servis baslangic yolu alinamadi: {exc}")
        return None


def _popup_baslangic_yolu(start_path: str | None) -> str:
    """
    Manuel popup picker için güvenli başlangıç klasörü çözer.
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
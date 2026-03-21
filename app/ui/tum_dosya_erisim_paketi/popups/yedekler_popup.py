# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paketi/popups/yedekler_popup.py

ROL:
- Yedek dosyalarını popup içinde listelemek
- Filtreleme yapmak
- Görüntüleme, indirme ve silme akışlarını başlatmak
- Toplu silme akışını yönetmek

MİMARİ:
- Doğrudan ortak bileşen import etmez
- Ortak yonetici üzerinden erişir
- Popup akışları yeni popups yolu üzerinden çağrılır
- Yedek satırı ve indirme işlemi yedek katmanı üzerinden çağrılır

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 3
TARIH: 2026-03-19
IMZA: FY.
"""

from __future__ import annotations

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY
from app.ui.tum_dosya_erisim_paketi.ortak.yoneticisi import (
    TumDosyaErisimOrtakYoneticisi,
)


def _ortak_yonetici():
    return TumDosyaErisimOrtakYoneticisi()


def _tiklanabilir_icon_sinifi():
    try:
        return _ortak_yonetici().tiklanabilir_icon_sinifi()
    except Exception:
        return None


def _animated_separator_widget():
    try:
        sinif = _ortak_yonetici().animated_separator_sinifi()
        return sinif()
    except Exception:
        return None


def _yedek_listeleme_modulu():
    from app.services.yedek import YedekYoneticisi
    return YedekYoneticisi()


def _yedek_satiri_yoneticisi():
    from app.ui.tum_dosya_erisim_paketi.yedek import TumDosyaErisimYedekYoneticisi
    return TumDosyaErisimYedekYoneticisi()


def _show_simple_popup(**kwargs):
    from app.ui.tum_dosya_erisim_paketi.popups.basit_popup import show_simple_popup
    return show_simple_popup(**kwargs)


def _show_confirm_popup(**kwargs):
    from app.ui.tum_dosya_erisim_paketi.popups.onay_popup import show_confirm_popup
    return show_confirm_popup(**kwargs)


def _open_backup_view_popup(yedek):
    from app.ui.tum_dosya_erisim_paketi.popups.yedek_goruntuleme_popup import (
        open_backup_view_popup,
    )
    return open_backup_view_popup(yedek)


def _silme_durum_popup_sinifi():
    from app.ui.tum_dosya_erisim_paketi.popups.silme_durum_popup import (
        SilmeDurumPopup,
    )
    return SilmeDurumPopup


def open_backups_popup(debug=None):
    yedek_yoneticisi = _yedek_listeleme_modulu()
    yedek_ui_yoneticisi = _yedek_satiri_yoneticisi()

    aktif_filtre = {"tip": "bugun", "tarih": ""}

    content = BoxLayout(
        orientation="vertical",
        padding=dp(14),
        spacing=dp(10),
    )

    title = Label(
        text="Yedeklenen Dosyalar",
        color=TEXT_PRIMARY,
        font_size="18sp",
        bold=True,
        size_hint_y=None,
        height=dp(28),
        halign="center",
        valign="middle",
    )
    title.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    content.add_widget(title)

    info = Label(
        text="Yedekler yükleniyor...",
        color=TEXT_MUTED,
        font_size="12sp",
        size_hint_y=None,
        height=dp(20),
        halign="center",
        valign="middle",
    )
    info.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    content.add_widget(info)

    ust_toolbar = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(44),
        spacing=dp(10),
    )

    ust_toolbar.add_widget(Label(size_hint_x=1))

    IconClass = _tiklanabilir_icon_sinifi()
    if IconClass is not None:
        try:
            tumunu_sil_btn = IconClass(
                source="app/assets/icons/delete.png",
                size_hint=(None, None),
                size=(dp(34), dp(34)),
                allow_stretch=True,
                keep_ratio=True,
            )
        except Exception:
            tumunu_sil_btn = Label(size_hint=(None, None), size=(dp(34), dp(34)))
    else:
        tumunu_sil_btn = Label(size_hint=(None, None), size=(dp(34), dp(34)))

    tumunu_sil_wrap = BoxLayout(
        orientation="horizontal",
        size_hint_x=None,
        width=dp(48),
    )
    tumunu_sil_wrap.add_widget(tumunu_sil_btn)
    ust_toolbar.add_widget(tumunu_sil_wrap)

    content.add_widget(ust_toolbar)

    sep1 = _animated_separator_widget()
    if sep1 is not None:
        content.add_widget(sep1)

    filtre_satiri_1 = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(40),
        spacing=dp(8),
    )

    btn_tumu = Button(
        text="Tümü",
        size_hint_x=1,
        background_normal="",
        color=(0.95, 0.95, 0.98, 1),
    )
    btn_bugun = Button(
        text="Bugün",
        size_hint_x=1,
        background_normal="",
        color=(0.95, 0.95, 0.98, 1),
    )
    btn_dun = Button(
        text="Dün",
        size_hint_x=1,
        background_normal="",
        color=(0.95, 0.95, 0.98, 1),
    )
    btn_son7 = Button(
        text="Son 7 Gün",
        size_hint_x=1.2,
        background_normal="",
        color=(0.95, 0.95, 0.98, 1),
    )

    filtre_satiri_1.add_widget(btn_tumu)
    filtre_satiri_1.add_widget(btn_bugun)
    filtre_satiri_1.add_widget(btn_dun)
    filtre_satiri_1.add_widget(btn_son7)
    content.add_widget(filtre_satiri_1)

    filtre_satiri_2 = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(42),
        spacing=dp(8),
    )

    tarih_input = TextInput(
        hint_text="Tarih ara: 2026-03-18 veya 18.03.2026",
        multiline=False,
        size_hint_x=1,
        size_hint_y=None,
        height=dp(42),
        background_normal="",
        background_active="",
        background_color=(0.12, 0.12, 0.16, 1),
        foreground_color=(0.95, 0.95, 0.98, 1),
        hint_text_color=(0.55, 0.58, 0.65, 1),
        cursor_color=(0.2, 0.85, 0.4, 1),
        padding=[dp(12), dp(10), dp(12), dp(10)],
    )

    btn_tarih_ara = Button(
        text="Tarih Ara",
        size_hint_x=None,
        width=dp(110),
        background_normal="",
        background_color=(0.18, 0.18, 0.22, 1),
        color=(0.95, 0.95, 0.98, 1),
    )

    filtre_satiri_2.add_widget(tarih_input)
    filtre_satiri_2.add_widget(btn_tarih_ara)
    content.add_widget(filtre_satiri_2)

    sep2 = _animated_separator_widget()
    if sep2 is not None:
        content.add_widget(sep2)

    scroll = ScrollView(
        do_scroll_x=False,
        do_scroll_y=True,
        bar_width=dp(8),
    )

    liste = BoxLayout(
        orientation="vertical",
        spacing=dp(8),
        size_hint_y=None,
    )
    liste.bind(minimum_height=liste.setter("height"))

    scroll.add_widget(liste)
    content.add_widget(scroll)

    popup = Popup(
        title="",
        content=content,
        size_hint=(0.94, 0.82),
        auto_dismiss=True,
        separator_height=0,
    )

    def _safe_debug(message: str) -> None:
        try:
            if callable(debug):
                debug(str(message))
        except Exception:
            pass

    def _filtre_bilgi_metni(yedek_sayisi: int) -> str:
        tip = aktif_filtre.get("tip", "tum")
        tarih = str(aktif_filtre.get("tarih", "") or "").strip()

        if tip == "bugun":
            return f"Bugünkü yedekler: {yedek_sayisi}"
        if tip == "dun":
            return f"Dünkü yedekler: {yedek_sayisi}"
        if tip == "son7":
            return f"Son 7 gün: {yedek_sayisi}"
        if tip == "tarih" and tarih:
            return f"{tarih} için yedekler: {yedek_sayisi}"
        return f"Toplam yedek: {yedek_sayisi}"

    def _renkleri_guncelle():
        secili = (0.18, 0.55, 0.28, 1)
        normal = (0.18, 0.18, 0.22, 1)

        btn_tumu.background_color = secili if aktif_filtre["tip"] == "tum" else normal
        btn_bugun.background_color = secili if aktif_filtre["tip"] == "bugun" else normal
        btn_dun.background_color = secili if aktif_filtre["tip"] == "dun" else normal
        btn_son7.background_color = secili if aktif_filtre["tip"] == "son7" else normal

    def _yedekleri_getir():
        tip = aktif_filtre.get("tip", "tum")
        tarih = str(aktif_filtre.get("tarih", "") or "").strip()

        if tip == "bugun":
            return yedek_yoneticisi.yedekleri_listele(bugun=True)
        if tip == "dun":
            return yedek_yoneticisi.yedekleri_listele(dun=True)
        if tip == "son7":
            return yedek_yoneticisi.yedekleri_listele(son_gun=7)
        if tip == "tarih" and tarih:
            return yedek_yoneticisi.yedekleri_listele(tarih=tarih)

        return yedek_yoneticisi.yedekleri_listele()

    def _ilk_filtreyi_belirle():
        try:
            bugun_listesi = yedek_yoneticisi.yedekleri_listele(bugun=True)
            if bugun_listesi:
                aktif_filtre["tip"] = "bugun"
                aktif_filtre["tarih"] = ""
                return
        except Exception as exc:
            _safe_debug(f"Bugün filtresi ilk yükte alınamadı: {exc}")

        try:
            dun_listesi = yedek_yoneticisi.yedekleri_listele(dun=True)
            if dun_listesi:
                aktif_filtre["tip"] = "dun"
                aktif_filtre["tarih"] = ""
                return
        except Exception as exc:
            _safe_debug(f"Dün filtresi ilk yükte alınamadı: {exc}")

        try:
            son7_listesi = yedek_yoneticisi.yedekleri_listele(son_gun=7)
            if son7_listesi:
                aktif_filtre["tip"] = "son7"
                aktif_filtre["tarih"] = ""
                return
        except Exception as exc:
            _safe_debug(f"Son 7 gün filtresi ilk yükte alınamadı: {exc}")

        aktif_filtre["tip"] = "tum"
        aktif_filtre["tarih"] = ""

    def refresh_list():
        _renkleri_guncelle()

        try:
            yedekler = _yedekleri_getir()
        except Exception as exc:
            _safe_debug(f"Yedek listeleme hatası: {exc}")
            yedekler = []

        try:
            info.text = _filtre_bilgi_metni(len(yedekler))
        except Exception:
            pass

        try:
            liste.clear_widgets()
        except Exception:
            pass

        if not yedekler:
            bos = Label(
                text="Bu filtre için yedek bulunamadı.",
                color=TEXT_MUTED,
                size_hint_y=None,
                height=dp(36),
                halign="center",
                valign="middle",
            )
            bos.bind(size=lambda inst, size: setattr(inst, "text_size", size))
            liste.add_widget(bos)
            return

        for yedek in yedekler:
            def on_view(y):
                _open_backup_view_popup(y)

            def on_download(y):
                try:
                    yedek_ui_yoneticisi.yedek_indirme_islemi_baslat(
                        debug or (lambda *_: None),
                        y,
                    )
                except Exception as exc:
                    _show_simple_popup(
                        title_text="İndirme Hatası",
                        body_text=f"Yedek kopyalanamadı:\n{exc}",
                        icon_name="warning.png",
                        auto_close_seconds=1.8,
                        compact=True,
                    )

            def _tekli_sil_onayli(y):
                SilmeDurumPopup = _silme_durum_popup_sinifi()

                durum_popup = SilmeDurumPopup(
                    title_text="Silme İşlemi",
                    body_text="Yedek siliniyor...",
                    success_text="Yedek başarıyla silindi.",
                    icon_name="onaylandi.png",
                ).open()

                durum_popup.set_progress(0.15, "Silme işlemi başlatıldı...")
                durum_popup.set_progress(0.35, "Yedek hazırlanıyor...")

                def _silme_adimi(_dt):
                    try:
                        durum_popup.set_progress(0.65, "Yedek siliniyor...")
                        silinen = yedek_yoneticisi.yedegi_sil(y)
                        _safe_debug(f"Yedek silindi: {silinen}")

                        refresh_list()

                        durum_popup.finish_success(
                            text="Yedek başarıyla silindi.",
                            auto_close_seconds=1.6,
                        )
                    except Exception as exc:
                        _safe_debug(f"Yedek silme hatası: {exc}")
                        durum_popup.dismiss()
                        _show_simple_popup(
                            title_text="Silme Hatası",
                            body_text=f"Yedek silinemedi:\n{exc}",
                            icon_name="warning.png",
                            auto_close_seconds=1.8,
                            compact=True,
                        )

                Clock.schedule_once(_silme_adimi, 0.18)

            def on_delete(y):
                _show_confirm_popup(
                    title_text="Yedeği Sil",
                    body_text=(
                        f"Bu yedek silinecek:\n{getattr(y, 'name', '')}\n\n"
                        "Bu işlem geri alınamaz."
                    ),
                    on_confirm=lambda: _tekli_sil_onayli(y),
                    confirm_icon="delete.png",
                )

            try:
                liste.add_widget(
                    yedek_ui_yoneticisi.yedek_satiri_olustur(
                        yedek,
                        on_view,
                        on_download,
                        on_delete,
                    )
                )
            except Exception as exc:
                _safe_debug(f"Yedek satırı oluşturulamadı: {yedek} | {exc}")

    def _toplu_sil_onayli():
        SilmeDurumPopup = _silme_durum_popup_sinifi()

        durum_popup = SilmeDurumPopup(
            title_text="Toplu Silme",
            body_text="Yedekler siliniyor...",
            success_text="Toplu silme tamamlandı.",
            icon_name="onaylandi.png",
        ).open()

        durum_popup.set_progress(0.12, "Silme işlemi başlatıldı...")
        durum_popup.set_progress(0.28, "Yedekler taranıyor...")

        def _silme_adimi(_dt):
            try:
                durum_popup.set_progress(0.62, "Yedekler siliniyor...")
                silinen_sayi = yedek_yoneticisi.tum_yedekleri_sil()
                _safe_debug(f"Toplu yedek silindi: {silinen_sayi}")

                refresh_list()

                if silinen_sayi <= 0:
                    durum_popup.dismiss()
                    _show_simple_popup(
                        title_text="Bilgi",
                        body_text="Silinecek yedek bulunamadı.",
                        icon_name="warning.png",
                        auto_close_seconds=1.5,
                        compact=True,
                    )
                else:
                    durum_popup.finish_success(
                        text=f"{silinen_sayi} yedek silindi.",
                        auto_close_seconds=1.8,
                    )
            except Exception as exc:
                _safe_debug(f"Toplu yedek silme hatası: {exc}")
                durum_popup.dismiss()
                _show_simple_popup(
                    title_text="Toplu Silme Hatası",
                    body_text=f"Yedekler silinemedi:\n{exc}",
                    icon_name="warning.png",
                    auto_close_seconds=1.8,
                    compact=True,
                )

        Clock.schedule_once(_silme_adimi, 0.22)

    def tumunu_sil(*_args):
        _show_confirm_popup(
            title_text="Tüm Yedekleri Sil",
            body_text="Listelenen tüm .bak dosyaları silinecek.\nBu işlem geri alınamaz.",
            on_confirm=_toplu_sil_onayli,
            confirm_icon="delete.png",
        )

    def filtre_tumu(*_args):
        aktif_filtre["tip"] = "tum"
        aktif_filtre["tarih"] = ""
        refresh_list()

    def filtre_bugun(*_args):
        aktif_filtre["tip"] = "bugun"
        aktif_filtre["tarih"] = ""
        refresh_list()

    def filtre_dun(*_args):
        aktif_filtre["tip"] = "dun"
        aktif_filtre["tarih"] = ""
        refresh_list()

    def filtre_son7(*_args):
        aktif_filtre["tip"] = "son7"
        aktif_filtre["tarih"] = ""
        refresh_list()

    def filtre_tarih_ara(*_args):
        tarih_text = str(tarih_input.text or "").strip()
        if not tarih_text:
            _show_simple_popup(
                title_text="Tarih Gerekli",
                body_text="Lütfen bir tarih girin.",
                icon_name="warning.png",
                auto_close_seconds=1.5,
                compact=True,
            )
            return

        aktif_filtre["tip"] = "tarih"
        aktif_filtre["tarih"] = tarih_text
        refresh_list()

    try:
        tumunu_sil_btn.bind(on_release=tumunu_sil)
    except Exception:
        pass

    btn_tumu.bind(on_release=filtre_tumu)
    btn_bugun.bind(on_release=filtre_bugun)
    btn_dun.bind(on_release=filtre_dun)
    btn_son7.bind(on_release=filtre_son7)
    btn_tarih_ara.bind(on_release=filtre_tarih_ara)
    tarih_input.bind(on_text_validate=filtre_tarih_ara)

    _ilk_filtreyi_belirle()
    _renkleri_guncelle()
    refresh_list()
    popup.open()
    return popup
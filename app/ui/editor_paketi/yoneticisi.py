# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/yoneticisi.py

ROL:
- Editor paketine tek giriş noktası sağlamak
- Alt paket yöneticilerini merkezileştirmek
- Üst katmanın editor paketi iç yapısını bilmesini engellemek
- Panel, root, aksiyon, popup, doğrulama, bildirim, bileşen ve yardımcı akışları tek yerden sunmak
- Editör popup ve panel akışlarında seçili dil destekli metinlerin aşağı katmanda korunmasına aracılık etmek
- Yeni eklenen yapıştır aksiyonunu ve ilgili bileşen erişimlerini üst katmana taşımak

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt paketlere doğrudan erişim yerine ilgili yönetici sınıfları kullanılır
- Lazy import + yönetici katmanı korunur
- Paket dışına iç modül detayları sızdırılmaz
- Editor paneli oluşturma akışı üst katmandan gelen callback'leri bozmadan aşağı taşır
- Popup ve yardımcı akışlar ilgili alt yöneticiler üzerinden merkezi biçimde yürütülür
- Tekrarlayan yönetici oluşturma maliyetini azaltmak için instance cache kullanılır
- Cache bozulursa kendini toparlayacak şekilde yeniden resolve yapabilir
- Dil entegrasyonu bozulmadan yeni anahtar bazlı bildirim akışlarını da taşıyabilir
- Fail-soft yaklaşım korunur; alt yönetici yüklenemese bile üst katman çökmez

API UYUMLULUK:
- Platform bağımsızdır
- Android API 35 ile uyumludur
- Doğrudan Android bridge çağrısı içermez

SURUM: 5
TARIH: 2026-03-26
IMZA: FY.
"""

from __future__ import annotations

import traceback


class EditorYoneticisi:
    """
    Editor paketi için merkezi üst yönetici.
    """

    def __init__(self) -> None:
        self._yonetici_cache: dict[str, object] = {}

    # =========================================================
    # INTERNAL
    # =========================================================
    def _cache_get(self, key: str):
        """
        Yönetici cache içinden güvenli biçimde değer döndürür.
        """
        try:
            return self._yonetici_cache.get(key)
        except Exception:
            return None

    def _cache_set(self, key: str, value) -> None:
        """
        Yönetici cache içine güvenli biçimde değer yazar.
        """
        try:
            self._yonetici_cache[key] = value
        except Exception:
            pass

    def _cache_delete(self, key: str) -> None:
        """
        Tek bir cache kaydını siler.
        """
        try:
            if key in self._yonetici_cache:
                del self._yonetici_cache[key]
        except Exception:
            pass

    def cache_temizle(self) -> None:
        """
        Tüm alt yönetici cache'lerini temizler.
        """
        try:
            self._yonetici_cache = {}
        except Exception:
            pass

    def _get_or_create_manager(
        self,
        cache_key: str,
        import_path: str,
        class_name: str,
    ):
        """
        İstenen alt yöneticiyi lazy import + instance cache ile üretir.
        """
        try:
            cached = self._cache_get(cache_key)
            if cached is not None:
                return cached
        except Exception:
            self._cache_delete(cache_key)

        try:
            module = __import__(import_path, fromlist=[class_name])
            cls = getattr(module, class_name, None)

            if cls is None:
                print(
                    "[EDITOR_YONETICISI] "
                    f"Yönetici sınıfı bulunamadı: {import_path}.{class_name}"
                )
                self._cache_delete(cache_key)
                return None

            instance = cls()
            self._cache_set(cache_key, instance)
            return instance

        except Exception:
            print(
                "[EDITOR_YONETICISI] "
                f"Yönetici yüklenemedi: {import_path}.{class_name}"
            )
            print(traceback.format_exc())
            self._cache_delete(cache_key)
            return None

    # =========================================================
    # ALT YONETICILER
    # =========================================================
    def _panel_yoneticisi(self):
        return self._get_or_create_manager(
            "panel_yoneticisi",
            "app.ui.editor_paketi.panel",
            "PanelYoneticisi",
        )

    def _root_yoneticisi(self):
        return self._get_or_create_manager(
            "root_yoneticisi",
            "app.ui.editor_paketi.root",
            "RootYoneticisi",
        )

    def _aksiyon_yoneticisi(self):
        return self._get_or_create_manager(
            "aksiyon_yoneticisi",
            "app.ui.editor_paketi.aksiyon",
            "AksiyonYoneticisi",
        )

    def _popup_yoneticisi(self):
        return self._get_or_create_manager(
            "popup_yoneticisi",
            "app.ui.editor_paketi.popup",
            "PopupYoneticisi",
        )

    def _dogrulama_yoneticisi(self):
        return self._get_or_create_manager(
            "dogrulama_yoneticisi",
            "app.ui.editor_paketi.dogrulama",
            "DogrulamaYoneticisi",
        )

    def _bildirim_yoneticisi(self):
        return self._get_or_create_manager(
            "bildirim_yoneticisi",
            "app.ui.editor_paketi.bildirim",
            "BildirimYoneticisi",
        )

    def _bilesenler_yoneticisi(self):
        return self._get_or_create_manager(
            "bilesenler_yoneticisi",
            "app.ui.editor_paketi.bilesenler",
            "BilesenlerYoneticisi",
        )

    def _yardimci_yoneticisi(self):
        return self._get_or_create_manager(
            "yardimci_yoneticisi",
            "app.ui.editor_paketi.yardimci",
            "YardimciYoneticisi",
        )

    # =========================================================
    # PANEL
    # =========================================================
    def panel_sinifi(self):
        """
        EditorPaneli sınıfını döndürür.
        """
        yonetici = self._panel_yoneticisi()
        return yonetici.panel_sinifi() if yonetici is not None else None

    def panel_olustur(self, **kwargs):
        """
        EditorPaneli örneği oluşturur.
        """
        yonetici = self._panel_yoneticisi()
        return yonetici.panel_olustur(**kwargs) if yonetici is not None else None

    # =========================================================
    # ROOT
    # =========================================================
    def root_sinifi(self):
        """
        Editor root sınıfını döndürür.
        """
        yonetici = self._root_yoneticisi()
        return yonetici.root_sinifi() if yonetici is not None else None

    def root_olustur(self, **kwargs):
        """
        Editor root örneği oluşturur.
        """
        yonetici = self._root_yoneticisi()
        return yonetici.root_olustur(**kwargs) if yonetici is not None else None

    # =========================================================
    # AKSIYON
    # =========================================================
    def copy_current_to_new(self, panel, *_args):
        """
        Mevcut kodu yeni kod alanına kopyalar.
        """
        yonetici = self._aksiyon_yoneticisi()
        return (
            yonetici.copy_current_to_new(panel, *_args)
            if yonetici is not None
            else None
        )

    def paste_new_code(self, panel, *_args):
        """
        Panodaki içeriği yeni kod alanına yapıştırır.
        """
        yonetici = self._aksiyon_yoneticisi()
        return (
            yonetici.paste_new_code(panel, *_args)
            if yonetici is not None
            else None
        )

    def clear_new_code(self, panel, *_args):
        """
        Yeni kod alanını temizler.
        """
        yonetici = self._aksiyon_yoneticisi()
        return (
            yonetici.clear_new_code(panel, *_args)
            if yonetici is not None
            else None
        )

    def check_new_code(self, panel, *_args):
        """
        Yeni kod doğrulamasını başlatır.
        """
        yonetici = self._aksiyon_yoneticisi()
        return (
            yonetici.check_new_code(panel, *_args)
            if yonetici is not None
            else None
        )

    def handle_update(self, panel, *_args):
        """
        Güncelleme akışını başlatır.
        """
        yonetici = self._aksiyon_yoneticisi()
        return (
            yonetici.handle_update(panel, *_args)
            if yonetici is not None
            else None
        )

    def handle_restore(self, panel, *_args):
        """
        Geri yükleme akışını başlatır.
        """
        yonetici = self._aksiyon_yoneticisi()
        return (
            yonetici.handle_restore(panel, *_args)
            if yonetici is not None
            else None
        )

    # =========================================================
    # POPUP
    # =========================================================
    def build_popup_toolbar(self, actions):
        """
        Popup araç çubuğu oluşturur.
        """
        yonetici = self._popup_yoneticisi()
        return yonetici.build_popup_toolbar(actions) if yonetici is not None else None

    def open_current_code_popup(self, panel, *_args):
        """
        Mevcut kod popup'ını açar.
        """
        yonetici = self._popup_yoneticisi()
        return (
            yonetici.open_current_code_popup(panel, *_args)
            if yonetici is not None
            else None
        )

    def open_new_code_editor_popup(self, panel, *_args):
        """
        Yeni kod düzenleme popup'ını açar.
        """
        yonetici = self._popup_yoneticisi()
        return (
            yonetici.open_new_code_editor_popup(panel, *_args)
            if yonetici is not None
            else None
        )

    # =========================================================
    # DOGRULAMA
    # =========================================================
    def normalize_code_text(self, text, trim_outer_blank_lines: bool = False) -> str:
        """
        Kod metnini normalize eder.
        """
        yonetici = self._dogrulama_yoneticisi()
        if yonetici is None:
            try:
                return str(text or "")
            except Exception:
                return ""
        return yonetici.normalize_code_text(
            text,
            trim_outer_blank_lines=trim_outer_blank_lines,
        )

    def first_meaningful_line(self, text: str) -> str:
        """
        İlk anlamlı satırı döndürür.
        """
        yonetici = self._dogrulama_yoneticisi()
        return yonetici.first_meaningful_line(text) if yonetici is not None else ""

    def looks_like_full_function(self, text: str) -> bool:
        """
        Metnin tam fonksiyon gibi görünüp görünmediğini döndürür.
        """
        yonetici = self._dogrulama_yoneticisi()
        return (
            yonetici.looks_like_full_function(text) if yonetici is not None else False
        )

    def basic_parse_check(self, text: str) -> None:
        """
        Temel parse kontrolü yapar.
        """
        yonetici = self._dogrulama_yoneticisi()
        return yonetici.basic_parse_check(text) if yonetici is not None else None

    def extract_line_number(self, exc) -> int:
        """
        Exception içinden satır numarası çıkarmaya çalışır.
        """
        yonetici = self._dogrulama_yoneticisi()
        return yonetici.extract_line_number(exc) if yonetici is not None else 0

    def validate_new_code(self, text: str) -> tuple[bool, str, int]:
        """
        Yeni kodu doğrular.

        Returns:
            tuple[bool, str, int]
        """
        yonetici = self._dogrulama_yoneticisi()
        if yonetici is None:
            return False, "Doğrulama yöneticisi yüklenemedi.", 0
        return yonetici.validate_new_code(text)

    # =========================================================
    # BILDIRIM
    # =========================================================
    def bildirim_sinifi(self):
        """
        EditorAksiyonBildirimi sınıfını döndürür.
        """
        yonetici = self._bildirim_yoneticisi()
        return yonetici.bildirim_sinifi() if yonetici is not None else None

    def bildirim_olustur(self, **kwargs):
        """
        Bildirim bileşeni örneği oluşturur.
        """
        yonetici = self._bildirim_yoneticisi()
        return yonetici.bildirim_olustur(**kwargs) if yonetici is not None else None

    # =========================================================
    # BILESENLER
    # =========================================================
    def kod_editoru_sinifi(self):
        """
        KodEditoru sınıfını döndürür.
        """
        yonetici = self._bilesenler_yoneticisi()
        return yonetici.kod_editoru_sinifi() if yonetici is not None else None

    def kod_paneli_sinifi(self):
        """
        KodPaneli sınıfını döndürür.
        """
        yonetici = self._bilesenler_yoneticisi()
        return yonetici.kod_paneli_sinifi() if yonetici is not None else None

    def bilgi_kutusu_sinifi(self):
        """
        BilgiKutusu sınıfını döndürür.
        """
        yonetici = self._bilesenler_yoneticisi()
        return yonetici.bilgi_kutusu_sinifi() if yonetici is not None else None

    def sade_kod_alani_sinifi(self):
        """
        SadeKodAlani sınıfını döndürür.
        """
        yonetici = self._bilesenler_yoneticisi()
        return yonetici.sade_kod_alani_sinifi() if yonetici is not None else None

    def aksiyon_ikon_butonu_sinifi(self):
        """
        Aksiyon ikon butonu sınıfını döndürür.
        """
        yonetici = self._bilesenler_yoneticisi()
        return (
            yonetici.aksiyon_ikon_butonu_sinifi()
            if yonetici is not None
            else None
        )

    def aksiyon_cubugu_sinifi(self):
        """
        Aksiyon çubuğu sınıfını döndürür.
        """
        yonetici = self._bilesenler_yoneticisi()
        return yonetici.aksiyon_cubugu_sinifi() if yonetici is not None else None

    def sade_kod_alani_olustur(self, **kwargs):
        """
        Sade kod alanı örneği oluşturur.
        """
        yonetici = self._bilesenler_yoneticisi()
        return (
            yonetici.sade_kod_alani_olustur(**kwargs)
            if yonetici is not None
            else None
        )

    def bilgi_kutusu_olustur(self, **kwargs):
        """
        Bilgi kutusu örneği oluşturur.
        """
        yonetici = self._bilesenler_yoneticisi()
        return (
            yonetici.bilgi_kutusu_olustur(**kwargs)
            if yonetici is not None
            else None
        )

    def aksiyon_cubugu_olustur(self, **kwargs):
        """
        Aksiyon çubuğu örneği oluşturur.
        """
        yonetici = self._bilesenler_yoneticisi()
        return (
            yonetici.aksiyon_cubugu_olustur(**kwargs)
            if yonetici is not None
            else None
        )

    # =========================================================
    # YARDIMCI
    # =========================================================
    def toast(self, text: str, icon_name: str = "", duration: float = 2.2) -> None:
        """
        Sistem toast bildirimi gösterir.
        """
        yonetici = self._yardimci_yoneticisi()
        if yonetici is None:
            return None
        return yonetici.toast(
            text=text,
            icon_name=icon_name,
            duration=duration,
        )

    def close_popups(self, panel) -> None:
        """
        Editör paneline ait popup'ları kapatır.
        """
        yonetici = self._yardimci_yoneticisi()
        return yonetici.close_popups(panel) if yonetici is not None else None

    def current_item_display(self, panel) -> str:
        """
        Seçili item için kullanıcıya gösterilecek metni döndürür.
        """
        yonetici = self._yardimci_yoneticisi()
        return yonetici.current_item_display(panel) if yonetici is not None else "-"

    def show_inline_notice(
        self,
        panel,
        title: str,
        text: str,
        icon_name: str = "onaylandi.png",
        tone: str = "success",
        duration: float = 4.0,
        on_tap=None,
        title_key: str = "",
        title_default: str = "",
        text_key: str = "",
        text_default: str = "",
    ) -> None:
        """
        Editör paneli içinde inline notice gösterir.
        Dil anahtarları desteklenir.
        """
        yonetici = self._yardimci_yoneticisi()
        if yonetici is None:
            return None

        return yonetici.show_inline_notice(
            panel=panel,
            title=title,
            text=text,
            icon_name=icon_name,
            tone=tone,
            duration=duration,
            on_tap=on_tap,
            title_key=title_key,
            title_default=title_default,
            text_key=text_key,
            text_default=text_default,
        )

    def set_status_info(self, panel, message: str = "", line_no: int = 0):
        """
        Bilgi durumunu uygular.
        """
        yonetici = self._yardimci_yoneticisi()
        return (
            yonetici.set_status_info(panel, message, line_no)
            if yonetici is not None
            else None
        )

    def set_status_warning(self, panel, message: str = "", line_no: int = 0):
        """
        Uyarı durumunu uygular.
        """
        yonetici = self._yardimci_yoneticisi()
        return (
            yonetici.set_status_warning(panel, message, line_no)
            if yonetici is not None
            else None
        )

    def set_status_error(self, panel, message: str = "", line_no: int = 0):
        """
        Hata durumunu uygular.
        """
        yonetici = self._yardimci_yoneticisi()
        return (
            yonetici.set_status_error(panel, message, line_no)
            if yonetici is not None
            else None
        )

    def set_status_success(self, panel, message: str = "", line_no: int = 0):
        """
        Başarı durumunu uygular.
        """
        yonetici = self._yardimci_yoneticisi()
        return (
            yonetici.set_status_success(panel, message, line_no)
            if yonetici is not None
            else None
        )

    def set_popup_error(
        self,
        label,
        editor_area,
        message: str = "",
        line_no: int = 0,
    ):
        """
        Popup içi hata metni ve hata satırını uygular.
        """
        yonetici = self._yardimci_yoneticisi()
        return (
            yonetici.set_popup_error(label, editor_area, message, line_no)
            if yonetici is not None
            else None
    )

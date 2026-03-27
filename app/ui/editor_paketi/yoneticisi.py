# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/editor_paketi/yoneticisi.py

ROL:
- Editor paketine tek giriş noktası sağlar
- Alt paket yöneticilerini merkezileştirir
- Üst katmanın editor paketi iç yapısını bilmesini engeller
- Panel, root, aksiyon, popup, doğrulama, bildirim, bileşen ve yardımcı akışları tek yerden sunar
- Editör popup ve panel akışlarında seçili dil destekli metinlerin aşağı katmanda korunmasına aracılık eder

MİMARİ:
- Üst katman sadece bu yöneticiyi bilir
- Alt paketlere doğrudan erişim yerine ilgili yönetici sınıfları kullanılır
- Lazy import + yönetici katmanı korunur
- Paket dışına iç modül detayları sızdırılmaz
- Tekrarlayan yönetici oluşturma maliyetini azaltmak için instance cache kullanılır
- Fail-soft yaklaşım uygulanır

SURUM: 6
TARIH: 2026-03-27
IMZA: FY.
"""

from __future__ import annotations


class EditorYoneticisi:
    """
    Editor paketi için merkezi üst yönetici.
    """

    YONETICI_HARITASI = {
        "panel": ("app.ui.editor_paketi.panel", "PanelYoneticisi"),
        "root": ("app.ui.editor_paketi.root", "RootYoneticisi"),
        "aksiyon": ("app.ui.editor_paketi.aksiyon", "AksiyonYoneticisi"),
        "popup": ("app.ui.editor_paketi.popup", "PopupYoneticisi"),
        "dogrulama": ("app.ui.editor_paketi.dogrulama", "DogrulamaYoneticisi"),
        "bildirim": ("app.ui.editor_paketi.bildirim", "BildirimYoneticisi"),
        "bilesenler": ("app.ui.editor_paketi.bilesenler", "BilesenlerYoneticisi"),
        "yardimci": ("app.ui.editor_paketi.yardimci", "YardimciYoneticisi"),
    }

    def __init__(self) -> None:
        self._yonetici_cache: dict[str, object] = {}

    # =========================================================
    # CACHE
    # =========================================================
    def cache_temizle(self) -> None:
        """
        Tüm alt yönetici cache'lerini temizler.
        """
        self._yonetici_cache = {}

    # =========================================================
    # INTERNAL
    # =========================================================
    def _yonetici_al(self, ad: str):
        """
        Verilen ad için alt yöneticiyi lazy import ile yükler.

        Args:
            ad: Yönetici kısa adı

        Returns:
            object | None
        """
        if ad in self._yonetici_cache:
            return self._yonetici_cache.get(ad)

        bilgi = self.YONETICI_HARITASI.get(ad)
        if not bilgi:
            print(f"[EDITOR_YONETICISI] Yönetici haritasında bulunamadı: {ad}")
            return None

        modul_yolu, sinif_adi = bilgi

        try:
            modul = __import__(modul_yolu, fromlist=[sinif_adi])
            sinif = getattr(modul, sinif_adi, None)
        except Exception as exc:
            print(f"[EDITOR_YONETICISI] Yönetici yüklenemedi: {modul_yolu}.{sinif_adi}")
            print(exc)
            self._yonetici_cache.pop(ad, None)
            return None

        if sinif is None:
            print(f"[EDITOR_YONETICISI] Yönetici sınıfı bulunamadı: {modul_yolu}.{sinif_adi}")
            self._yonetici_cache.pop(ad, None)
            return None

        try:
            ornek = sinif()
        except Exception as exc:
            print(f"[EDITOR_YONETICISI] Yönetici örneği oluşturulamadı: {modul_yolu}.{sinif_adi}")
            print(exc)
            self._yonetici_cache.pop(ad, None)
            return None

        self._yonetici_cache[ad] = ornek
        return ornek

    def _yonetici_cagir(self, yonetici_adi: str, metod_adi: str, *args, **kwargs):
        """
        Alt yönetici üstündeki metodu güvenli biçimde çağırır.

        Args:
            yonetici_adi: Alt yönetici kısa adı
            metod_adi: Çağrılacak metod adı

        Returns:
            Any | None
        """
        yonetici = self._yonetici_al(yonetici_adi)
        if yonetici is None:
            return None

        try:
            metod = getattr(yonetici, metod_adi, None)
            if callable(metod):
                return metod(*args, **kwargs)
        except Exception as exc:
            print(
                f"[EDITOR_YONETICISI] Çağrı başarısız: "
                f"{yonetici_adi}.{metod_adi}"
            )
            print(exc)
            return None

        print(
            f"[EDITOR_YONETICISI] Metod bulunamadı: "
            f"{yonetici_adi}.{metod_adi}"
        )
        return None

    # =========================================================
    # PANEL
    # =========================================================
    def panel_sinifi(self):
        return self._yonetici_cagir("panel", "panel_sinifi")

    def panel_olustur(self, **kwargs):
        return self._yonetici_cagir("panel", "panel_olustur", **kwargs)

    # =========================================================
    # ROOT
    # =========================================================
    def root_sinifi(self):
        return self._yonetici_cagir("root", "root_sinifi")

    def root_olustur(self, **kwargs):
        return self._yonetici_cagir("root", "root_olustur", **kwargs)

    # =========================================================
    # AKSIYON
    # =========================================================
    def copy_current_to_new(self, panel, *_args):
        return self._yonetici_cagir("aksiyon", "copy_current_to_new", panel, *_args)

    def paste_new_code(self, panel, *_args):
        return self._yonetici_cagir("aksiyon", "paste_new_code", panel, *_args)

    def clear_new_code(self, panel, *_args):
        return self._yonetici_cagir("aksiyon", "clear_new_code", panel, *_args)

    def check_new_code(self, panel, *_args):
        return self._yonetici_cagir("aksiyon", "check_new_code", panel, *_args)

    def handle_update(self, panel, *_args):
        return self._yonetici_cagir("aksiyon", "handle_update", panel, *_args)

    def handle_restore(self, panel, *_args):
        return self._yonetici_cagir("aksiyon", "handle_restore", panel, *_args)

    # =========================================================
    # POPUP
    # =========================================================
    def build_popup_toolbar(self, actions):
        return self._yonetici_cagir("popup", "build_popup_toolbar", actions)

    def open_current_code_popup(self, panel, *_args):
        return self._yonetici_cagir("popup", "open_current_code_popup", panel, *_args)

    def open_new_code_editor_popup(self, panel, *_args):
        return self._yonetici_cagir(
            "popup",
            "open_new_code_editor_popup",
            panel,
            *_args,
        )

    # =========================================================
    # DOGRULAMA
    # =========================================================
    def normalize_code_text(self, text, trim_outer_blank_lines: bool = False) -> str:
        sonuc = self._yonetici_cagir(
            "dogrulama",
            "normalize_code_text",
            text,
            trim_outer_blank_lines=trim_outer_blank_lines,
        )
        try:
            return str(sonuc if sonuc is not None else text or "")
        except Exception:
            return ""

    def first_meaningful_line(self, text: str) -> str:
        sonuc = self._yonetici_cagir("dogrulama", "first_meaningful_line", text)
        return str(sonuc or "")

    def looks_like_full_function(self, text: str) -> bool:
        sonuc = self._yonetici_cagir("dogrulama", "looks_like_full_function", text)
        return bool(sonuc)

    def basic_parse_check(self, text: str):
        return self._yonetici_cagir("dogrulama", "basic_parse_check", text)

    def extract_line_number(self, exc) -> int:
        sonuc = self._yonetici_cagir("dogrulama", "extract_line_number", exc)
        try:
            return int(sonuc or 0)
        except Exception:
            return 0

    def validate_new_code(self, text: str) -> tuple[bool, str, int]:
        sonuc = self._yonetici_cagir("dogrulama", "validate_new_code", text)
        if isinstance(sonuc, tuple) and len(sonuc) == 3:
            return sonuc
        return False, "Doğrulama yöneticisi yüklenemedi.", 0

    # =========================================================
    # BILDIRIM
    # =========================================================
    def bildirim_sinifi(self):
        return self._yonetici_cagir("bildirim", "bildirim_sinifi")

    def bildirim_olustur(self, **kwargs):
        return self._yonetici_cagir("bildirim", "bildirim_olustur", **kwargs)

    # =========================================================
    # BILESENLER
    # =========================================================
    def kod_editoru_sinifi(self):
        return self._yonetici_cagir("bilesenler", "kod_editoru_sinifi")

    def kod_paneli_sinifi(self):
        return self._yonetici_cagir("bilesenler", "kod_paneli_sinifi")

    def bilgi_kutusu_sinifi(self):
        return self._yonetici_cagir("bilesenler", "bilgi_kutusu_sinifi")

    def sade_kod_alani_sinifi(self):
        return self._yonetici_cagir("bilesenler", "sade_kod_alani_sinifi")

    def aksiyon_ikon_butonu_sinifi(self):
        return self._yonetici_cagir("bilesenler", "aksiyon_ikon_butonu_sinifi")

    def aksiyon_cubugu_sinifi(self):
        return self._yonetici_cagir("bilesenler", "aksiyon_cubugu_sinifi")

    def sade_kod_alani_olustur(self, **kwargs):
        return self._yonetici_cagir("bilesenler", "sade_kod_alani_olustur", **kwargs)

    def bilgi_kutusu_olustur(self, **kwargs):
        return self._yonetici_cagir("bilesenler", "bilgi_kutusu_olustur", **kwargs)

    def aksiyon_cubugu_olustur(self, **kwargs):
        return self._yonetici_cagir("bilesenler", "aksiyon_cubugu_olustur", **kwargs)

    # =========================================================
    # YARDIMCI
    # =========================================================
    def toast(
        self,
        text: str,
        icon_name: str = "",
        duration: float = 2.2,
        panel=None,
    ) -> None:
        return self._yonetici_cagir(
            "yardimci",
            "toast",
            text=text,
            icon_name=icon_name,
            duration=duration,
            panel=panel,
        )

    def close_popups(self, panel) -> None:
        return self._yonetici_cagir("yardimci", "close_popups", panel)

    def current_item_display(self, panel) -> str:
        sonuc = self._yonetici_cagir("yardimci", "current_item_display", panel)
        return str(sonuc or "-")

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
        return self._yonetici_cagir(
            "yardimci",
            "show_inline_notice",
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
        return self._yonetici_cagir(
            "yardimci",
            "set_status_info",
            panel,
            message,
            line_no,
        )

    def set_status_warning(self, panel, message: str = "", line_no: int = 0):
        return self._yonetici_cagir(
            "yardimci",
            "set_status_warning",
            panel,
            message,
            line_no,
        )

    def set_status_error(self, panel, message: str = "", line_no: int = 0):
        return self._yonetici_cagir(
            "yardimci",
            "set_status_error",
            panel,
            message,
            line_no,
        )

    def set_status_success(self, panel, message: str = "", line_no: int = 0):
        return self._yonetici_cagir(
            "yardimci",
            "set_status_success",
            panel,
            message,
            line_no,
        )

    def set_popup_error(
        self,
        label,
        editor_area,
        message: str = "",
        line_no: int = 0,
        panel=None,
    ):
        return self._yonetici_cagir(
            "yardimci",
            "set_popup_error",
            label,
            editor_area,
            message,
            line_no,
            panel=panel,
        )

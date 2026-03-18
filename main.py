# -*- coding: utf-8 -*-
"""
DOSYA: main.py
MODUL: main

ROL:
- Uygulamanın giriş noktası
- Kivy App sınıfını başlatır
- RootWidget oluşturur
- Uygulama başlığında sürüm bilgisini gösterir
- Proje kökünü sys.path içine ekler
- APK içinde ve normal çalıştırmada importları sade ve güvenli tutar
- Hata olursa traceback'i ekranda göstermeye çalışır
- Geliştirme modunda Test Dosya Seç butonu ekler
- Test dosya seçildiğinde gerçek UI akışını tetikler

DAVRANIŞ:
- app/config.py içindeki DEV_MODE aktifse "Test Dosya Seç" butonu görünür
- DEV_MODE kapalıysa buton hiç görünmez
- Test dosyası seçilince gerçek dosya seçme/tarama akışı tetiklenir
- APK için normal akış bozulmaz

SURUM: 10
TARIH: 2026-03-18
IMZA: FY.
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


# =========================================================
# PATH
# =========================================================
def _safe_resolve(path: Path) -> Path:
    try:
        return path.resolve()
    except Exception:
        try:
            return path.absolute()
        except Exception:
            return path


def _proje_koku_bul() -> Path:
    """
    main.py dosyasının bulunduğu klasörü proje kökü kabul eder.
    """
    try:
        return _safe_resolve(Path(__file__).parent)
    except Exception:
        try:
            return _safe_resolve(Path.cwd())
        except Exception:
            return Path(".")


PROJE_ROOT = _proje_koku_bul()

if str(PROJE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJE_ROOT))


# =========================================================
# ERROR UI
# =========================================================
def _build_error_root(hata_metni: str) -> BoxLayout:
    root = BoxLayout(
        orientation="vertical",
        padding=dp(18),
        spacing=dp(12),
    )

    baslik = Label(
        text="Fonksiyon Degistirici",
        size_hint_y=None,
        height=dp(42),
        font_size="20sp",
        bold=True,
        color=(1, 1, 1, 1),
        halign="center",
        valign="middle",
        shorten=True,
        shorten_from="right",
        max_lines=1,
    )
    baslik.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    root.add_widget(baslik)

    mesaj = Label(
        text="Uygulama açılırken hata oluştu.\n\n" + str(hata_metni or ""),
        color=(1, 0.82, 0.82, 1),
        halign="left",
        valign="top",
    )
    mesaj.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))
    root.add_widget(mesaj)

    return root


# =========================================================
# DEV MODE
# =========================================================
def _dev_mode_aktif_mi() -> bool:
    try:
        from app.config import DEV_MODE
    except Exception:
        return False

    if isinstance(DEV_MODE, bool):
        return DEV_MODE

    deger = str(DEV_MODE or "").strip().lower()
    return deger in ("1", "true", "evet", "on", "aktif")


# =========================================================
# DEV TEST FLOW
# =========================================================
def _handle_dev_test_file_selected(root_widget, path: str) -> None:
    """
    Test popup ile seçilen dosyayı gerçek RootWidget akışına bağlar.
    """
    try:
        from app.ui.dosya_secici_paketi.models import DocumentSelection

        secim_yolu = str(path or "").strip()
        if not secim_yolu:
            try:
                root_widget.set_status_warning("Test dosya yolu boş geldi.")
            except Exception:
                pass
            return

        secim = DocumentSelection(
            source="filesystem",
            uri="",
            local_path=secim_yolu,
            display_name=Path(secim_yolu).name,
            mime_type="text/x-python",
        )

        try:
            if getattr(root_widget, "dosya_secici", None) is not None:
                root_widget.dosya_secici.set_selection(secim)
        except Exception:
            pass

        try:
            root_widget.scan_file(secim_yolu)
        except Exception as exc:
            try:
                root_widget.set_status_error(f"Test dosya tarama hatası: {exc}")
            except Exception:
                pass

    except Exception:
        try:
            print(traceback.format_exc())
        except Exception:
            pass


def _ekle_dev_test_butonu(root_widget) -> None:
    """
    DEV_MODE açıksa, tıklanabilir test dosya seç butonunu
    ana root yerleşimine ekler.
    """
    if not _dev_mode_aktif_mi():
        return

    try:
        from kivy.uix.button import Button
        from app.ui.test_dosya_secici import TestDosyaSeciciPopup

        btn = Button(
            text="Test Dosya Seç",
            size_hint_y=None,
            height=dp(52),
            background_normal="",
            background_down="",
            background_color=(0.16, 0.24, 0.36, 1),
            color=(1, 1, 1, 1),
            bold=True,
        )

        def _ac_popup(*_args):
            try:
                popup = TestDosyaSeciciPopup(
                    on_select=lambda p: _handle_dev_test_file_selected(root_widget, p)
                )
                popup.open()
            except Exception as exc:
                try:
                    root_widget.set_status_error(f"Test picker açılamadı: {exc}")
                except Exception:
                    pass

        btn.bind(on_release=_ac_popup)

        # Scroll içindeki alanlara değil, ana root'a ekliyoruz ki dokunma düzgün çalışsın.
        if getattr(root_widget, "main_root", None) is not None:
            root_widget.main_root.add_widget(btn, index=0)
        else:
            root_widget.add_widget(btn)

    except Exception:
        try:
            print(traceback.format_exc())
        except Exception:
            pass


# =========================================================
# APP
# =========================================================
class FonksiyonDegistiriciApp(App):
    """
    Ana Kivy uygulaması.
    """

    def build(self):
        try:
            try:
                from kivy.core.window import Window

                Window.softinput_mode = "below_target"
            except Exception:
                pass

            from app.core.uygulama_meta import UYGULAMA_ADI, tam_surum
            from app.ui.root import RootWidget

            self.title = f"{UYGULAMA_ADI} v{tam_surum()}"

            root = RootWidget()
            _ekle_dev_test_butonu(root)
            return root

        except Exception:
            hata = traceback.format_exc()
            try:
                print(hata)
            except Exception:
                pass
            return _build_error_root(hata)

    def on_start(self):
        try:
            print(f"PROJE_ROOT = {PROJE_ROOT}")
            print(f"DEV_MODE = {_dev_mode_aktif_mi()}")
        except Exception:
            pass


# =========================================================
# RUN
# =========================================================
def main() -> None:
    try:
        FonksiyonDegistiriciApp().run()
    except Exception:
        try:
            print(traceback.format_exc())
        except Exception:
            pass


if __name__ == "__main__":
    main()

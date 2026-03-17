# -*- coding: utf-8 -*-
"""
DOSYA: app/services/reklam_servisi.py

ROL:
- AdMob reklamlarının yüklenmesini ve yönetilmesini sağlar
- Android bridge üzerinden AdMob SDK çağrısı yapar
- Reklam debug adımlarını toplar
- Sonucu kopyalanabilir popup içinde gösterir

NOT:
- Şu anda TEST reklam kullanılmaktadır.
- Google Play'e yüklemeden önce gerçek reklam birimi ile değiştirilmelidir.
- Bu sürüm manuel test moduna uyumludur.
- Reklam servisi kendi debug popup işini kendi yönetir.
"""

from __future__ import annotations

from jnius import autoclass
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.utils import platform

from app.services.gecici_bildirim_servisi import gecici_bildirim_servisi


class ReklamServisi:
    TEST_BANNER_ID = "ca-app-pub-3940256099942544/6300978111"
    REAL_BANNER_ID = "ca-app-pub-5522917995813710/2607730157"

    def __init__(self) -> None:
        self._initialized = False
        self._banner_yuklendi = False
        self._son_kullanilan_id = self.TEST_BANNER_ID

        self._debug_lines: list[str] = []
        self._debug_popup = None
        self._debug_text_input = None

    # =========================================================
    # DEBUG
    # =========================================================
    def _debug_reset(self) -> None:
        self._debug_lines = []

    def _debug_add(self, message: str) -> None:
        satir = str(message or "").strip()
        if not satir:
            return
        self._debug_lines.append(satir)
        print(f"[REKLAM] {satir}")
        try:
            if self._debug_text_input is not None:
                self._debug_text_input.text = "\n".join(self._debug_lines)
        except Exception:
            pass

    def _debug_text(self) -> str:
        return "\n".join(self._debug_lines)

    def _debug_copy(self, _instance=None) -> None:
        try:
            Clipboard.copy(self._debug_text())
            gecici_bildirim_servisi.show(
                text="Reklam debug metni kopyalandı.",
                icon_name="onaylandi.png",
                duration=2.0,
            )
        except Exception as exc:
            gecici_bildirim_servisi.show(
                text=f"Kopyalama hatası: {exc}",
                icon_name="warning.png",
                duration=3.0,
            )

    def _debug_close_popup(self, _instance=None) -> None:
        try:
            if self._debug_popup is not None:
                self._debug_popup.dismiss()
        except Exception:
            pass

    def debug_popup_goster(self, title: str = "Reklam Debug") -> None:
        try:
            content = BoxLayout(
                orientation="vertical",
                spacing=dp(8),
                padding=dp(8),
            )

            self._debug_text_input = TextInput(
                text=self._debug_text(),
                multiline=True,
                readonly=False,
                size_hint=(1, 1),
                background_normal="",
                background_active="",
                background_color=(0.08, 0.08, 0.10, 1),
                foreground_color=(1, 1, 1, 1),
                cursor_color=(1, 1, 1, 1),
                font_size="13sp",
            )
            content.add_widget(self._debug_text_input)

            btn_bar = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(48),
                spacing=dp(8),
            )

            copy_btn = Button(
                text="Kopyala",
                background_normal="",
                background_down="",
                background_color=(0.16, 0.62, 0.34, 1),
                color=(1, 1, 1, 1),
            )
            copy_btn.bind(on_release=self._debug_copy)
            btn_bar.add_widget(copy_btn)

            close_btn = Button(
                text="Kapat",
                background_normal="",
                background_down="",
                background_color=(0.74, 0.20, 0.20, 1),
                color=(1, 1, 1, 1),
            )
            close_btn.bind(on_release=self._debug_close_popup)
            btn_bar.add_widget(close_btn)

            content.add_widget(btn_bar)

            self._debug_popup = Popup(
                title=title,
                content=content,
                size_hint=(0.95, 0.80),
                auto_dismiss=True,
            )
            self._debug_popup.open()

        except Exception as exc:
            gecici_bildirim_servisi.show(
                text=f"Popup açma hatası: {exc}",
                icon_name="warning.png",
                duration=3.0,
            )

    # =========================================================
    # INTERNAL
    # =========================================================
    def _android_bridge(self):
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = PythonActivity.mActivity
        AdMobBridge = autoclass("org.fy.bridge.AdMobBridge")
        return activity, AdMobBridge

    # =========================================================
    # REKLAM YÜKLE
    # =========================================================
    def reklam_yukle(self, use_real_ad: bool = False) -> None:
        if platform != "android":
            self._debug_add("HATA: Android dışında reklam yükleme atlandı.")
            return

        activity, AdMobBridge = self._android_bridge()

        if not self._initialized:
            AdMobBridge.initialize(activity)
            self._initialized = True
            self._debug_add("Adım 5: initialize tamamlandı.")
        else:
            self._debug_add("Adım 5: initialize zaten yapılmış.")

        ad_unit_id = self.REAL_BANNER_ID if use_real_ad else self.TEST_BANNER_ID
        self._son_kullanilan_id = ad_unit_id
        self._debug_add(f"Adım 6: Reklam ID seçildi -> {ad_unit_id}")

        AdMobBridge.loadBanner(activity, ad_unit_id)
        self._banner_yuklendi = True
        self._debug_add("Adım 7: loadBanner çağrısı tamamlandı.")

    # =========================================================
    # REKLAM GÖSTER
    # =========================================================
    def reklam_goster(self) -> None:
        if platform != "android":
            self._debug_add("HATA: Android dışında reklam gösterme atlandı.")
            return

        if not self._banner_yuklendi:
            self._debug_add("HATA: Banner henüz yüklenmedi.")
            return

        activity, AdMobBridge = self._android_bridge()
        self._debug_add("Adım 8: Bridge ve activity tekrar alındı.")

        AdMobBridge.showBanner(activity)
        self._debug_add("Adım 9: showBanner çağrısı tamamlandı.")

    # =========================================================
    # TEK PARÇA TEST AKIŞI
    # =========================================================
    def reklam_test_et(self, use_real_ad: bool = False) -> None:
        self._debug_reset()

        try:
            if platform != "android":
                self._debug_add("HATA: Android platform değil.")
                self.debug_popup_goster("Reklam Test Hatası")
                return

            self._debug_add("Adım 1: Android platform doğrulandı.")

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            self._debug_add("Adım 2: PythonActivity bulundu.")

            activity = PythonActivity.mActivity
            self._debug_add("Adım 3: mActivity alındı.")

            AdMobBridge = autoclass("org.fy.bridge.AdMobBridge")
            self._debug_add("Adım 4: AdMobBridge bulundu.")

            self.reklam_yukle(use_real_ad=use_real_ad)
            self._debug_add("Adım 7b: reklam_yukle metodu tamamlandı.")

            def _delayed_show(_dt):
                try:
                    self._debug_add("Adım 8b: gecikmeli show başlıyor.")
                    self.reklam_goster()
                    self._debug_add("Adım 10: reklam_goster metodu tamamlandı.")

                    gecici_bildirim_servisi.show(
                        text="Reklam test akışı tamamlandı.",
                        icon_name="onaylandi.png",
                        duration=2.0,
                    )
                except Exception as exc:
                    hata = f"{type(exc).__name__}: {exc}"
                    self._debug_add(f"HATA(show): {hata}")
                    gecici_bildirim_servisi.show(
                        text=f"Reklam gösterme hatası: {exc}",
                        icon_name="warning.png",
                        duration=3.0,
                    )
                finally:
                    self.debug_popup_goster("Reklam Test Sonucu")

            Clock.schedule_once(_delayed_show, 1.0)

        except Exception as exc:
            self._banner_yuklendi = False
            hata = f"{type(exc).__name__}: {exc}"
            self._debug_add(f"HATA: {hata}")
            gecici_bildirim_servisi.show(
                text=f"Reklam yükleme hatası: {exc}",
                icon_name="warning.png",
                duration=3.0,
            )
            self.debug_popup_goster("Reklam Test Hatası")

    # =========================================================
    # REKLAM KAPAT
    # =========================================================
    def reklam_kapat(self) -> None:
        if platform != "android":
            return

        try:
            activity, AdMobBridge = self._android_bridge()
            AdMobBridge.hideBanner(activity)
            gecici_bildirim_servisi.show(
                text="Reklam gizleme komutu gönderildi.",
                icon_name="warning.png",
                duration=2.5,
            )
        except Exception as exc:
            gecici_bildirim_servisi.show(
                text=f"Reklam gizleme hatası: {exc}",
                icon_name="warning.png",
                duration=3.0,
            )

    # =========================================================
    # REKLAM YOK ET
    # =========================================================
    def reklam_yok_et(self) -> None:
        if platform != "android":
            return

        try:
            activity, AdMobBridge = self._android_bridge()
            AdMobBridge.destroyBanner(activity)
            self._banner_yuklendi = False
            gecici_bildirim_servisi.show(
                text="Reklam tamamen kaldırıldı.",
                icon_name="warning.png",
                duration=2.5,
            )
        except Exception as exc:
            gecici_bildirim_servisi.show(
                text=f"Reklam yok etme hatası: {exc}",
                icon_name="warning.png",
                duration=3.0,
            )

    # =========================================================
    # DURUM
    # =========================================================
    def reklam_hazir_mi(self) -> bool:
        return bool(self._banner_yuklendi)

    def test_modu_mu(self) -> bool:
        return self._son_kullanilan_id == self.TEST_BANNER_ID


reklam_servisi = ReklamServisi()

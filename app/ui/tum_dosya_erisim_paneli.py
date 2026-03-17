# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paneli.py

ROL:
- Android'de tüm dosya erişimi durumunu kullanıcıya göstermek
- Gerekirse kullanıcıyı ilgili ayar ekranına yönlendirmek
- Açık / kapalı durumu premium kart görünümünde göstermek
- Kapalı durumda sürekli pulse ile dikkat çekmek
- Açık durumda kısa süre pulse gösterip sonra sakinleştirmek

API 34 UYUMLULUK NOTU:
- Ayar ekranından geri dönüldüğünde izin durumu otomatik yeniden kontrol edilir
- İzin durumu okunamazsa kontrollü hata görünümü uygulanır
- Görünüm korunmuş, sadece davranış güvenli hale getirilmiştir

SURUM: 7
TARIH: 2026-03-17
IMZA: FY.
"""

from __future__ import annotations

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.utils import platform

from app.ui.iconlu_baslik import IconluBaslik
from app.ui.kart import Kart
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY


class TiklanabilirIcon(ButtonBehavior, Image):
    pass


class TumDosyaErisimPaneli(Kart):
    def __init__(self, on_status_changed=None, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(138),
            spacing=dp(8),
            padding=(dp(12), dp(10), dp(12), dp(10)),
            bg=(0.08, 0.11, 0.16, 1),
            border=(0.18, 0.21, 0.27, 1),
            radius=16,
            **kwargs,
        )

        self.on_status_changed = on_status_changed

        self.status_icon = None
        self.info_label = None
        self.detail_label = None
        self.action_open_icon = None
        self.action_close_icon = None

        self._pulse_anim = None
        self._stop_pulse_event = None
        self._last_status = None
        self._action_icon_visible_width = dp(70)

        self._settings_watch_event = None
        self._settings_watch_remaining = 0
        self._watch_seconds_default = 12

        self._build_ui()
        self.refresh_status()

    def _debug(self, message: str) -> None:
        try:
            print("[TUM_DOSYA_ERISIM]", str(message))
        except Exception:
            pass

    # =========================================================
    # UI
    # =========================================================
    def _build_ui(self) -> None:
        ust = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(64),
            spacing=dp(10),
        )

        self.status_icon = TiklanabilirIcon(
            source="app/assets/icons/erisim_kapali.png",
            size_hint=(None, None),
            size=(dp(50), dp(50)),
            allow_stretch=True,
            keep_ratio=True,
            opacity=1,
        )
        self.status_icon.bind(on_release=self._handle_status_icon_click)
        ust.add_widget(self.status_icon)

        metinler = BoxLayout(
            orientation="vertical",
            spacing=dp(2),
        )

        baslik = IconluBaslik(
            text="Tüm Dosya Erişimi",
            icon_name="folder_open.png",
            height_dp=24,
            font_size="14sp",
            color=TEXT_PRIMARY,
        )
        baslik.size_hint_y = None
        baslik.height = dp(24)
        metinler.add_widget(baslik)

        self.info_label = Label(
            text="Durum kontrol ediliyor...",
            color=TEXT_PRIMARY,
            font_size="14sp",
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(22),
            bold=True,
        )
        self.info_label.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))
        metinler.add_widget(self.info_label)

        self.detail_label = Label(
            text="Bu izin dosya tarama akışı için önerilir.",
            color=TEXT_MUTED,
            font_size="11sp",
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(18),
        )
        self.detail_label.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))
        metinler.add_widget(self.detail_label)

        ust.add_widget(metinler)
        self.add_widget(ust)

        alt = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(32),
            spacing=dp(10),
        )

        alt.add_widget(Label(size_hint_x=1))

        self._action_open_wrap = BoxLayout(
            orientation="horizontal",
            size_hint=(None, None),
            size=(self._action_icon_visible_width, dp(30)),
        )
        self.action_open_icon = TiklanabilirIcon(
            source="app/assets/icons/erisimi_ac_aksiyon.png",
            size_hint=(None, None),
            size=(dp(28), dp(28)),
            allow_stretch=True,
            keep_ratio=True,
        )
        self.action_open_icon.bind(on_release=self._handle_open_action)
        self._action_open_wrap.add_widget(Label(size_hint_x=1))
        self._action_open_wrap.add_widget(self.action_open_icon)
        self._action_open_wrap.add_widget(Label(size_hint_x=1))

        self._action_close_wrap = BoxLayout(
            orientation="horizontal",
            size_hint=(None, None),
            size=(self._action_icon_visible_width, dp(30)),
        )
        self.action_close_icon = TiklanabilirIcon(
            source="app/assets/icons/erisimi_kapat_aksiyon.png",
            size_hint=(None, None),
            size=(dp(28), dp(28)),
            allow_stretch=True,
            keep_ratio=True,
        )
        self.action_close_icon.bind(on_release=self._handle_close_action)
        self._action_close_wrap.add_widget(Label(size_hint_x=1))
        self._action_close_wrap.add_widget(self.action_close_icon)
        self._action_close_wrap.add_widget(Label(size_hint_x=1))

        alt.add_widget(self._action_open_wrap)
        alt.add_widget(self._action_close_wrap)
        self.add_widget(alt)

    # =========================================================
    # WATCH / SETTINGS DÖNÜŞ TAKİBİ
    # =========================================================
    def _stop_settings_watch(self) -> None:
        try:
            if self._settings_watch_event is not None:
                self._settings_watch_event.cancel()
        except Exception:
            pass
        self._settings_watch_event = None
        self._settings_watch_remaining = 0

    def _start_settings_watch(self, seconds: int | float | None = None) -> None:
        self._stop_settings_watch()

        try:
            toplam = int(seconds if seconds is not None else self._watch_seconds_default)
        except Exception:
            toplam = self._watch_seconds_default

        self._settings_watch_remaining = max(3, toplam)

        def _poll(_dt):
            try:
                onceki = self._last_status
                self.refresh_status()

                self._settings_watch_remaining -= 1

                if self._last_status != onceki:
                    self._debug("Ayar dönüşünde izin durumu değişti, izleme durduruldu.")
                    self._stop_settings_watch()
                    return

                if self._settings_watch_remaining <= 0:
                    self._debug("Ayar dönüşü izleme süresi doldu.")
                    self._stop_settings_watch()
                    return
            except Exception as exc:
                self._debug(f"Ayar dönüşü izleme hatası: {exc}")
                self._stop_settings_watch()

        self._settings_watch_event = Clock.schedule_interval(_poll, 1.0)

    # =========================================================
    # ANİMASYON
    # =========================================================
    def _cancel_stop_event(self):
        try:
            if self._stop_pulse_event is not None:
                self._stop_pulse_event.cancel()
        except Exception:
            pass
        self._stop_pulse_event = None

    def _stop_pulse(self):
        self._cancel_stop_event()
        try:
            if self._pulse_anim is not None and self.status_icon is not None:
                self._pulse_anim.cancel(self.status_icon)
        except Exception:
            pass
        self._pulse_anim = None
        try:
            if self.status_icon is not None:
                self.status_icon.opacity = 1
                self.status_icon.size = (dp(50), dp(50))
        except Exception:
            pass

    def _start_pulse_forever(self):
        self._stop_pulse()
        try:
            anim = (
                Animation(opacity=0.72, size=(dp(58), dp(58)), duration=0.55)
                + Animation(opacity=1.00, size=(dp(50), dp(50)), duration=0.55)
            )
            anim.repeat = True
            anim.start(self.status_icon)
            self._pulse_anim = anim
        except Exception:
            pass

    def _start_pulse_for_seconds(self, seconds: float):
        self._stop_pulse()
        try:
            anim = (
                Animation(opacity=0.78, size=(dp(56), dp(56)), duration=0.50)
                + Animation(opacity=1.00, size=(dp(50), dp(50)), duration=0.50)
            )
            anim.repeat = True
            anim.start(self.status_icon)
            self._pulse_anim = anim
            self._stop_pulse_event = Clock.schedule_once(
                lambda *_: self._stop_pulse(),
                max(0.1, float(seconds)),
            )
        except Exception:
            pass

    # =========================================================
    # ACTION GÖRÜNÜRLÜĞÜ
    # =========================================================
    def _set_wrap_visible(self, wrap, visible: bool) -> None:
        if wrap is None:
            return
        try:
            wrap.opacity = 1 if visible else 0
            wrap.width = self._action_icon_visible_width if visible else 0.01
        except Exception:
            pass

    def _show_open_action(self):
        self._set_wrap_visible(self._action_open_wrap, True)
        self._set_wrap_visible(self._action_close_wrap, False)

    def _show_close_action(self):
        self._set_wrap_visible(self._action_open_wrap, False)
        self._set_wrap_visible(self._action_close_wrap, True)

    # =========================================================
    # STATE UYGULAMA
    # =========================================================
    def _apply_closed_state(self):
        try:
            if self.status_icon is not None:
                self.status_icon.source = "app/assets/icons/erisim_kapali.png"
        except Exception:
            pass

        self.set_bg_rgba((0.16, 0.09, 0.10, 1))
        self.set_border_rgba((0.30, 0.14, 0.16, 1))

        self.info_label.text = "Tüm dosya erişimi kapalı"
        self.info_label.color = (1.0, 0.82, 0.82, 1)

        self.detail_label.text = "Öneri: erişimi açıp sonra dosya seç."
        self.detail_label.color = (0.96, 0.72, 0.72, 1)

        self._show_open_action()
        self._start_pulse_forever()

    def _apply_open_state(self):
        try:
            if self.status_icon is not None:
                self.status_icon.source = "app/assets/icons/erisim_acik.png"
        except Exception:
            pass

        self.set_bg_rgba((0.08, 0.18, 0.12, 1))
        self.set_border_rgba((0.14, 0.30, 0.20, 1))

        self.info_label.text = "Tüm dosya erişimi açık"
        self.info_label.color = (0.82, 1.0, 0.86, 1)

        self.detail_label.text = "Belge seçimi ve tarama için hazır."
        self.detail_label.color = (0.72, 0.94, 0.78, 1)

        self._show_close_action()
        self._start_pulse_for_seconds(10.0)

    def _apply_non_android_state(self):
        try:
            if self.status_icon is not None:
                self.status_icon.source = "app/assets/icons/erisim_kapali.png"
        except Exception:
            pass

        self.set_bg_rgba((0.08, 0.11, 0.16, 1))
        self.set_border_rgba((0.18, 0.21, 0.27, 1))

        self.info_label.text = "Android ortamı değil"
        self.info_label.color = TEXT_PRIMARY

        self.detail_label.text = "Bu panel Android üzerinde etkin çalışır."
        self.detail_label.color = TEXT_MUTED

        self._show_open_action()
        self._stop_pulse()

    def _apply_unknown_state(self, detail_text: str):
        try:
            if self.status_icon is not None:
                self.status_icon.source = "app/assets/icons/erisim_kapali.png"
        except Exception:
            pass

        self.set_bg_rgba((0.14, 0.11, 0.08, 1))
        self.set_border_rgba((0.28, 0.22, 0.12, 1))

        self.info_label.text = "İzin durumu doğrulanamadı"
        self.info_label.color = (1.0, 0.92, 0.78, 1)

        detay = str(detail_text or "").strip()
        self.detail_label.text = detay or "Durum tekrar kontrol edilmeli."
        self.detail_label.color = (0.95, 0.82, 0.62, 1)

        self._show_open_action()
        self._stop_pulse()

    # =========================================================
    # İZİN AKIŞI
    # =========================================================
    def _open_settings(self) -> None:
        if platform != "android":
            self._apply_non_android_state()
            return

        try:
            from app.services.android_ozel_izin_servisi import tum_dosya_erisim_ayarlari_ac

            tum_dosya_erisim_ayarlari_ac()
            self.detail_label.text = "Ayar ekranı açıldı. Geri dönünce durum yenilenir."
            self._start_settings_watch()
        except Exception as exc:
            self._apply_unknown_state(f"Ayar ekranı açılamadı: {exc}")
            self._debug(f"Ayar ekranı açılamadı: {exc}")

    def refresh_status(self) -> None:
        if platform != "android":
            onceki = self._last_status
            self._last_status = False
            self._apply_non_android_state()

            try:
                if self.on_status_changed and onceki != self._last_status:
                    self.on_status_changed(False)
            except Exception:
                pass
            return

        try:
            from app.services.android_ozel_izin_servisi import tum_dosya_erisim_izni_var_mi

            durum = bool(tum_dosya_erisim_izni_var_mi())
            onceki = self._last_status
            self._last_status = durum

            if durum:
                self._apply_open_state()
            else:
                self._apply_closed_state()

            try:
                if self.on_status_changed and onceki != durum:
                    self.on_status_changed(durum)
            except Exception:
                pass

            self._debug(f"Tüm dosya erişimi durumu: {durum}")
        except Exception as exc:
            onceki = self._last_status
            self._last_status = None
            self._apply_unknown_state(f"İzin durumu okunamadı: {exc}")

            try:
                if self.on_status_changed and onceki is not None:
                    self.on_status_changed(False)
            except Exception:
                pass

            self._debug(f"İzin durumu okunamadı: {exc}")

    # =========================================================
    # EVENTLER
    # =========================================================
    def _handle_status_icon_click(self, *_args) -> None:
        self._open_settings()

    def _handle_open_action(self, *_args) -> None:
        self._open_settings()

    def _handle_close_action(self, *_args) -> None:
        self._open_settings()

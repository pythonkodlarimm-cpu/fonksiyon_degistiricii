# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/tum_dosya_erisim_paneli.py

ROL:
- Ana ekranda sadece menu.png gösterir
- Menüye basınca erişim ve yedek popup akışlarını açar
- Yedeklenen dosyaları görüntüler
- Erişim ayar ekranını açar
- Animasyonlu separator ve glow efektleri içerir

SURUM: 20
TARIH: 2026-03-18
IMZA: FY.
"""

from __future__ import annotations

import math
from pathlib import Path

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform

from app.ui.kart import Kart
from app.ui.tema import TEXT_MUTED, TEXT_PRIMARY


class TiklanabilirIcon(ButtonBehavior, Image):
    pass


class AnimatedSeparator(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(6),
            **kwargs,
        )

        self._phase = 0.0
        self._segment_count = 7
        self._segment_colors = []
        self._segment_rects = []
        self._anim_event = None

        with self.canvas.before:
            for _ in range(self._segment_count):
                color = Color(1, 1, 1, 1)
                rect = RoundedRectangle(radius=[dp(4)])
                self._segment_colors.append(color)
                self._segment_rects.append(rect)

        self.bind(pos=self._update_graphics, size=self._update_graphics)
        self._update_graphics()
        self._start_animation()

    def _update_graphics(self, *_args):
        if self._segment_count <= 0:
            return

        bosluk = dp(3)
        toplam_bosluk = bosluk * (self._segment_count - 1)
        parca_genislik = max(1.0, (self.width - toplam_bosluk) / self._segment_count)

        x = self.x
        for rect in self._segment_rects:
            rect.pos = (x, self.y)
            rect.size = (parca_genislik, self.height)
            x += parca_genislik + bosluk

    def _animate(self, dt):
        self._phase += dt * 3.2

        for i, color in enumerate(self._segment_colors):
            p = self._phase + (i * 0.55)
            r = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(p + 0.0))
            g = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(p + 2.1))
            b = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(p + 4.2))
            color.rgba = (r, g, b, 1)

    def _start_animation(self):
        self._stop_animation()
        self._anim_event = Clock.schedule_interval(self._animate, 1 / 24)

    def _stop_animation(self):
        try:
            if self._anim_event is not None:
                self._anim_event.cancel()
        except Exception:
            pass
        self._anim_event = None

    def on_parent(self, _instance, parent):
        if parent is None:
            self._stop_animation()
        elif self._anim_event is None:
            self._start_animation()


class TumDosyaErisimPaneli(Kart):
    def __init__(self, on_status_changed=None, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            padding=(dp(10), dp(10)),
            bg=(0.08, 0.11, 0.16, 1),
            border=(0.18, 0.21, 0.27, 1),
            radius=12,
            **kwargs,
        )

        self.on_status_changed = on_status_changed
        self.menu_icon = None
        self._last_status = None
        self._menu_anim = None
        self._popup_action_anim = None
        self._current_popup_action_icon = None
        self._current_popup = None

        self._build_ui()
        self.refresh_status()
        self._start_menu_glow()

    # =========================================================
    # DEBUG / FALLBACK
    # =========================================================
    def _debug(self, message: str) -> None:
        try:
            print("[TUM_DOSYA_ERISIM]", str(message))
        except Exception:
            pass

    def _show_simple_popup(self, title_text: str, body_text: str) -> None:
        try:
            content = BoxLayout(
                orientation="vertical",
                padding=dp(14),
                spacing=dp(10),
            )

            title = Label(
                text=str(title_text or ""),
                color=TEXT_PRIMARY,
                font_size="17sp",
                bold=True,
                size_hint_y=None,
                height=dp(28),
                halign="center",
                valign="middle",
            )
            title.bind(size=lambda inst, size: setattr(inst, "text_size", size))
            content.add_widget(title)

            body = Label(
                text=str(body_text or ""),
                color=TEXT_PRIMARY,
                halign="left",
                valign="top",
            )
            body.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))

            scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
            scroll.add_widget(body)
            content.add_widget(scroll)

            popup = Popup(
                title="",
                content=content,
                size_hint=(0.92, 0.62),
                auto_dismiss=True,
                separator_height=0,
            )
            popup.open()
        except Exception as exc:
            self._debug(f"simple popup açılamadı: {exc}")

    # =========================================================
    # UI
    # =========================================================
    def _build_ui(self):
        self.menu_icon = TiklanabilirIcon(
            source="app/assets/icons/menu.png",
            size_hint=(None, None),
            size=(dp(36), dp(36)),
            opacity=1,
            allow_stretch=True,
            keep_ratio=True,
        )
        self.menu_icon.bind(on_release=self._open_main_menu)
        self.add_widget(self.menu_icon)

    # =========================================================
    # STATUS
    # =========================================================
    def refresh_status(self):
        onceki = self._last_status

        if platform != "android":
            self._last_status = False
        else:
            try:
                from app.services.android_ozel_izin_servisi import (
                    tum_dosya_erisim_izni_var_mi,
                )
                self._last_status = bool(tum_dosya_erisim_izni_var_mi())
            except Exception as exc:
                self._last_status = None
                self._debug(f"Durum okuma hatası: {exc}")

        try:
            if self.on_status_changed and onceki != self._last_status:
                self.on_status_changed(bool(self._last_status))
        except Exception:
            pass

    # =========================================================
    # ANIMATION
    # =========================================================
    def _stop_menu_glow(self) -> None:
        try:
            if self._menu_anim is not None and self.menu_icon is not None:
                self._menu_anim.cancel(self.menu_icon)
        except Exception:
            pass
        self._menu_anim = None

    def _start_menu_glow(self) -> None:
        self._stop_menu_glow()
        try:
            anim = (
                Animation(opacity=0.72, size=(dp(40), dp(40)), duration=0.60)
                + Animation(opacity=1.0, size=(dp(36), dp(36)), duration=0.60)
            )
            anim.repeat = True
            anim.start(self.menu_icon)
            self._menu_anim = anim
        except Exception:
            pass

    def _stop_popup_action_glow(self) -> None:
        try:
            if self._popup_action_anim is not None and self._current_popup_action_icon is not None:
                self._popup_action_anim.cancel(self._current_popup_action_icon)
        except Exception:
            pass
        self._popup_action_anim = None

    def _start_popup_action_glow(self) -> None:
        self._stop_popup_action_glow()
        try:
            if self._current_popup_action_icon is None:
                return

            anim = (
                Animation(opacity=0.74, size=(dp(96), dp(96)), duration=0.55)
                + Animation(opacity=1.0, size=(dp(88), dp(88)), duration=0.55)
            )
            anim.repeat = True
            anim.start(self._current_popup_action_icon)
            self._popup_action_anim = anim
        except Exception:
            pass

    # =========================================================
    # MAIN MENU
    # =========================================================
    def _open_main_menu(self, *_args):
        try:
            self.refresh_status()

            content = BoxLayout(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(12),
            )

            title = Label(
                text="Menü İşlemleri",
                color=TEXT_PRIMARY,
                font_size="19sp",
                bold=True,
                size_hint_y=None,
                height=dp(30),
                halign="center",
                valign="middle",
            )
            title.bind(size=lambda inst, size: setattr(inst, "text_size", size))
            content.add_widget(title)

            separator = AnimatedSeparator()
            content.add_widget(separator)

            buttons = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(100),
                spacing=dp(18),
            )

            erisim_wrap = BoxLayout(orientation="vertical", spacing=dp(6))
            erisim_btn = TiklanabilirIcon(
                source="app/assets/icons/settings.png",
                size_hint=(None, None),
                size=(dp(58), dp(58)),
                allow_stretch=True,
                keep_ratio=True,
            )
            erisim_lbl = Label(
                text="Erişim İşlemleri",
                color=TEXT_PRIMARY,
                font_size="12sp",
                halign="center",
                valign="middle",
            )
            erisim_lbl.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))
            erisim_icon_row = BoxLayout(size_hint_y=None, height=dp(64))
            erisim_icon_row.add_widget(Label(size_hint_x=1))
            erisim_icon_row.add_widget(erisim_btn)
            erisim_icon_row.add_widget(Label(size_hint_x=1))
            erisim_wrap.add_widget(erisim_icon_row)
            erisim_wrap.add_widget(erisim_lbl)

            yedek_wrap = BoxLayout(orientation="vertical", spacing=dp(6))
            yedek_btn = TiklanabilirIcon(
                source="app/assets/icons/yedeklenen_dosyalar.png",
                size_hint=(None, None),
                size=(dp(58), dp(58)),
                allow_stretch=True,
                keep_ratio=True,
            )
            yedek_lbl = Label(
                text="Yedeklenen Dosyalar",
                color=TEXT_PRIMARY,
                font_size="12sp",
                halign="center",
                valign="middle",
            )
            yedek_lbl.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))
            yedek_icon_row = BoxLayout(size_hint_y=None, height=dp(64))
            yedek_icon_row.add_widget(Label(size_hint_x=1))
            yedek_icon_row.add_widget(yedek_btn)
            yedek_icon_row.add_widget(Label(size_hint_x=1))
            yedek_wrap.add_widget(yedek_icon_row)
            yedek_wrap.add_widget(yedek_lbl)

            buttons.add_widget(erisim_wrap)
            buttons.add_widget(yedek_wrap)
            content.add_widget(buttons)

            popup = Popup(
                title="",
                content=content,
                size_hint=(0.92, None),
                height=dp(240),
                auto_dismiss=True,
                separator_height=0,
            )

            erisim_btn.bind(on_release=lambda *_: self._switch_popup(popup, self._open_access_popup))
            yedek_btn.bind(on_release=lambda *_: self._switch_popup(popup, self._open_backups_popup))

            popup.open()
        except Exception as exc:
            self._debug(f"ana menü açılamadı: {exc}")
            self._show_simple_popup("Menü Hatası", f"Menü açılamadı:\n{exc}")

    def _switch_popup(self, old_popup, next_open_fn):
        try:
            old_popup.dismiss()
        except Exception:
            pass
        Clock.schedule_once(lambda *_: next_open_fn(), 0.05)

    # =========================================================
    # ACCESS POPUP
    # =========================================================
    def _open_access_popup(self):
        self.refresh_status()

        if self._last_status is True:
            durum_text = "Tüm Dosya Erişimi Açık"
            action_icon = "app/assets/icons/setting_on.png"
            durum_color = (0.26, 1.0, 0.42, 1)
            action_desc = "Erişimi kapatmak için aşağıdaki simgeye dokunun."
        elif self._last_status is False:
            durum_text = "Tüm Dosya Erişimi Kapalı"
            action_icon = "app/assets/icons/setting_off.png"
            durum_color = (1.0, 0.38, 0.38, 1)
            action_desc = "Erişimi açmak için aşağıdaki simgeye dokunun."
        else:
            durum_text = "Durum Bilinmiyor"
            action_icon = "app/assets/icons/warning.png"
            durum_color = (1.0, 0.82, 0.36, 1)
            action_desc = "Durum okunamadı. Aşağıdaki simge ile ayar ekranını açabilirsiniz."

        content = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
        )

        title = Label(
            text="Erişim İşlemleri",
            color=TEXT_PRIMARY,
            font_size="19sp",
            bold=True,
            size_hint_y=None,
            height=dp(30),
            halign="center",
            valign="middle",
        )
        title.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        content.add_widget(title)

        durum = Label(
            text=durum_text,
            color=durum_color,
            font_size="17sp",
            bold=True,
            size_hint_y=None,
            height=dp(28),
            halign="center",
            valign="middle",
        )
        durum.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        content.add_widget(durum)

        content.add_widget(AnimatedSeparator())

        action_wrap = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(162),
            spacing=dp(10),
        )

        self._current_popup_action_icon = TiklanabilirIcon(
            source=action_icon,
            size_hint=(None, None),
            size=(dp(88), dp(88)),
            opacity=1,
            allow_stretch=True,
            keep_ratio=True,
        )

        icon_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(102),
        )
        icon_row.add_widget(Label(size_hint_x=1))
        icon_row.add_widget(self._current_popup_action_icon)
        icon_row.add_widget(Label(size_hint_x=1))

        desc_label = Label(
            text=action_desc,
            color=TEXT_PRIMARY,
            font_size="14sp",
            size_hint_y=None,
            height=dp(44),
            halign="center",
            valign="middle",
        )
        desc_label.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))

        action_wrap.add_widget(icon_row)
        action_wrap.add_widget(desc_label)
        content.add_widget(action_wrap)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.90, None),
            height=dp(318),
            auto_dismiss=True,
            separator_height=0,
        )

        self._current_popup_action_icon.bind(on_release=lambda *_: self._handle_action(popup))
        popup.bind(on_open=lambda *_: self._start_popup_action_glow())
        popup.bind(on_dismiss=lambda *_: self._on_popup_dismiss())
        popup.open()

    # =========================================================
    # BACKUPS POPUP
    # =========================================================
    def _open_backups_popup(self):
        try:
            self._debug("yedek popup açılıyor")

            from app.services.yedek_listeleme_servisi import yedekleri_listele

            try:
                yedekler = yedekleri_listele()
                self._debug(f"yedek sayısı: {len(yedekler)}")
            except Exception as exc:
                self._debug(f"Yedek listeleme hatası: {exc}")
                self._show_simple_popup(
                    "Yedek Hatası",
                    f"Yedekler listelenemedi:\n{exc}",
                )
                return

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

            content.add_widget(AnimatedSeparator())

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

            if not yedekler:
                bos = Label(
                    text="Henüz yedeklenen dosya yok.",
                    color=TEXT_MUTED,
                    size_hint_y=None,
                    height=dp(36),
                    halign="center",
                    valign="middle",
                )
                bos.bind(size=lambda inst, size: setattr(inst, "text_size", size))
                liste.add_widget(bos)
            else:
                for yedek in yedekler:
                    try:
                        liste.add_widget(self._build_backup_row(yedek))
                    except Exception as exc:
                        self._debug(f"yedek satırı oluşturulamadı: {yedek} | {exc}")

            scroll.add_widget(liste)
            content.add_widget(scroll)

            popup = Popup(
                title="",
                content=content,
                size_hint=(0.94, 0.82),
                auto_dismiss=True,
                separator_height=0,
            )
            popup.open()

        except Exception as exc:
            self._debug(f"_open_backups_popup kritik hata: {exc}")
            self._show_simple_popup(
                "Yedek Popup Hatası",
                f"Yedek ekranı açılamadı:\n{exc}",
            )

    def _build_backup_row(self, yedek: Path):
        satir = Kart(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(66),
            padding=(dp(10), dp(8), dp(10), dp(8)),
            spacing=dp(8),
            bg=(0.10, 0.13, 0.18, 1),
            border=(0.18, 0.21, 0.27, 1),
            radius=12,
        )

        metin_wrap = BoxLayout(orientation="vertical", spacing=dp(2))

        ad = Label(
            text=str(getattr(yedek, "name", "") or ""),
            color=TEXT_PRIMARY,
            font_size="13sp",
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(22),
            shorten=True,
            shorten_from="right",
        )
        ad.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))

        yol = Label(
            text=str(yedek),
            color=TEXT_MUTED,
            font_size="10sp",
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(18),
            shorten=True,
            shorten_from="center",
        )
        yol.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))

        metin_wrap.add_widget(ad)
        metin_wrap.add_widget(yol)

        aksiyonlar = BoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            width=dp(110),
            spacing=dp(8),
        )

        gor_btn = TiklanabilirIcon(
            source="app/assets/icons/visibility_on.png",
            size_hint=(None, None),
            size=(dp(32), dp(32)),
            allow_stretch=True,
            keep_ratio=True,
        )
        indir_btn = TiklanabilirIcon(
            source="app/assets/icons/download.png",
            size_hint=(None, None),
            size=(dp(32), dp(32)),
            allow_stretch=True,
            keep_ratio=True,
        )

        gor_btn.bind(on_release=lambda *_: self._safe_open_backup_view(yedek))
        indir_btn.bind(on_release=lambda *_: self._safe_download_backup(yedek))

        aksiyonlar.add_widget(gor_btn)
        aksiyonlar.add_widget(indir_btn)

        satir.add_widget(metin_wrap)
        satir.add_widget(aksiyonlar)
        return satir

    def _safe_open_backup_view(self, yedek: Path) -> None:
        try:
            self._open_backup_view_popup(yedek)
        except Exception as exc:
            self._debug(f"yedek görüntüleme hatası: {exc}")
            self._show_simple_popup(
                "Görüntüleme Hatası",
                f"Yedek açılamadı:\n{exc}",
            )

    def _open_backup_view_popup(self, yedek: Path):
        try:
            from app.services.dosya_servisi import read_text
            icerik = read_text(yedek)
        except Exception as exc:
            icerik = f"Dosya görüntülenemedi: {exc}"

        content = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(8),
        )

        baslik = Label(
            text=str(getattr(yedek, "name", "") or ""),
            color=TEXT_PRIMARY,
            font_size="16sp",
            bold=True,
            size_hint_y=None,
            height=dp(28),
            halign="center",
            valign="middle",
        )
        baslik.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        content.add_widget(baslik)

        body = Label(
            text=str(icerik or ""),
            color=TEXT_PRIMARY,
            halign="left",
            valign="top",
            size_hint_y=None,
        )
        body.bind(texture_size=lambda inst, val: setattr(inst, "height", max(dp(40), val[1])))
        body.bind(size=lambda inst, size: setattr(inst, "text_size", (size[0], None)))

        scroll = ScrollView(do_scroll_x=True, do_scroll_y=True)
        scroll.add_widget(body)
        content.add_widget(scroll)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.95, 0.88),
            auto_dismiss=True,
            separator_height=0,
        )
        popup.open()

    def _safe_download_backup(self, yedek: Path) -> None:
        try:
            self._download_backup(yedek)
        except Exception as exc:
            self._debug(f"yedek indirme hata wrapper: {exc}")
            self._show_simple_popup(
                "İndirme Hatası",
                f"Yedek indirilemedi:\n{exc}",
            )

    def _download_backup(self, yedek: Path):
        try:
            from app.services.yedek_indirme_servisi import yedegi_indir
            hedef = yedegi_indir(yedek)
            self._debug(f"Yedek indirildi: {hedef}")
            self._show_simple_popup(
                "İndirme Tamam",
                f"Yedek kaydedildi:\n{hedef}",
            )
        except Exception as exc:
            self._debug(f"Yedek indirme hatası: {exc}")
            raise

    # =========================================================
    # POPUP CLEANUP
    # =========================================================
    def _on_popup_dismiss(self) -> None:
        self._stop_popup_action_glow()
        self._current_popup = None
        self._current_popup_action_icon = None

    # =========================================================
    # ACTION
    # =========================================================
    def _handle_action(self, popup):
        if platform == "android":
            try:
                from app.services.android_ozel_izin_servisi import (
                    tum_dosya_erisim_ayarlari_ac,
                )
                tum_dosya_erisim_ayarlari_ac()
            except Exception as exc:
                self._debug(f"Ayar açma hatası: {exc}")
                self._show_simple_popup(
                    "Ayar Hatası",
                    f"Ayar ekranı açılamadı:\n{exc}",
                )
        else:
            self._debug("Android dışı ortamda ayar ekranı açılamaz.")
            self._show_simple_popup(
                "Bilgi",
                "Bu işlem yalnızca Android ortamında kullanılabilir.",
            )

        try:
            popup.dismiss()
        except Exception:
            pass
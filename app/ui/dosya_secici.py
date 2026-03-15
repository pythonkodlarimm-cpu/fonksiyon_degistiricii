# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici.py
ROL:
- Python dosyası seçme alanı
- Seçilen dosyayı tarama / yenileme akışını başlatma
- Masaüstünde özel popup ile, Android'de sistem belge seçici ile dosya seçimi sağlar

MİMARİ:
- Kendi görünümünü kendi çizer
- Root sadece callback verir
- Dosya seçimi, popup ve araç satırı burada yönetilir

DAVRANIŞ:
- Android'de dosya seçildiği anda otomatik tarama başlar
- Masaüstünde popup'tan dosya seçildiği anda otomatik tarama başlar
- Ayrı "Tara" aksiyonu kaldırılmıştır

DEBUG:
- Dosya seçiminin hangi aşamada koptuğunu görmek için debug mesajları vardır
- Mesajlar print ile konsola/loga düşer

SURUM: 12
TARIH: 2026-03-15
IMZA: FY.
"""

from __future__ import annotations

from pathlib import Path

from kivy.clock import Clock
from kivy.graphics import Color
from kivy.graphics import RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.utils import platform

from app.ui.icon_toolbar import IconToolbar
from app.ui.iconlu_baslik import IconluBaslik
from app.ui.tema import (
    CARD_BG,
    CARD_BG_DARK,
    CARD_BG_SOFT,
    INPUT_BG,
    RADIUS_MD,
    TEXT_MUTED,
    TEXT_PRIMARY,
)


def _varsayilan_baslangic_klasoru() -> Path:
    adaylar = [
        Path.home(),
        Path.cwd(),
    ]

    for aday in adaylar:
        try:
            if aday.exists() and aday.is_dir():
                return aday.resolve()
        except Exception:
            pass

    return Path.cwd().resolve()


class _SatirKart(BoxLayout):
    def __init__(self, bg=(0.16, 0.16, 0.18, 1), radius=14, **kwargs):
        super().__init__(**kwargs)
        self._bg = tuple(bg)
        self._radius = float(radius)

        with self.canvas.before:
            self._bg_color = Color(*self._bg)
            self._bg_rect = RoundedRectangle(radius=[dp(self._radius)])

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

    def _update_canvas(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size


class DosyaSecici(BoxLayout):
    ANDROID_PICK_REQUEST_CODE = 12091

    def __init__(self, on_scan, on_refresh=None, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(156),
            spacing=dp(8),
            **kwargs,
        )

        self.on_scan = on_scan
        self.on_refresh = on_refresh
        self.popup = None

        self._android_result_bound = False
        self._android_last_temp_file = None
        self._last_selected_path = ""
        self._picker_open = False

        self._build_ui()
        self._android_bind_activity_result()

    # =========================================================
    # DEBUG
    # =========================================================
    def _debug(self, message: str) -> None:
        try:
            print("[DOSYA_SECICI]", str(message))
        except Exception:
            pass

    # =========================================================
    # UI
    # =========================================================
    def _build_ui(self) -> None:
        self._build_header()
        self._build_path_box()
        self._build_action_row()

    def _build_header(self) -> None:
        self.header = IconluBaslik(
            text="Python Dosyası",
            icon_name="schema.png",
            height_dp=30,
            font_size="15sp",
            color=TEXT_PRIMARY,
        )
        self.add_widget(self.header)

    def _build_path_box(self) -> None:
        self.path_input = TextInput(
            hint_text="Python dosyası seç...",
            multiline=False,
            readonly=True,
            size_hint_y=None,
            height=dp(46),
            background_normal="",
            background_active="",
            background_color=INPUT_BG,
            foreground_color=TEXT_PRIMARY,
            cursor_color=TEXT_PRIMARY,
            padding=(dp(12), dp(12)),
            font_size="14sp",
        )
        self.add_widget(self.path_input)

        self.path_hint = Label(
            text="Seçilen dosya burada görünecek",
            size_hint_y=None,
            height=dp(16),
            color=TEXT_MUTED,
            font_size="12sp",
            halign="left",
            valign="middle",
            shorten=True,
            shorten_from="right",
        )
        self.path_hint.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
        self.add_widget(self.path_hint)

    def _build_action_row(self) -> None:
        toolbar = IconToolbar(
            spacing_dp=24,
            padding_dp=8,
        )

        toolbar.add_tool(
            icon_name="folder_open.png",
            text="Seç",
            on_release=self._open_selector,
            icon_size_dp=42,
            text_size="12sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        toolbar.add_tool(
            icon_name="refresh.png",
            text="Yenile",
            on_release=self._handle_refresh,
            icon_size_dp=42,
            text_size="12sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        self.add_widget(toolbar)

    # =========================================================
    # PUBLIC API
    # =========================================================
    def get_path(self) -> str:
        text_path = self.path_input.text.strip()
        if text_path:
            return text_path
        return str(self._last_selected_path or "").strip()

    def set_path(self, value: str) -> None:
        temiz = str(value or "").strip()
        self.path_input.text = temiz
        self.path_hint.text = temiz if temiz else "Seçilen dosya burada görünecek"
        self._last_selected_path = temiz
        self._debug(f"Path set edildi: {temiz}")

    # =========================================================
    # ACTIONS
    # =========================================================
    def _handle_refresh(self, *_args):
        yol = self.get_path()
        self._debug(f"Yenile tetiklendi: {yol}")

        if self.on_refresh:
            self.on_refresh(yol)
        elif self.on_scan:
            self.on_scan(yol)

    def _open_selector(self, *_args):
        self._debug("Dosya seçici açılıyor")

        if platform == "android":
            self._show_android_picker_info_popup()
        else:
            self._open_popup()

    def _after_file_selected(self, selected_path: str) -> None:
        self._debug(f"Dosya seçildi: {selected_path}")

        temiz = str(selected_path or "").strip()
        if not temiz:
            self._show_info_popup(
                "Dosya Seçici",
                "Seçilen dosya yolu alınamadı.",
            )
            return

        try:
            p = Path(temiz)
            if not p.exists() or not p.is_file():
                self._show_info_popup(
                    "Dosya Seçici",
                    f"Seçilen dosya bulunamadı:\n{temiz}",
                )
                return
        except Exception as exc:
            self._show_info_popup(
                "Dosya Seçici",
                f"Dosya doğrulanamadı:\n{exc}",
            )
            return

        self.set_path(temiz)

        def _run_scan(_dt):
            try:
                final_path = self.get_path()
                self._debug(f"Otomatik tarama başlıyor: {final_path}")

                if not final_path:
                    self._show_info_popup(
                        "Tarama Hatası",
                        "Dosya yolu boş olduğu için tarama başlatılamadı.",
                    )
                    return

                if self.on_scan:
                    self.on_scan(final_path)
            except Exception as exc:
                self._show_info_popup(
                    "Tarama Hatası",
                    f"Dosya seçildi ama tarama başlatılamadı:\n{exc}",
                )

        Clock.schedule_once(_run_scan, 0)

    # =========================================================
    # ANDROID SYSTEM PICKER
    # =========================================================
    def _android_bind_activity_result(self):
        if platform != "android":
            return

        if self._android_result_bound:
            return

        try:
            from android import activity  # type: ignore

            activity.bind(on_activity_result=self._on_android_activity_result)
            self._android_result_bound = True
            self._debug("Android activity result bind edildi")
        except Exception as exc:
            self._android_result_bound = False
            self._debug(f"Android bind hatası: {exc}")

    def _show_android_picker_info_popup(self):
        ana = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(12),
        )

        mesaj = (
            "Python dosyası seçmek üzeresiniz.\n\n"
            "Uygulama yalnızca sizin seçtiğiniz dosyaya erişir.\n"
            "Bu erişimi daha sonra cihaz ayarlarından değiştirebilirsiniz.\n\n"
            "Devam ettiğinizde Android sistem dosya seçicisi açılacaktır."
        )

        lbl = Label(
            text=mesaj,
            color=TEXT_PRIMARY,
            halign="left",
            valign="top",
            size_hint_y=None,
            font_size="15sp",
        )

        def _lbl_guncelle(*_args):
            try:
                lbl.text_size = (lbl.width, None)
                lbl.texture_update()
                lbl.height = lbl.texture_size[1]
            except Exception:
                pass

        lbl.bind(width=lambda *_: _lbl_guncelle(), texture_size=lambda *_: _lbl_guncelle())
        _lbl_guncelle()
        ana.add_widget(lbl)

        toolbar = IconToolbar(
            spacing_dp=18,
            padding_dp=6,
        )

        vazgec_btn = toolbar.add_tool(
            icon_name="cancel.png",
            text="Vazgeç",
            on_release=lambda *_: None,
            icon_size_dp=36,
            text_size="11sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        ayarlar_btn = toolbar.add_tool(
            icon_name="settings.png",
            text="Ayarlar",
            on_release=lambda *_: None,
            icon_size_dp=36,
            text_size="11sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        devam_btn = toolbar.add_tool(
            icon_name="onaylandi.png",
            text="Devam",
            on_release=lambda *_: None,
            icon_size_dp=36,
            text_size="11sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        ana.add_widget(toolbar)

        popup = Popup(
            title="Dosya Erişimi",
            content=ana,
            size_hint=(0.92, 0.50),
            auto_dismiss=False,
            separator_height=0,
        )

        def _vazgec(*_args):
            self._debug("Picker bilgi popup: vazgeç")
            popup.dismiss()

        def _ayarlar(*_args):
            self._debug("Picker bilgi popup: ayarlar")
            self._open_app_settings()

        def _devam(*_args):
            self._debug("Picker bilgi popup: devam")
            popup.dismiss()
            self._picker_open = True
            self._open_android_document_picker()

            Clock.schedule_once(self._force_picker_reset, 10)

        vazgec_btn.bind(on_release=_vazgec)
        ayarlar_btn.bind(on_release=_ayarlar)
        devam_btn.bind(on_release=_devam)

        popup.open()

    def _force_picker_reset(self, *_args):
        self._picker_open = False
        self._debug("Picker force reset çalıştı")

    def _open_app_settings(self):
        if platform != "android":
            return

        try:
            from jnius import autoclass, cast  # type: ignore

            Intent = autoclass("android.content.Intent")
            Uri = autoclass("android.net.Uri")
            Settings = autoclass("android.provider.Settings")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")

            current_activity = cast("android.app.Activity", PythonActivity.mActivity)
            intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
            intent.setData(Uri.parse("package:" + current_activity.getPackageName()))
            current_activity.startActivity(intent)
            self._debug("Uygulama ayarları açıldı")
        except Exception as exc:
            self._show_info_popup(
                "Ayarlar",
                f"Ayarlar ekranı açılamadı:\n{exc}",
            )

    def _open_android_document_picker(self):
        self._debug("Android picker açıldı")

        try:
            from jnius import autoclass, cast  # type: ignore

            Intent = autoclass("android.content.Intent")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")

            current_activity = cast("android.app.Activity", PythonActivity.mActivity)

            intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            intent.setType("*/*")

            mime_types = [
                "text/plain",
                "text/x-python",
                "application/json",
                "application/octet-stream",
            ]
            intent.putExtra(Intent.EXTRA_MIME_TYPES, mime_types)

            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            intent.addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)

            current_activity.startActivityForResult(
                intent,
                self.ANDROID_PICK_REQUEST_CODE,
            )
        except Exception as exc:
            self._picker_open = False
            self._show_info_popup(
                "Dosya Seçici Hatası",
                f"Android dosya seçici açılamadı:\n{exc}",
            )

    def _android_cache_root(self) -> Path:
        """
        Android'de tempfile yerine uygulamanın gerçek cache klasörünü kullan.
        """
        if platform != "android":
            return Path.cwd()

        try:
            from jnius import autoclass, cast  # type: ignore

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            current_activity = cast("android.app.Activity", PythonActivity.mActivity)
            cache_dir = current_activity.getCacheDir()
            cache_path = str(cache_dir.getAbsolutePath())
            root = Path(cache_path) / "fonksiyon_degistirici_android"
            root.mkdir(parents=True, exist_ok=True)
            self._debug(f"Android cache root: {root}")
            return root
        except Exception as exc:
            self._debug(f"Android cache root fallback: {exc}")
            fallback = Path.cwd() / "fonksiyon_degistirici_android"
            fallback.mkdir(parents=True, exist_ok=True)
            return fallback

    def _on_android_activity_result(self, request_code, result_code, intent):
        self._debug("Android activity result geldi")

        if platform != "android":
            return

        if request_code != self.ANDROID_PICK_REQUEST_CODE:
            self._debug(f"Istenen request code değil: {request_code}")
            return

        self._picker_open = False

        try:
            from jnius import autoclass, cast  # type: ignore

            Activity = autoclass("android.app.Activity")
            Intent = autoclass("android.content.Intent")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")

            self._debug(f"Result code: {result_code}")

            if result_code != Activity.RESULT_OK:
                self._debug("Result OK değil, seçim iptal edilmiş olabilir")
                return

            if intent is None:
                self._show_info_popup("Dosya Seçici", "Dosya seçimi tamamlanmadı.")
                return

            uri = intent.getData()
            self._debug(f"URI alındı: {uri}")

            if uri is None:
                self._show_info_popup("Dosya Seçici", "Dosya seçilemedi.")
                return

            current_activity = cast("android.app.Activity", PythonActivity.mActivity)
            resolver = current_activity.getContentResolver()

            try:
                flags = intent.getFlags()
                take_flags = (
                    flags
                    & (
                        Intent.FLAG_GRANT_READ_URI_PERMISSION
                        | Intent.FLAG_GRANT_WRITE_URI_PERMISSION
                    )
                )
                resolver.takePersistableUriPermission(uri, take_flags)
                self._debug("Persistable uri izni alındı")
            except Exception as exc:
                self._debug(f"Persistable izin alınamadı: {exc}")

            secilen_yol = self._android_copy_uri_to_temp_file(resolver, uri)
            self._debug(f"Temp dosya: {secilen_yol}")

            if not secilen_yol:
                self._show_info_popup(
                    "Dosya Seçici",
                    "Seçilen dosya uygulamaya aktarılamadı.",
                )
                return

            self._after_file_selected(secilen_yol)
        except Exception as exc:
            self._show_info_popup(
                "Dosya Seçici Hatası",
                f"Seçilen dosya işlenemedi:\n{exc}",
            )

    def _android_copy_uri_to_temp_file(self, resolver, uri) -> str:
        input_stream = None

        try:
            display_name = self._android_get_display_name(resolver, uri) or "secilen_dosya.py"
            display_name = str(display_name).strip() or "secilen_dosya.py"
            self._debug(f"Gorunen dosya adı: {display_name}")

            if not display_name.lower().endswith(".py"):
                if "." not in display_name:
                    display_name += ".py"

            input_stream = resolver.openInputStream(uri)
            if input_stream is None:
                self._debug("openInputStream None döndü")
                return ""

            cache_root = self._android_cache_root()
            target_path = cache_root / display_name

            if self._android_last_temp_file:
                try:
                    eski = Path(self._android_last_temp_file)
                    if eski.exists() and eski.is_file():
                        eski.unlink()
                        self._debug(f"Eski temp silindi: {eski}")
                except Exception as exc:
                    self._debug(f"Eski temp silinemedi: {exc}")

            toplam_yazilan = 0

            with open(target_path, "wb") as out_file:
                while True:
                    byte_val = input_stream.read()
                    if byte_val == -1:
                        break
                    out_file.write(bytes([byte_val]))
                    toplam_yazilan += 1

            self._debug(f"Yazılan byte: {toplam_yazilan}")

            if toplam_yazilan <= 0:
                try:
                    if target_path.exists():
                        target_path.unlink()
                except Exception:
                    pass
                return ""

            self._android_last_temp_file = str(target_path)
            return str(target_path)

        except Exception as exc:
            self._debug(f"Temp kopyalama hatası: {exc}")
            return ""
        finally:
            try:
                if input_stream is not None:
                    input_stream.close()
            except Exception:
                pass

    def _android_get_display_name(self, resolver, uri):
        cursor = None
        try:
            from jnius import autoclass  # type: ignore

            OpenableColumns = autoclass("android.provider.OpenableColumns")

            cursor = resolver.query(uri, None, None, None, None)
            if cursor is not None and cursor.moveToFirst():
                idx = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                if idx >= 0:
                    return cursor.getString(idx)
        except Exception as exc:
            self._debug(f"Display name query hatası: {exc}")
        finally:
            try:
                if cursor is not None:
                    cursor.close()
            except Exception:
                pass

        try:
            path_str = str(uri.toString())
            if "/" in path_str:
                return path_str.rsplit("/", 1)[-1]
        except Exception:
            pass

        return None

    # =========================================================
    # POPUP HELPERS
    # =========================================================
    def _build_popup_toolbar(self):
        toolbar = IconToolbar(
            spacing_dp=14,
            padding_dp=0,
        )

        geri_btn = toolbar.add_tool(
            icon_name="arrow_back_geri.png",
            text="Yukarı",
            on_release=lambda *_: None,
            icon_size_dp=32,
            text_size="10sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        ana_depo_btn = toolbar.add_tool(
            icon_name="folder_open.png",
            text="Ana Depo",
            on_release=lambda *_: None,
            icon_size_dp=32,
            text_size="10sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        yenile_btn = toolbar.add_tool(
            icon_name="refresh.png",
            text="Yenile",
            on_release=lambda *_: None,
            icon_size_dp=32,
            text_size="10sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        kapat_btn = toolbar.add_tool(
            icon_name="cancel.png",
            text="Kapat",
            on_release=lambda *_: None,
            icon_size_dp=32,
            text_size="10sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        return toolbar, geri_btn, ana_depo_btn, yenile_btn, kapat_btn

    def _popup_satiri_ekle(self, liste, text, callback, renk):
        sarici = _SatirKart(
            orientation="vertical",
            size_hint_y=None,
            height=dp(56),
            padding=(0, 0),
            bg=renk,
            radius=RADIUS_MD,
        )

        btn = Button(
            text=text,
            size_hint=(1, 1),
            halign="left",
            valign="middle",
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            color=TEXT_PRIMARY,
            bold=False,
            font_size="13sp",
            shorten=True,
            shorten_from="right",
        )
        btn.bind(
            size=lambda inst, size: setattr(
                inst,
                "text_size",
                (size[0] - dp(20), size[1]),
            )
        )
        btn.bind(on_release=callback)

        sarici.add_widget(btn)
        liste.add_widget(sarici)

    # =========================================================
    # DESKTOP / NORMAL PYTHON POPUP
    # =========================================================
    def _open_popup(self, *_args):
        if self.popup:
            try:
                self.popup.dismiss()
            except Exception:
                pass
            self.popup = None

        mevcut_klasor = _varsayilan_baslangic_klasoru()
        alt_sinir = Path(mevcut_klasor.anchor) if mevcut_klasor.anchor else mevcut_klasor

        ana = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(8),
        )

        ust_baslik = IconluBaslik(
            text="Python Dosyası Seç",
            icon_name="schema.png",
            height_dp=32,
            font_size="15sp",
            color=TEXT_PRIMARY,
        )
        ana.add_widget(ust_baslik)

        yol_input = TextInput(
            text="",
            multiline=False,
            readonly=True,
            size_hint_y=None,
            height=dp(44),
            background_normal="",
            background_active="",
            background_color=INPUT_BG,
            foreground_color=TEXT_PRIMARY,
            cursor_color=TEXT_PRIMARY,
            padding=(dp(10), dp(12)),
            font_size="13sp",
        )
        ana.add_widget(yol_input)

        bilgi_lbl = Label(
            text=".py dosyaları listelenir",
            size_hint_y=None,
            height=dp(18),
            color=TEXT_MUTED,
            font_size="12sp",
            halign="left",
            valign="middle",
        )
        bilgi_lbl.bind(
            size=lambda inst, size: setattr(inst, "text_size", (size[0], None))
        )
        ana.add_widget(bilgi_lbl)

        ust_bar, geri_btn, ana_depo_btn, yenile_btn, kapat_btn = self._build_popup_toolbar()
        ana.add_widget(ust_bar)

        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8),
            scroll_type=["bars", "content"],
        )

        liste = GridLayout(
            cols=1,
            spacing=dp(6),
            padding=(0, dp(4)),
            size_hint_y=None,
        )
        liste.bind(minimum_height=liste.setter("height"))

        scroll.add_widget(liste)
        ana.add_widget(scroll)

        popup = Popup(
            title="",
            content=ana,
            size_hint=(0.96, 0.96),
            auto_dismiss=False,
            separator_height=0,
        )

        def _popup_kapaninca(*_args):
            self.popup = None

        popup.bind(on_dismiss=_popup_kapaninca)
        self.popup = popup

        def yol_yaz():
            yol_input.text = "Geçerli klasör: " + str(mevcut_klasor)

        def listeyi_yenile(*_args):
            liste.clear_widgets()
            yol_yaz()

            try:
                klasorler = []
                dosyalar = []

                for oge in sorted(
                    mevcut_klasor.iterdir(),
                    key=lambda p: (not p.is_dir(), p.name.lower()),
                ):
                    if oge.is_dir():
                        klasorler.append(oge)
                    elif oge.is_file() and oge.suffix.lower() == ".py":
                        dosyalar.append(oge)

                for klasor in klasorler:
                    self._popup_satiri_ekle(
                        liste,
                        "[KLASOR]  " + klasor.name,
                        lambda _btn, p=klasor: klasore_gir(p),
                        CARD_BG,
                    )

                for dosya in dosyalar:
                    self._popup_satiri_ekle(
                        liste,
                        "[PY]  " + dosya.name,
                        lambda _btn, p=dosya: dosya_sec(p),
                        CARD_BG_SOFT,
                    )

                if not klasorler and not dosyalar:
                    self._popup_satiri_ekle(
                        liste,
                        "Bu klasörde Python dosyası yok.",
                        lambda *_: None,
                        CARD_BG_DARK,
                    )

            except Exception as exc:
                self._popup_satiri_ekle(
                    liste,
                    "[Hata] " + str(exc),
                    lambda *_: None,
                    (0.30, 0.15, 0.15, 1),
                )

            try:
                scroll.scroll_y = 1
            except Exception:
                pass

        def klasore_gir(klasor: Path):
            nonlocal mevcut_klasor
            try:
                if klasor.exists() and klasor.is_dir():
                    mevcut_klasor = klasor.resolve()
                    listeyi_yenile()
            except Exception:
                pass

        def dosya_sec(dosya: Path):
            try:
                secili = str(dosya.resolve())
                self._debug(f"Masaüstü dosyası seçildi: {secili}")
                popup.dismiss()
                self._after_file_selected(secili)
            except Exception as exc:
                self._debug(f"Masaüstü dosya seçim hatası: {exc}")

        def yukari_cik(*_args):
            nonlocal mevcut_klasor
            try:
                mevcut = mevcut_klasor.resolve()

                if str(mevcut) == str(alt_sinir):
                    return

                ust = mevcut.parent
                if ust.exists() and ust.is_dir():
                    mevcut_klasor = ust.resolve()
                    listeyi_yenile()
            except Exception:
                pass

        def ana_depoya_don(*_args):
            nonlocal mevcut_klasor
            try:
                mevcut_klasor = _varsayilan_baslangic_klasoru()
                listeyi_yenile()
            except Exception:
                pass

        def kapat_popup(*_args):
            try:
                popup.dismiss()
            except Exception:
                self.popup = None

        geri_btn.bind(on_release=yukari_cik)
        ana_depo_btn.bind(on_release=ana_depoya_don)
        yenile_btn.bind(on_release=listeyi_yenile)
        kapat_btn.bind(on_release=kapat_popup)

        listeyi_yenile()
        popup.open()

    # =========================================================
    # INFO POPUP
    # =========================================================
    def _show_info_popup(self, title: str, message: str):
        self._debug(f"POPUP -> {title}: {message}")

        icerik = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(12),
        )

        lbl = Label(
            text=message,
            color=TEXT_PRIMARY,
            halign="left",
            valign="middle",
        )
        lbl.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        icerik.add_widget(lbl)

        btn = Button(
            text="Tamam",
            size_hint_y=None,
            height=dp(42),
            background_normal="",
            background_down="",
            background_color=(0.20, 0.20, 0.24, 1),
            color=TEXT_PRIMARY,
        )

        popup = Popup(
            title=title,
            content=icerik,
            size_hint=(0.86, 0.36),
            auto_dismiss=False,
        )

        btn.bind(on_release=lambda *_: popup.dismiss())
        icerik.add_widget(btn)
        popup.open()
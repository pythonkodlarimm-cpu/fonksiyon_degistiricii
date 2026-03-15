# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/android_tree_picker.py

ROL:
- Android'de klasör seçme ve klasör içi .py dosyalarını gösterme akışı
- ACTION_OPEN_DOCUMENT_TREE ile klasör URI alır
- DocumentFile ile gezinir
- Seçilen dosyayı cache'e kopyalayıp üst katmana bildirir

SURUM: 2
TARIH: 2026-03-15
IMZA: FY.
"""

from __future__ import annotations

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from app.ui.dosya_secici_paketi.android_tree_repo import AndroidTreeRepo
from app.ui.dosya_secici_paketi.info_popup import show_info_popup
from app.ui.dosya_secici_paketi.models import PickerSelection
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


class _SatirKart(BoxLayout):
    def __init__(self, bg=(0.16, 0.16, 0.18, 1), radius=14, **kwargs):
        super().__init__(**kwargs)
        from kivy.graphics import Color, RoundedRectangle

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


class AndroidTreePicker:
    ANDROID_TREE_REQUEST_CODE = 12092

    def __init__(self, owner, on_selected):
        self.owner = owner
        self.on_selected = on_selected
        self.repo = AndroidTreeRepo(owner=owner)

        self._result_bound = False
        self._picker_open = False
        self._last_temp_file = ""

        self._root_doc = None
        self._current_doc = None
        self._doc_stack = []

        self._browser_popup = None

        self._bind_activity_result()

    # ---------------------------------------------------------
    # debug
    # ---------------------------------------------------------
    def _debug(self, message: str) -> None:
        try:
            self.owner._debug(f"[TREE] {message}")
        except Exception:
            try:
                print("[ANDROID_TREE_PICKER]", str(message))
            except Exception:
                pass

    # ---------------------------------------------------------
    # bind
    # ---------------------------------------------------------
    def _bind_activity_result(self):
        try:
            from android import activity  # type: ignore

            if not self._result_bound:
                activity.bind(on_activity_result=self._on_activity_result)
                self._result_bound = True
                self._debug("activity result bind edildi")
        except Exception as exc:
            self._debug(f"bind hatası: {exc}")

    # ---------------------------------------------------------
    # open tree
    # ---------------------------------------------------------
    def open_tree_picker(self):
        self._picker_open = True
        self._debug("ACTION_OPEN_DOCUMENT_TREE açılıyor")

        try:
            from jnius import autoclass, cast  # type: ignore

            Intent = autoclass("android.content.Intent")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")

            current_activity = cast("android.app.Activity", PythonActivity.mActivity)

            intent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE)
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            intent.addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)

            current_activity.startActivityForResult(
                intent,
                self.ANDROID_TREE_REQUEST_CODE,
            )

            Clock.schedule_once(self._force_picker_reset, 12)

        except Exception as exc:
            self._picker_open = False
            show_info_popup(
                owner=self.owner,
                title="Klasör Seçici Hatası",
                message=f"Klasör seçici açılamadı:\n{exc}",
            )

    def _force_picker_reset(self, *_args):
        self._picker_open = False
        self._debug("force reset çalıştı")

    # ---------------------------------------------------------
    # activity result
    # ---------------------------------------------------------
    def _on_activity_result(self, request_code, result_code, intent):
        self._debug(f"activity result geldi | request={request_code} result={result_code}")

        if request_code != self.ANDROID_TREE_REQUEST_CODE:
            self._debug("request code eşleşmedi, çıkılıyor")
            return

        self._picker_open = False

        try:
            from jnius import autoclass

            Activity = autoclass("android.app.Activity")

            if result_code != Activity.RESULT_OK:
                self._debug("klasör seçimi iptal edildi veya başarısız")
                return

            if intent is None:
                show_info_popup(
                    owner=self.owner,
                    title="Klasör Seçici",
                    message="Klasör seçimi tamamlanmadı.",
                )
                return

            tree_uri = intent.getData()
            self._debug(f"tree uri: {tree_uri}")

            if tree_uri is None:
                show_info_popup(
                    owner=self.owner,
                    title="Klasör Seçici",
                    message="Klasör seçilemedi.",
                )
                return

            self.repo.take_persistable_permission(intent, tree_uri)

            root_doc = self.repo.get_root_doc(tree_uri)
            self._debug(f"root_doc: {root_doc}")

            if root_doc is None:
                show_info_popup(
                    owner=self.owner,
                    title="Klasör Seçici",
                    message="Seçilen klasör açılamadı.",
                )
                return

            try:
                root_exists = bool(root_doc.exists())
            except Exception:
                root_exists = False

            try:
                root_is_dir = bool(root_doc.isDirectory())
            except Exception:
                root_is_dir = False

            self._debug(f"root exists={root_exists} is_dir={root_is_dir}")

            if not root_exists or not root_is_dir:
                show_info_popup(
                    owner=self.owner,
                    title="Klasör Seçici",
                    message="Seçilen klasör geçerli görünmüyor.",
                )
                return

            self._root_doc = root_doc
            self._current_doc = root_doc
            self._doc_stack = [root_doc]

            self._debug("browser popup açılıyor")
            self._open_browser_popup()

        except Exception as exc:
            self._debug(f"activity result işleme hatası: {exc}")
            show_info_popup(
                owner=self.owner,
                title="Klasör Seçici Hatası",
                message=f"Seçilen klasör işlenemedi:\n{exc}",
            )

    # ---------------------------------------------------------
    # browser ui
    # ---------------------------------------------------------
    def _build_toolbar(self):
        toolbar = IconToolbar(
            spacing_dp=14,
            padding_dp=0,
        )

        geri_btn = toolbar.add_tool(
            icon_name="arrow_back_geri.png",
            text="Geri",
            on_release=lambda *_: None,
            icon_size_dp=32,
            text_size="10sp",
            color=TEXT_MUTED,
            icon_bg=None,
        )

        kok_btn = toolbar.add_tool(
            icon_name="folder_open.png",
            text="Kök",
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

        return toolbar, geri_btn, kok_btn, yenile_btn, kapat_btn

    def _satir_ekle(self, liste, text, callback, renk):
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

    def _current_path_text(self) -> str:
        try:
            names = []
            for doc in self._doc_stack:
                name = str(doc.getName() or "").strip()
                if name:
                    names.append(name)

            if names:
                return "/".join(names)

            return "Seçilen Klasör"
        except Exception:
            return "Seçilen Klasör"

    def _open_browser_popup(self):
        if self._browser_popup:
            try:
                self._browser_popup.dismiss()
            except Exception:
                pass
            self._browser_popup = None

        ana = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(8),
        )

        ust_baslik = IconluBaslik(
            text="Klasörden Python Dosyası Seç",
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
            text="Klasörler ve .py dosyaları listelenir. Gerekirse diğer dosyalar da gösterilir.",
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

        ust_bar, geri_btn, kok_btn, yenile_btn, kapat_btn = self._build_toolbar()
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
            self._browser_popup = None

        popup.bind(on_dismiss=_popup_kapaninca)
        self._browser_popup = popup

        def yol_yaz():
            yol_input.text = "Geçerli klasör: " + self._current_path_text()

        def listeyi_yenile(*_args):
            liste.clear_widgets()
            yol_yaz()

            try:
                items = self.repo.list_children(self._current_doc)
                self._debug(f"listelenen öğe sayısı: {len(items)}")

                if not items:
                    self._satir_ekle(
                        liste,
                        "Bu klasörde gösterilebilir öğe yok.",
                        lambda *_: None,
                        CARD_BG_DARK,
                    )
                else:
                    for item in items:
                        if item["is_dir"]:
                            self._satir_ekle(
                                liste,
                                "[KLASOR]  " + item["name"],
                                lambda _btn, current=item: klasore_gir(current),
                                CARD_BG,
                            )
                        elif item["name"].lower().endswith(".py"):
                            self._satir_ekle(
                                liste,
                                "[PY]  " + item["name"],
                                lambda _btn, current=item: dosya_sec(current),
                                CARD_BG_SOFT,
                            )
                        else:
                            self._satir_ekle(
                                liste,
                                "[DOSYA]  " + item["name"],
                                lambda _btn, current=item: dosya_sec(current),
                                CARD_BG_DARK,
                            )

                try:
                    scroll.scroll_y = 1
                except Exception:
                    pass

            except Exception as exc:
                self._debug(f"listeleme hatası: {exc}")
                self._satir_ekle(
                    liste,
                    "[Hata] " + str(exc),
                    lambda *_: None,
                    (0.30, 0.15, 0.15, 1),
                )

        def klasore_gir(item):
            try:
                doc = item["doc"]
                self._current_doc = doc
                self._doc_stack.append(doc)
                self._debug(f"Klasöre girildi: {item['name']}")
                listeyi_yenile()
            except Exception as exc:
                self._debug(f"Klasöre giriş hatası: {exc}")

        def dosya_sec(item):
            try:
                doc = item["doc"]
                temp_path = self.repo.materialize_file(
                    file_doc=doc,
                    previous_temp_file=self._last_temp_file,
                )

                self._debug(f"Temp path: {temp_path}")

                if not temp_path:
                    show_info_popup(
                        owner=self.owner,
                        title="Dosya Seçici",
                        message="Seçilen dosya uygulama alanına kopyalanamadı.",
                    )
                    return

                self._last_temp_file = temp_path

                popup.dismiss()
                self.on_selected(
                    PickerSelection(
                        path=temp_path,
                        uri=item["uri"],
                        display_name=item["name"],
                        source="android_tree",
                    )
                )
            except Exception as exc:
                self._debug(f"Dosya seçim hatası: {exc}")
                show_info_popup(
                    owner=self.owner,
                    title="Dosya Seçici",
                    message=f"Dosya seçilemedi:\n{exc}",
                )

        def geri(*_args):
            try:
                if len(self._doc_stack) <= 1:
                    return

                self._doc_stack.pop()
                self._current_doc = self._doc_stack[-1]
                self._debug("Bir üst klasöre çıkıldı")
                listeyi_yenile()
            except Exception as exc:
                self._debug(f"Geri hatası: {exc}")

        def koka_don(*_args):
            try:
                if self._root_doc is None:
                    return

                self._current_doc = self._root_doc
                self._doc_stack = [self._root_doc]
                self._debug("Tree köküne dönüldü")
                listeyi_yenile()
            except Exception as exc:
                self._debug(f"Köke dönme hatası: {exc}")

        def kapat(*_args):
            try:
                popup.dismiss()
            except Exception:
                self._browser_popup = None

        geri_btn.bind(on_release=geri)
        kok_btn.bind(on_release=koka_don)
        yenile_btn.bind(on_release=listeyi_yenile)
        kapat_btn.bind(on_release=kapat)

        listeyi_yenile()
        popup.open()
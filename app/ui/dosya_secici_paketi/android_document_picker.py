# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/dosya_secici_paketi/android_document_picker.py

ROL:
- Android gerçek sistem dosya seçicisini açar
- Seçilen dosyayı URI olarak alır
- Yalnızca sade DocumentSelection üretir

NOT:
- Bu dosya sadece seçim yapar
- İçe aktarma, tarama, yedekleme burada yapılmaz
"""

from __future__ import annotations

from kivy.utils import platform

from app.ui.dosya_secici_paketi.models import DocumentSelection


class AndroidDocumentPicker:
    ANDROID_REQUEST_CODE = 10240

    def __init__(self, owner, on_selected):
        self.owner = owner
        self.on_selected = on_selected
        self._is_bound = False
        self._bind_activity_result()

    def _debug(self, msg: str) -> None:
        try:
            self.owner._debug(f"[ANDROID_PICKER] {msg}")
        except Exception:
            try:
                print("[ANDROID_PICKER]", str(msg))
            except Exception:
                pass

    def _bind_activity_result(self) -> None:
        if platform != "android":
            return

        if self._is_bound:
            return

        try:
            from android import activity  # type: ignore

            activity.bind(on_activity_result=self._on_activity_result)
            self._is_bound = True
            self._debug("activity result bind edildi")
        except Exception as exc:
            self._debug(f"bind hatası: {exc}")

    def open_picker(self) -> None:
        if platform != "android":
            self._debug("Android değil")
            return

        try:
            from jnius import autoclass, cast  # type: ignore

            Intent = autoclass("android.content.Intent")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")

            current_activity = cast("android.app.Activity", PythonActivity.mActivity)

            intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            intent.setType("*/*")

            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            intent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
            intent.addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)

            current_activity.startActivityForResult(intent, self.ANDROID_REQUEST_CODE)
            self._debug("picker açıldı")

        except Exception as exc:
            self._debug(f"picker açma hatası: {exc}")

    def _on_activity_result(self, request_code, result_code, intent) -> None:
        if request_code != self.ANDROID_REQUEST_CODE:
            return

        try:
            from jnius import autoclass

            Activity = autoclass("android.app.Activity")

            if result_code != Activity.RESULT_OK:
                self._debug("seçim iptal edildi")
                return

            if intent is None:
                self._debug("intent boş")
                return

            uri = intent.getData()
            if uri is None:
                self._debug("uri boş")
                return

            uri_str = str(uri.toString() or "").strip()
            if not uri_str:
                self._debug("uri string boş")
                return

            display_name = ""
            mime_type = ""

            try:
                from app.services.android_uri_servisi import (
                    get_display_name,
                    get_mime_type,
                    take_persistable_permission,
                )

                try:
                    take_persistable_permission(intent, uri_str)
                except Exception as exc:
                    self._debug(f"persistable izin alınamadı: {exc}")

                try:
                    display_name = str(get_display_name(uri_str) or "").strip()
                except Exception as exc:
                    self._debug(f"display name alınamadı: {exc}")

                try:
                    mime_type = str(get_mime_type(uri_str) or "").strip()
                except Exception as exc:
                    self._debug(f"mime type alınamadı: {exc}")

            except Exception as exc:
                self._debug(f"android_uri_servisi kullanılamadı: {exc}")

            secim = DocumentSelection(
                source="android_document",
                uri=uri_str,
                local_path="",
                display_name=display_name,
                mime_type=mime_type,
            )

            self._debug(
                f"seçim tamam | uri={uri_str} | display={display_name} | mime={mime_type}"
            )

            if self.on_selected:
                self.on_selected(secim)

        except Exception as exc:
            self._debug(f"activity result hatası: {exc}")